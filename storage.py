import time

class storage:
	### timeout is in sec
	timeout = 0
	store   = []
	thresh  = 0
	minHit  = 0

	def __init__( self, minHit, timeout, thresh ):
		self.timeout = timeout
		self.store   = []
		self.thresh  = thresh
		self.minHit  = minHit

	def compareHash( self, hash1, hash2 ):
		return abs( hash1 - hash2 ) < self.thresh
	
	def addFace( self, face ):
		## face, currTime
		found = False
		[ img, hash ] = face
		for elem in self.store:
			[ refImg, refHash ] = elem[ 0 ]
			elem[2] += 1
			if self.compareHash( refHash, hash ):
				elem[1] = int( time.time() )
				print img.size, refImg.size
				if img.size[0] > refImg.size[0]:
					elem[0][0] = img
				found = True
				break
		if not found:
			print 'adding'
			#self.store.append( [ face, int(time.time()), 1 ] )

	def popFace( self, index ):
		faceTime = self.store[ index ]
		del self.store[ index ]
		return faceTime

	def faceTimedOut( self ):
		index   = 0
		indexes = []
		for [ face, pushTime, hits ] in self.store:
			if int( time.time() ) - pushTime > self.timeout:
				if hits > self.minHit:
					indexes.append( index )
				else:
					self.popFace( index )
					index -= 1
			index += 1
		return indexes

	def numFaces( self ):
		return len( self.store )

	def findFace( self, face ):
		index      = 0
		foundIndex = None
		for [ sFace, sTime ] in self.store:
			## TODO: relace with xcorr2 or imagehash
			
			if sFace == face:
				foundIndex = index
				break

			index += 1
		return foundIndex
