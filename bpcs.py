# Untuk penysipan pesan pada gambar berformat bmp dan png yang tidak terkompresi
# gambar memiliki warna 1 byte atau 3 byte
import time
import binascii
import io
import sys
import extended_vigenere as cipher
from PIL import Image
from ImageComparer import ImageComparer
# import readline
# readline.parse_and_bind("tab: complete")
global chessBoard, threshold, maxChange
chessBoard = [i % 2 for i in xrange(64)]
threshold = 0.3
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
		self.msgBlocks = []
		self.notAllowed = []

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
	# 				px[j, i] = self.pbc[j, i]
	# 			else:
	# 				if isinstance(self.pbc[j, i], int):
	# 					px[j, i] = self.pbc[j, i] ^ self.pbc[j-1, i]
	# 				else:
	# 					tup = []
	# 					k = 0
	# 					while k < 3:
	# 						res = self.pbc[j, i][k] ^ self.pbc[j-1, i][k]
	# 						tup.append(res)
	# 						k+=1
	# 					px[j, i] = tuple(tup)
	# 			j+=1
	# 		i+=1

	# 	return image

	# def convertCGC2PBC(self, image):
	# 	self.pbc = self.image.load()
	# 	width = self.image.size[0]
	# 	height = self.image.size[1]
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
	# 				px[j, i] = px[j, i]
	# 			else:
	# 				if isinstance(px[j, i], int):
	# 					px[j, i] = px[j, i] ^ px[j-1, i]
	# 				else:
	# 					tup = []
	# 					k = 0
	# 					while k < 3:
	# 						res = px[j, i][k] ^ px[j-1, i][k]
	# 						tup.append(res)
	# 						k+=1
	# 					px[j, i] = tuple(tup)
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

					bitplane = {'bitplane':bits, 'complexity':0}
					bitplaneForEachColor.append(bitplane)

				bitplaneForAllColor.append(bitplaneForEachColor)
			
				i+=1
			self.convertPBC2CGC(bitplaneForAllColor)
			self.bitPlanes.append(bitplaneForAllColor)
			

	def setStegoKey(self, key):
		self.key = key

	def encryptMsg(self):
		self.message = cipher.encrypt(self.message, self.key)

	def decryptMsg(self):
		self.message = cipher.decrypt(self.message, self.key)

	def defineMsgLen(self):
		if self.msglen % 8 == 0:
			return self.msglen
		else:
			return self.msglen + (8 - self.msglen % 8) + 1

	def readMsg(self):
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

	def seed(self, idx):
		if len(self.key) > 0:
			return cipher.extended_ascii.index(self.key[idx]) % 10
		elif len(self.key) == 0 or self.seq == 1:
			return 1

	def embedding(self):
		# pass
		msgBitplaneIdx = 0
		idx = self.seed(0)
		keyLen = len(self.key)
		keyIdx = 0
		replaced = []
		bitplaneLen = len(self.bitPlanes)
		msgBitplaneLen = len(self.msgBitplanes)

		while idx < bitplaneLen:
			if idx not in self.notAllowed and idx not in replaced:
				for bitplanes in self.bitPlanes[idx]: # 1 for grayscale, 3 for rgb
					i = 0
					while i < len(bitplanes): 

						if bitplanes[i]['complexity'] > threshold and msgBitplaneIdx < len(self.msgBitplanes):
							replaced.append(idx)
							bitplanes[i]['bitplane'] = self.msgBitplanes[msgBitplaneIdx]['bitplane']
							msgBitplaneIdx += 1

						if msgBitplaneIdx == msgBitplaneLen:
							break


						i+=1
					if msgBitplaneIdx == msgBitplaneLen:
						break
			if msgBitplaneIdx == msgBitplaneLen:
				break
			keyIdx+=1

			if keyIdx == keyLen:
				keyIdx = 0

			idx += self.seed(keyIdx)
			if idx >= bitplaneLen and len(replaced) < len(self.msgBitplanes):
				idx = 0



	def createImage(self):
		idx = 0
		while idx < len(self.bitPlanes):
			i = 0
			rgb = []
			blockLen = len(self.bitPlanes[idx])
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
		new.save('stego_'+self.imagePath, self.image.format)

	def extracting(self):
		self.msgBitplanes = []
		idx = self.seed(0)
		keyLen = len(self.key)
		keyIdx = 0
		extracted = []
		msgBitplaneNumber = 91
		bitplaneLen = len(self.bitPlanes)

		while idx < bitplaneLen:
			if idx not in self.notAllowed and idx not in extracted:
				for bitplanes in self.bitPlanes[idx]: # 1 for grayscale, 3 for rgb
					i = 0
					while i < len(bitplanes): 

						if bitplanes[i]['complexity'] > threshold:
							extracted.append(idx)
							self.msgBitplanes.append(bitplanes[i])

						i+=1
						if len(self.msgBitplanes) >= msgBitplaneNumber:
							break
					if len(self.msgBitplanes) >= msgBitplaneNumber:
						break

			if len(self.msgBitplanes) >= msgBitplaneNumber:
				break
			keyIdx += 1
			if keyIdx == keyLen:
				keyIdx = 0

			idx += self.seed(keyIdx)
			if idx >= len(self.bitPlanes) and len(extracted) < msgBitplaneNumber:
				idx = 0

	def joinMessage(self):
		bits = []
		bit = ''
		for bitplane in self.msgBitplanes:

			i = 1
			for b in bitplane['bitplane']:
				bit += str(b)
				if i % 8 == 0:
					bits.append(bit)
					bit = ''
				i+=1

		self.message = ''
		for bit in bits:
			self.message += chr(int(bit, 2))

	def payloadByte(self):
		# self.bitPlanes harus sudah terisi
		slotBitPlane = 0
		for a in self.bitPlanes:
			for b in a:
				for c in b:
					if c['complexity']>threshold:
						slotBitPlane += 1

		slotBitPlane -= 50 # penyimpanan filename, extension, file size, conjugation map

		# payload = slot x 8 byte (atau slot x 64 bit)
		return slotBitPlane*8

	def payloadBit(self):
		return payloadByte*8



if __name__ == "__main__":
	# INPUT
	filename = raw_input("Image 1 name: ")
	bpcs = BPCS(filename, 'example.txt')
	# bpcs.convertCGC2PBC().save("lenna_double_convert.bmp")
	key = raw_input("key: ")

	# PROSES
	start_time = time.time()
	bpcs.dividePixels()
	bpcs.createBitplanes()
	print('Payload = {} byte'.format(bpcs.payloadByte()))
	bpcs.readMsg()
	bpcs.setStegoKey(key)

	bpcs.encryptMsg()
	bpcs.divideMessage()
	bpcs.createMsgBitplane()
	bpcs.embedding()

	bpcs.createImage()

	bpcs.writeImage()	

	# OUTPUT
	print("Run time")
	print("--- %s seconds ---" % (time.time() - start_time))
	
	start_time = time.time()
	bpcs1 = BPCS('stego_'+filename, 'example.txt')
	bpcs1.dividePixels()
	bpcs1.createBitplanes()
	bpcs1.setStegoKey(key)
	bpcs1.extracting()
	bpcs1.joinMessage()
	bpcs1.decryptMsg()
	print(bpcs1.message)
	print("Extract time")
	print("--- %s seconds ---" % (time.time() - start_time))
	comparer = ImageComparer(filename, "stego_"+filename)
	comparer.printPSNR()