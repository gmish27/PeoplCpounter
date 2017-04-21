import cv2
from PIL import Image
import imagehash as imsh
from storage import storage
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import datetime
from imutils.video import FPS
from pistream import pistream

"""
resolution = (400,320)
camera = PiCamera()
camera.resolution = resolution
camera.framerate = 24
camera.shutter_speed = 30000
time.sleep(1)
camera.start_preview()
camera.awb_mode = 'off'
camera.awb_gains = (1.9, 0.8)
camera.exposure_mode = 'off'
time.sleep(10)
#camera.shutter_speed = 90 #shutter_speed should be 2x framerate
#camera.framerate = (5*10**3)/(camera.shutter_speed)

rawCapture = PiRGBArray(camera, size=resolution)

time.sleep(0.1)
"""

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

s = storage(2, 2, 20)#min_hit time_out threshold
firstFrame = None
min_area = 5000
fps = FPS().start()
no_of_frames = 0
vs = pistream().start()
time.sleep(5)

def capface(im):
	t=datetime.datetime.now();
	im.save('FACES/faceio'+str(t)+'.jpg','JPEG')
	print "\nflag is reset"
	return 0

while True:
	frame = vs.read()
	facesTimedOut = s.faceTimedOut()
	#print s.numFaces()
	if len(facesTimedOut) > 0:
		indexAdjust = 0
		for index in facesTimedOut:
			[pImg, pHash] = s.popFace(index - indexAdjust)[0]
			indexAdjust  += 1
			capface(pImg)

	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	#r = 100.0/gray.shape[1]
	#dim = (100, int(gray.shape[0] * r))
	#gray_resized = cv2.resize(gray, dim, interpolation = cv2.INTER_AREA)
	gray_resized = gray
	frame = gray_resized
	gray = cv2.GaussianBlur(gray_resized, (21, 21), 0)
	
	if firstFrame is None:
		print "[INFO] starting background model..."
		firstFrame = gray.copy().astype("float")
		firstFrame = gray
		continue
	
	#cv2.accumulateWeighted(gray, firstFrame, 0.5)
	frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(firstFrame))
	
	thresh = cv2.threshold(frameDelta, 5, 255, cv2.THRESH_BINARY)[1]
	thresh = cv2.dilate(thresh, None, iterations=2)
	cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]

	for c in cnts:
		if cv2.contourArea(c) < min_area:
			continue
		(cx, cy, cw, ch) = cv2.boundingRect(c)
		img = gray_resized[cy:cy+ch, cx:cx+cw]
		faces = face_cascade.detectMultiScale(gray_resized, 1.3, 5)
		for (x,y,w,h) in faces:
			roi_gray = img[y:y+h, x:x+w]
			cv2.rectangle(frame,(x+cx,y+cy),(x+cx+w,y+cy+h),(255,0),2)
			im = Image.fromarray(roi_gray)
			img_hash = imsh.whash(im)
			s.addFace([im, img_hash])
	#print 'working'
	fps.update()
	if no_of_frames is 100:
		fps.stop()
		print 'approx. FPS: '+ str(fps.fps())
		no_of_frames = 0
	else:
		no_of_frames += 1 
	cv2.imshow('img',frame)
	#cv2.imshow('delta',frameDelta)
	k = cv2.waitKey(10) & 0xff
	if k == 27: #press ESC to exit
		break

cv2.destroyAllWindows()
vs.stop()


