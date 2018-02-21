# Untuk penysipan pesan pada gambar berformat bmp dan png yang tidak terkompresi
# gambar memiliki warna 1 byte atau 3 byte
import time
import binascii
import io
import sys
import os
import extended_vigenere as cipher
from PIL import Image
from ImageComparer import ImageComparer

import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
# import readline
# readline.parse_and_bind("tab: complete")
global chessBoard, maxChange
chessBoard = [i % 2 for i in xrange(64)]
maxChange = 112

class BPCS :

	def __init__(self, imagePath, filename):
		self.imagePath = imagePath
		self.image = Image.open(self.imagePath)
		self.mode = self.image.mode
		self.blocks = []
		self.bitPlanes = [] # array of pixel, pixel = array of bitplane, bitplane = array of int (0,1)
		self.pbcBitplanes = []
		self.fileMsgName = filename
		self.numberOfMsgPlane = 0
		self.msgBlocks = []
		self.notAllowed = []
		self.conjugateTable = []
		self.msgLen = 0
		self.threshold = 0.3

	# def convertPBC2CGC(self):
	# 	self.pbc = self.image.load()
	# 	width = self.image.size[0]
	# 	height = self.image.size[1]
	# 	image = self.create_image(width, height)
	# 	px = image.load()
	# 	i = 0
	# 	while i<height :
	# 		j = 0
	# 		while j < width:
	# 			if j % width == 0:
	# 				px[i, j] = self.pbc[i, j]
	# 			else:
	# 				if isinstance(self.pbc[i, j], int):
	# 					px[i, j] = self.pbc[i, j] ^ self.pbc[i, j-1]
	# 				else:
	# 					tup = []
	# 					k = 0
	# 					while k < 3:
	# 						res = self.pbc[i, j][k] ^ self.pbc[i, j-1][k]
	# 						tup.append(res)
	# 						k+=1
	# 					px[i, j] = tuple(tup)
	# 			j+=1
	# 		i+=1

	# 	return image

	# def convertCGC2PBC(self):
	# 	self.pbc = self.image.load()
	# 	width = self.image.size[0]
	# 	height = self.image.size[1]
	# 	image = self.create_image(width, height)
	# 	px = image.load()
	# 	i = 0
	# 	while i<height :
	# 		j = 0
	# 		while j < width:
	# 			if j % width == 0:
	# 				px[i, j] = self.pbc[i, j]
	# 			else:
	# 				if isinstance(self.pbc[i, j], int):
	# 					px[i, j] = self.pbc[i, j] ^ px[i, j-1]
	# 				else:
	# 					tup = []
	# 					k = 0
	# 					while k < 3:
	# 						res = self.pbc[i, j][k] ^ px[i, j-1][k]
	# 						tup.append(res)
	# 						k+=1
	# 					px[i, j] = tuple(tup)
	# 			j+=1
	# 		i+=1

	# 	return image

	# def convertCGC2PBC(self, image):
	# 	px = image.load()
	# 	width = self.image.size[0]
	# 	height = self.image.size[1]
	# 	i = 0
	# 	while i<height :
	# 		j = 0
	# 		while j < width:
	# 			if j % width == 0:
	# 				px[i, j] = self.pbc[i, j]
	# 			else:
	# 				if isinstance(px[i, j], int):
	# 					px[i, j] = px[i, j] ^ self.pbc[i, j-1]
	# 				else:
	# 					tup = []
	# 					k = 0
	# 					while k < 3:
	# 						res = px[i, j][k] ^ self.pbc[i, j-1][k]
	# 						tup.append(res)
	# 						k+=1
	# 					px[i, j] = tuple(tup)
	# 			j+=1
	# 		i+=1

	def convertPBC2CGC(self, bitplanes):
		self.pbcBitplanes.append(bitplanes)
		i = 0
		while i < len(bitplanes): # 1 for greyscale, 3 for rgb
			j = 0
			while j < len(bitplanes[i][j]):
				if j == 0:
					bitplanes[i][j] = bitplanes[i][j]
					bitplanes[i][j]['complexity'] = self.calculateComplexity(bitplanes[i][j]['bitplane'])
				else:
					k = 0
					while k < 64:
						bitplanes[i][j]['bitplane'][k] = bitplanes[i][j]['bitplane'][k] ^ bitplanes[i][j-1]['bitplane'][k] 
						k+=1

					bitplanes[i][j]['complexity'] = self.calculateComplexity(bitplanes[i][j]['bitplane'])
				j+=1
			i+=1

	def convertCGC2PBC(self, cgcbitplanes, pbcbitplanes):
		i = 0
		while i < len(cgcbitplanes): # 1 for greyscale, 3 for rgb
			j = 0
			while j < len(cgcbitplanes[i][j]):
				if j == 0:
					cgcbitplanes[i][j] = cgcbitplanes[i][j]
				else:
					k = 0
					while k < 64:
						cgcbitplanes[i][j]['bitplane'][k] = cgcbitplanes[i][j]['bitplane'][k] ^ pbcbitplanes[i][j-1]['bitplane'][k] 
						k+=1
				j+=1
			i+=1

	def defineBlockSize(self):
		self.width, self.height = self.image.size
		return (self.width / 8 + int(self.width % 8 > 0)) * (self.height / 8 + int(self.height % 8 > 0)) 

	def definePixelBoundary(self):
		# tentukan batas pixel
		if self.width % 8 == 0: # pixel kelipatan 8
			col = self.width + 1
		else: # pixel bukan kelipatan 8
			col = self.width + (8 - self.width % 8) + 1

		if self.height % 8 == 0:
			row = self.height + 1
		else:
			row = self.height + (8 - self.height % 8) + 1

		return col, row


	def initializeBlock(self, blocksize):
		# buat tempatnya bloknya dulu
		i = 0
		blocks = []
		while i < blocksize :
			blocks.append([])
			i+=1
		return blocks

	def dividePixels(self):
		#jumlah blok
		blockSize = self.defineBlockSize()
		# image = self.convertPBC2CGC()

		image = self.image
		self.blocks = self.initializeBlock(blockSize)

		i = 1
		idx = 0
		limit = 0
		col, row = self.definePixelBoundary()

		px = image.load() # load pixel dari gambar
		while i < col:
			bits = []
			j = 1
			while j < row:

				if j < self.height + 1 and i < self.width + 1: # iterasi masih kurang dari jumlah pixel
					if self.mode == 'L': # gambar grayscale
						bits.append([bin(px[i-1, j-1])[2:].zfill(8)])

					else: # gambar berwarna
						bits.append([bin(x)[2:].zfill(8) for x in px[i-1,j-1]])
				else:
					exc =  bin(255)[2:].zfill(8)
					bits.append((exc, exc, exc)) 
					if idx not in self.notAllowed:
						self.notAllowed.append(idx)

				if j % 8 == 0 or (j > self.height and len(bits) == 8):

					self.blocks[idx].extend(bits)
					idx += 1
					bits = []

				j+=1

			if i % 8 == 0: 
				limit = idx

			idx = limit
			i+=1

	def calculateComplexity(self, bitplane):
		i = 0
		change = 0
		while i < len(bitplane):
			if i < 55 and i % 8 != 0:
				change += abs(bitplane[i]-bitplane[i-1])+abs(bitplane[i]-bitplane[i+8])
			elif i % 8 == 0 and i < 55:
				change += abs(bitplane[i]-bitplane[i+8])
			elif i > 55:
				change += abs(bitplane[i]-bitplane[i-1])
			i+=1

		return float(change)/float(maxChange)

	def createBitplanes(self): 

		for block in self.blocks:
			i = 0
			colorLen = len(block[0])
			bitplaneForAllColor = []

			while i < colorLen: # 3 for rgb, 1 for grayscale
				j = 0
				bitplaneForEachColor = []
				while j < 8: # 8 bit dari setiap warna pada rgb
					k = 0

					bits = []
					while k < 64: # 64 jumlah kelompok warna
						bits.append(int(block[k][i][j]))
						k += 1
					j += 1

					bitplane = {'bitplane':bits, 'complexity':self.calculateComplexity(bits)}
					bitplaneForEachColor.append(bitplane)

				bitplaneForAllColor.append(bitplaneForEachColor)
			
				i+=1
			if self.cgc:
				self.convertPBC2CGC(bitplaneForAllColor)
			self.bitPlanes.append(bitplaneForAllColor)
			

	def setStegoKey(self, key):
		self.key = key

	def encryptMsg(self):
		if len(self.key) == 0:
			self.message = cipher.encrypt(self.message, 'a')
		else:
			self.message = cipher.encrypt(self.message, self.key)

	def decryptMsg(self):
		if len(self.key) == 0:
			self.message = cipher.decrypt(self.message, 'a')
		else:
			self.message = cipher.decrypt(self.message, self.key)

	def defineMsgLen(self):
		if self.msglen % 8 == 0:
			return self.msglen
		else:
			return self.msglen + (8 - self.msglen % 8) + 1

	def readMsg(self):
		self.msgLen = os.stat(self.fileMsgName).st_size
		numberOfBit =  self.msgLen*8
		modular64OfNumber = numberOfBit%64
		if(modular64OfNumber == 0):
			self.numberOfMsgPlane = self.msgLen/8
		else:
			self.numberOfMsgPlane = self.msgLen/8+1
		file = open(self.fileMsgName, 'r')
		self.message = file.read()
		file.close()

	def divideMessage(self):

		blockSize = len(self.message) / 8 + int(len(self.message) % 8 > 0)
		self.msgBlocks = self.initializeBlock(blockSize)
		self.msglen = len(self.message)
		length = self.defineMsgLen()

		i = 1
		idx = 0
		while i < length:
			if i < len(self.message) + 1:
				self.msgBlocks[idx].append(bin(ord(self.message[i-1]))[2:].zfill(8))
			else:
				self.msgBlocks[idx].append(bin(ord(' '))[2:].zfill(8))
			if i % 8 == 0:
				idx+=1
			i+=1

	def conjugateBitplane(self, bitplane):
		i = 0
		while i < len(bitplane):
			bitplane[i] ^= chessBoard[i]
			i+=1
		return bitplane

	#Untuk nama file (Ascii 16 bit)
	def intToBitplane(self,number):
		bitplane = []
		t = {'0':[0,0,0],'1':[0,0,1],'2':[0,1,0],'3':[0,1,1],'4':[1,0,0],'5':[1,0,1] ,'6':[1,1,0],'7':[1,1,1]}
		for c in oct(int(number))[1:]:
			bitplane+=t[c]
		remainder = 16 - len(bitplane)%16
		if (remainder != 16):
			for i in range(remainder):
				bitplane = [0]+bitplane
		return bitplane
	
	#Untuk ukuran file (batas maksimal 64 bit)
	def intToBitplaneExpanded(self,number):
		bitplane = []
		t = {'0':[0,0,0],'1':[0,0,1],'2':[0,1,0],'3':[0,1,1],'4':[1,0,0],'5':[1,0,1] ,'6':[1,1,0],'7':[1,1,1]}
		for c in oct(int(number))[1:]:
			bitplane+=t[c]
		remainder = 64 - len(bitplane)%64
		if (remainder != 64):
			for i in range(remainder):
				bitplane = [0]+bitplane
		return bitplane

	def bitplaneToInt(self, bitplane):
		stringOfBit = ''
		for bit in bitplane:
			stringOfBit += str(bit)
		return int(stringOfBit,2)

	def stringToBitplanes(self, string):
		bitplanes = []
		bitplane = []
		bitplane += self.intToBitplane(len(string))
		length = 1
		for char in string:
			bitplane += self.intToBitplane(ord(char))
			length+=1
			if(length == 4):
				bitplanes.append(bitplane)
				bitplane=[]
				length=0
		if(length != 0):
			for i in range((4-length)*16):
				bitplane.append(0)
			bitplanes.append(bitplane)
		return bitplanes

	def bitplanesToString(self, bitplanes):
		string = ''
		char = ''
		length = 0
		bitOfChar = ''
		lengthOfString = 0
		for bitplane in bitplanes:
			for bit in bitplane:
				bitOfChar += str(bit)
				length += 1
				if(length == 16):
					if(lengthOfString==0):
						lengthOfString = int(bitOfChar,2)
						bitOfChar = ''
						length = 0
					else :
						char = chr(int(bitOfChar,2))
						string += char
						char = ''
						bitOfChar = ''
						length = 0
						if(len(string)==lengthOfString):
							break
			if(len(string)==lengthOfString):
				break
		return string
	
	def createMsgBitplane(self):
		self.msgBitplanes = []

		for block in self.msgBlocks:
			i = 0
			bitplanebits = []
			for bits in block:
				for bit in bits:
					bitplanebits.append(int(bit))
			bitplane = {'bitplane':bitplanebits, 'complexity':self.calculateComplexity(bitplanebits)}
			self.msgBitplanes.append(bitplane)

	def seed(self):
		sumC = 0
		for c in self.key:
			sumC += cipher.extended_ascii.index(c)

		if sumC % 2 == 0:
			return True
		return False
		# if self.random:
		# 	if len(self.key) == 0:
		# 		return cipher.extended_ascii.index('a') % 10
		# 	return cipher.extended_ascii.index(self.key[idx]) % 10
		# else:
		# 	return 1

	def embedding(self):
		# pass
		msgBitplaneIdx = 0
		isEven = self.seed()

		if isEven:
			idx = 0
		else:
			idx = 1

		keyLen = len(self.key)
		keyIdx = 0
		replaced = []
		bitplaneLen = len(self.bitPlanes)
		msgBitplaneLen = len(self.msgBitplanes)
		hasInsertmsgBitplaneLen = False
		hasInsertNameMsgBitplanesLen = False
		hasInsertNameMsg = False
		hasInsertMsg = False
		hasInsertConjugateTable = False
		hasInsertConjugateBitplaneLen = False
		hasInsertConjugateConjugateTableTable = False
		nameMsgBitplanes = self.stringToBitplanes(self.fileMsgName)
		nameMsgBitplanesLen = len(nameMsgBitplanes)
		nameMsgBitplaneIdx = 0
		conjugateBitplaneIdx = 0
		conjugateBitplaneNeeded = 0
		conjugateTableTemp = []
		conjugateBitplaneLen = 0
		conjugateConjugateTableTable = []
		conjugateConjugateTableTableIdx = 0
		arrayOfPosition = []
		for i in range(1 + 1 + 1 + nameMsgBitplanesLen + msgBitplaneLen):
			self.appendConjugateTableFunction(conjugateTableTemp,0)
		self.makeFinalConjugateTableFunction(conjugateTableTemp)
		conjugateBitplaneLen = len(conjugateTableTemp)
		isReturn = False

		while idx < bitplaneLen:
			if idx not in self.notAllowed and idx not in replaced:
				jdx=0
				for bitplanes in self.bitPlanes[idx]: # 1 for grayscale, 3 for rgb
					i = 0
					while i < len(bitplanes): 
						
						if bitplanes[i]['complexity'] > self.threshold :
							if not hasInsertmsgBitplaneLen :
								bitplanes[i]['bitplane'] = self.intToBitplaneExpanded(self.msgLen)
								if(self.calculateComplexity(bitplanes[i]['bitplane']) < self.threshold):
									bitplanes[i]['bitplane'] = self.conjugateBitplane(bitplanes[i]['bitplane'])
									self.appendConjugateTable(1)
								else:
									self.appendConjugateTable(0)
								print("hasInsertmsgBitplaneLen",msgBitplaneLen)
								hasInsertmsgBitplaneLen = True
								arrayOfPosition.append([idx,jdx,i])
							elif not hasInsertNameMsgBitplanesLen :
								bitplanes[i]['bitplane'] = self.intToBitplaneExpanded(nameMsgBitplanesLen)
								if(self.calculateComplexity(bitplanes[i]['bitplane']) < self.threshold):
									bitplanes[i]['bitplane'] = self.conjugateBitplane(bitplanes[i]['bitplane'])
									self.appendConjugateTable(1)
								else:
									self.appendConjugateTable(0)
								print("hasInsertNameMsgBitplanesLen",nameMsgBitplanesLen)
								hasInsertNameMsgBitplanesLen = True
								arrayOfPosition.append([idx,jdx,i])
							elif not hasInsertConjugateBitplaneLen :
								bitplanes[i]['bitplane'] = self.intToBitplaneExpanded(conjugateBitplaneLen)
								if(self.calculateComplexity(bitplanes[i]['bitplane']) < self.threshold):
									bitplanes[i]['bitplane'] = self.conjugateBitplane(bitplanes[i]['bitplane'])
									self.appendConjugateTable(1)
								else:
									self.appendConjugateTable(0)
								print("hasInsertConjugateBitplaneLen",conjugateBitplaneLen)
								hasInsertConjugateBitplaneLen = True
								arrayOfPosition.append([idx,jdx,i])
							elif not hasInsertNameMsg :
								bitplanes[i]['bitplane'] = nameMsgBitplanes[nameMsgBitplaneIdx]
								if(self.calculateComplexity(bitplanes[i]['bitplane']) < self.threshold):
									bitplanes[i]['bitplane'] = self.conjugateBitplane(bitplanes[i]['bitplane'])
									self.appendConjugateTable(1)
								else:
									self.appendConjugateTable(0)
								nameMsgBitplaneIdx+=1
								arrayOfPosition.append([idx,jdx,i])
								if nameMsgBitplaneIdx >= nameMsgBitplanesLen :
									hasInsertNameMsg = True
							elif not hasInsertMsg :
								bitplanes[i]['bitplane'] = self.msgBitplanes[msgBitplaneIdx]['bitplane']
								if(self.calculateComplexity(bitplanes[i]['bitplane']) < self.threshold):
									bitplanes[i]['bitplane'] = self.conjugateBitplane(bitplanes[i]['bitplane'])
									self.appendConjugateTable(1)
								else:
									self.appendConjugateTable(0)
								msgBitplaneIdx += 1
								arrayOfPosition.append([idx,jdx,i])
								if (msgBitplaneIdx >= msgBitplaneLen) :
									hasInsertMsg = True
									self.makeFinalConjugateTable()
							elif not hasInsertConjugateTable :
								bitplanes[i]['bitplane'] = self.conjugateTable[conjugateBitplaneIdx]
								if(self.calculateComplexity(bitplanes[i]['bitplane']) < self.threshold):
									bitplanes[i]['bitplane'] = self.conjugateBitplane(bitplanes[i]['bitplane'])
									conjugateConjugateTableTable.append(1)
								else:
									conjugateConjugateTableTable.append(0)
								conjugateBitplaneIdx+=1
								arrayOfPosition.append([idx,jdx,i])
								if (conjugateBitplaneIdx >= conjugateBitplaneLen) :
									hasInsertConjugateTable = True
							elif not hasInsertConjugateConjugateTableTable :
								if (conjugateConjugateTableTableIdx < conjugateBitplaneLen):
									bitplanes[i]['bitplane'] = self.conjugateBitplane(self.intToBitplaneExpanded(conjugateConjugateTableTable[conjugateConjugateTableTableIdx]))
									conjugateConjugateTableTableIdx+=1
									arrayOfPosition.append([idx,jdx,i])
								else:
									hasInsertConjugateConjugateTableTable = True
						if hasInsertmsgBitplaneLen and hasInsertNameMsgBitplanesLen and hasInsertConjugateBitplaneLen and hasInsertNameMsg and hasInsertMsg and hasInsertConjugateTable and hasInsertConjugateConjugateTableTable:
							break
						i+=1

					if hasInsertmsgBitplaneLen and hasInsertNameMsgBitplanesLen and hasInsertConjugateBitplaneLen and hasInsertNameMsg and hasInsertMsg and hasInsertConjugateTable and hasInsertConjugateConjugateTableTable:
						break
					jdx+=1
				replaced.append(idx)
			if hasInsertmsgBitplaneLen and hasInsertNameMsgBitplanesLen and hasInsertConjugateBitplaneLen and hasInsertNameMsg and hasInsertMsg and hasInsertConjugateTable and hasInsertConjugateConjugateTableTable:
				break
			keyIdx+=1

			if keyIdx == keyLen:
				keyIdx = 0

			if self.random:
				idx += 2
			else:
				idx += 1

			if idx >= bitplaneLen and self.random:
				if isReturn:
					break

				if isEven:
					idx = 1
				else:
					idx = 0
				isReturn = True
		if not (hasInsertmsgBitplaneLen and hasInsertNameMsgBitplanesLen and hasInsertConjugateBitplaneLen 
			and hasInsertNameMsg and hasInsertMsg and hasInsertConjugateTable and hasInsertConjugateConjugateTableTable):
			return False

		return True

	#Model tabel berupa bitplanes
	def appendConjugateTable(self, bit):
		if (len(self.conjugateTable) == 0):
			self.conjugateTable.append([bit])
		elif(len(self.conjugateTable[-1])==64):
			self.conjugateTable.append([bit])
		else:
			self.conjugateTable[-1].append(bit)

	def appendConjugateTableFunction(self,conjugateTable,bit):
		if (len(conjugateTable) == 0):
			conjugateTable.append([bit])
		elif(len(conjugateTable[-1])==64):
			conjugateTable.append([bit])
		else:
			conjugateTable[-1].append(bit)

	def makeFinalConjugateTable(self):
		lenghtOfLastBitplane = len(self.conjugateTable[-1])
		if(lenghtOfLastBitplane!=64):
			for i in range(64-lenghtOfLastBitplane):
				self.conjugateTable[-1].append(0)
	
	def makeFinalConjugateTableFunction(self, conjugateTable):
		lenghtOfLastBitplane = len(conjugateTable[-1])
		if(lenghtOfLastBitplane!=64):
			for i in range(64-lenghtOfLastBitplane):
				conjugateTable[-1].append(0)

	def createImage(self):
		idx = 0
		while idx < len(self.bitPlanes):
			i = 0
			rgb = []
			blockLen = len(self.bitPlanes[idx])
			if self.cgc:
				self.convertCGC2PBC(self.bitPlanes[idx], self.pbcBitplanes[idx])
			while i < 64:
				j = 0
				values = []
				while j < blockLen:
					k = 0
					bit = ''
					while k < 8:
						bit += str(self.bitPlanes[idx][j][k]['bitplane'][i])
						k+=1
					values.append(int(bit, 2))
					j+=1
				rgb.append(values)
				i+=1

			self.blocks[idx] = rgb
			idx+=1
	
	def create_image(self, i, j):
		image = Image.new(self.mode, (i, j), "white")
		return image

	def writeImage(self):
		width, height = self.image.size
		new = self.create_image(width, height)
		pixels = new.load()

		i = 1
		idx = 0
		limit = 0
		col = 0
		limitIdx = 0

		while i < width+1:
			j = 1
			while j < height+1:

				if j == 1:
					idx = limitIdx
				if self.mode == 'L':
					pixels[i-1, j-1] = self.blocks[col][idx][0]
				else:
					pixels[i-1, j-1] = tuple(self.blocks[col][idx])

				idx += 1
				if j % 8 == 0 or j >= height:
					col += 1
					idx = limitIdx

				j+=1

			limitIdx += 8
			if i % 8 == 0:
				limit = col
				limitIdx = 0

			col = limit
			i+=1

		# self.convertCGC2PBC(new)
		arr_splited = self.imagePath.split("/")
		# print(os.path.join(settings.MEDIA_ROOT, 'stego_' + arr_splited[-1]))

		new.save(os.path.join(settings.MEDIA_ROOT, 'stego_' + arr_splited[-1]), self.image.format)

	def extracting(self):
		self.msgBitplanes = []
		isEven = self.seed()
		if isEven:
			idx = 0
		else:
			idx = 1
		arrayOfPosition = []
		keyLen = len(self.key)
		keyIdx = 0
		extracted = []
		msgBitplaneNumber = 0
		nameFileBitplaneNumber = 0
		conjugateBitplaneNumber = 0
		hasGetMsgBitplaneNumber = False
		hasGetNameFileBitplaneNumber = False
		hasGetConjugateBitplaneNumber = False
		hasGetNameFile = False
		hasGetMsg = False
		hasGetConjugateTable = False
		hasGetPosition = False
		hasGetConjugateConjugateTableTable = False
		getPositionIndx = 0
		nameFileBitplaneIdx = 0
		nameFileBitplanes = []
		msgBitplaneIdx = 0
		conjugateConjugateTableTable = []
		conjugateConjugateTableTableIdx = 0
		conjugateTableIdx = 0
		
		bitplaneLen = len(self.bitPlanes)
		isReturn = False

		while idx < bitplaneLen:
			if idx not in self.notAllowed and idx not in extracted:
				jdx=0
				for bitplanes in self.bitPlanes[idx]: # 1 for grayscale, 3 for rgb
					i = 0
					while i < len(bitplanes): 
						
						if bitplanes[i]['complexity'] > self.threshold:
							if not hasGetMsgBitplaneNumber :
								extracted.append(idx)
								self.msgLen = self.bitplaneToInt(self.conjugateBitplane(bitplanes[i]['bitplane']))
								numberOfBit =  self.msgLen*8
								modular64OfNumber = numberOfBit%64
								if(modular64OfNumber == 0):
									msgBitplaneNumber = self.msgLen/8
								else:
									msgBitplaneNumber = self.msgLen/8+1
								arrayOfPosition.append([idx,jdx,i])
								hasGetMsgBitplaneNumber = True
								print("size ", self.msgLen)
								print("Jumlah bitplane pesan", msgBitplaneNumber)
							elif not hasGetNameFileBitplaneNumber :
								extracted.append(idx)
								nameFileBitplaneNumber = self.bitplaneToInt(self.conjugateBitplane(bitplanes[i]['bitplane']))
								arrayOfPosition.append([idx,jdx,i])
								hasGetNameFileBitplaneNumber = True
								print("Jumlah bitplane nama pesan", nameFileBitplaneNumber)
							elif not hasGetConjugateBitplaneNumber :
								extracted.append(idx)
								conjugateBitplaneNumber = self.bitplaneToInt(self.conjugateBitplane(bitplanes[i]['bitplane']))
								arrayOfPosition.append([idx,jdx,i])
								hasGetConjugateBitplaneNumber = True
								print("Jumlah bitplane tabel konjugasi", conjugateBitplaneNumber)
							elif not hasGetPosition:
								extracted.append(idx)
								arrayOfPosition.append([idx,jdx,i])
								getPositionIndx+=1
								if(getPositionIndx >= (msgBitplaneNumber+nameFileBitplaneNumber+(conjugateBitplaneNumber*2))):
									hasGetPosition = True
							
						i+=1
						if hasGetMsgBitplaneNumber and hasGetNameFileBitplaneNumber and hasGetConjugateBitplaneNumber and hasGetPosition:
							break
					if hasGetMsgBitplaneNumber and hasGetNameFileBitplaneNumber and hasGetConjugateBitplaneNumber and hasGetPosition:
						break
					jdx+=1

			if hasGetMsgBitplaneNumber and hasGetNameFileBitplaneNumber and hasGetConjugateBitplaneNumber and hasGetPosition:
				break

			keyIdx += 1
			if keyIdx == keyLen:
				keyIdx = 0

			if self.random:
				idx += 2
			else:
				idx += 1

			if idx >= len(self.bitPlanes) and self.random:
				if isReturn:
					break

				if isEven:
					idx = 1
				else:
					idx = 0
				isReturn = True

		if not (hasGetMsgBitplaneNumber and hasGetNameFileBitplaneNumber and hasGetConjugateBitplaneNumber and hasGetPosition):
			return False

		try:
			idx=0
			#print("posisi",arrayOfPosition)
			while (idx < len(arrayOfPosition)):
				if not hasGetConjugateConjugateTableTable :
					startIdx = 1 + 1 + 1 + nameFileBitplaneNumber + msgBitplaneNumber + conjugateBitplaneNumber
					if (conjugateConjugateTableTableIdx < conjugateBitplaneNumber):
						row = arrayOfPosition[startIdx+conjugateConjugateTableTableIdx][0]
						col = arrayOfPosition[startIdx+conjugateConjugateTableTableIdx][1]
						zoz = arrayOfPosition[startIdx+conjugateConjugateTableTableIdx][2]
						conjugateConjugateTableTable.append(self.bitplaneToInt(self.conjugateBitplane(self.bitPlanes[row][col][zoz]['bitplane'])))
					else:
						print('tabel konjugasi untuk tabel konjugasi')
						print(conjugateConjugateTableTable)
						hasGetConjugateConjugateTableTable = True
					conjugateConjugateTableTableIdx+=1
				elif not hasGetConjugateTable :
					startIdx = 1 + 1 + 1 + nameFileBitplaneNumber + msgBitplaneNumber
					if conjugateTableIdx < conjugateBitplaneNumber :
						row = arrayOfPosition[startIdx+conjugateTableIdx][0]
						col = arrayOfPosition[startIdx+conjugateTableIdx][1]
						zoz = arrayOfPosition[startIdx+conjugateTableIdx][2]
						if(conjugateConjugateTableTable[conjugateTableIdx]==0):
							self.conjugateTable.append(self.bitPlanes[row][col][zoz]['bitplane'])
						else:
							self.conjugateTable.append(self.conjugateBitplane(self.bitPlanes[row][col][zoz]['bitplane']))
					else :
						print('tabel konjugasi')
						print(self.conjugateTable)
						hasGetConjugateTable = True
					conjugateTableIdx+=1
				elif not hasGetNameFile :
					startIdx = 1+1+1								
					rowCon = (startIdx+nameFileBitplaneIdx)/64
					colCon = (startIdx+nameFileBitplaneIdx)%64
					row = arrayOfPosition[startIdx+nameFileBitplaneIdx][0]
					col = arrayOfPosition[startIdx+nameFileBitplaneIdx][1]
					zoz = arrayOfPosition[startIdx+nameFileBitplaneIdx][2]
					if(self.conjugateTable[rowCon][colCon] == 0):
						nameFileBitplanes.append(self.bitPlanes[row][col][zoz]['bitplane'])
					else:
						nameFileBitplanes.append(self.conjugateBitplane(self.bitPlanes[row][col][zoz]['bitplane']))
					nameFileBitplaneIdx+=1
					if nameFileBitplaneIdx >= nameFileBitplaneNumber:
						print("name bitplane", nameFileBitplanes)
						self.fileMsgName = self.bitplanesToString(nameFileBitplanes)
						print('nama msg', self.fileMsgName)
						hasGetNameFile = True
				elif not hasGetMsg :
					startIdx = 1+1+1+nameFileBitplaneNumber
					rowCon = (startIdx+msgBitplaneIdx)/64
					colCon = (startIdx+msgBitplaneIdx)%64
					row = arrayOfPosition[startIdx+msgBitplaneIdx][0]
					col = arrayOfPosition[startIdx+msgBitplaneIdx][1]
					zoz = arrayOfPosition[startIdx+msgBitplaneIdx][2]
					if(self.conjugateTable[rowCon][colCon] == 0):
						self.msgBitplanes.append(self.bitPlanes[row][col][zoz]['bitplane'])
					else:
						self.msgBitplanes.append(self.conjugateBitplane(self.bitPlanes[row][col][zoz]['bitplane']))
					msgBitplaneIdx+=1
					if msgBitplaneIdx >= msgBitplaneNumber:
						print('pesan selesai')
						hasGetMsg=True

				idx+=1
			return True
		except Exception as e:
			return False
		

	def joinMessage(self):
		bits = []
		bit = ''
		for bitplane in self.msgBitplanes:

			for b in bitplane:
				bit += str(b)
				if len(bit) == 8:
					bits.append(bit)
					bit = ''

		self.message = ''
		for bit in bits:
			self.message += chr(int(bit, 2))
			if len(self.message) == self.msgLen:
				break

	def createExtractedFile(self):
		file = open(os.path.join(settings.MEDIA_ROOT, self.fileMsgName), 'w')
		file.write(self.message)
		file.close()

	def payloadByte(self):
		# self.bitPlanes harus sudah terisi
		slotBitPlane = 0
		for a in self.bitPlanes:
			for b in a:
				for c in b:
					if c['complexity']>self.threshold:
						slotBitPlane += 1

		slotBitPlane -= 50 # penyimpanan filename, extension, file size, conjugation map

		# payload = slot x 8 byte (atau slot x 64 bit)
		return slotBitPlane*8

	def payloadBit(self):
		return payloadByte*8


	def option(self, is_cgc, is_random):
		self.random = is_random
		self.cgc = is_cgc

	def setThreshold(self, new_thres):
		if new_thres != '' :
			self.threshold = new_thres



if __name__ == "__main__":
	filename = raw_input("Image name: ")
	secret_file = raw_input("Secret File: ")
	bpcs = BPCS(filename, secret_file)
	key = raw_input("key: ")

	start_time = time.time()
	bpcs.option(True, True)
	bpcs.dividePixels()
	bpcs.createBitplanes()
	bpcs.readMsg()
	bpcs.setStegoKey(key)

	bpcs.encryptMsg()
	bpcs.divideMessage()
	bpcs.createMsgBitplane()
	bpcs.embedding()

	bpcs.createImage()

	bpcs.writeImage()

	print("Embed time")
	print("--- %s seconds ---" % (time.time() - start_time))
	
	start_time = time.time()
	bpcs = BPCS('stego_'+filename, 'mple.txt')
	bpcs.option(True, True)
	bpcs.dividePixels()
	bpcs.createBitplanes()
	bpcs.setStegoKey(key)
	bpcs.extracting()
	bpcs.joinMessage()
	bpcs.decryptMsg()
	print(bpcs.message)
	bpcs.createExtractedFile()
	print("Extract time")
	print("--- %s seconds ---" % (time.time() - start_time))