# Untuk penysipan pesan pada gambar berformat bmp dan png yang tidak terkompresi
# gambar memiliki warna 1 byte atau 3 byte

import binascii
import io
import sys
from PIL import Image
import readline
readline.parse_and_bind("tab: complete")
global chessBoard, threshold, maxChange
chessBoard = [i % 2 for i in xrange(64)]
threshold = 0.3
maxChange = 112

# kelas untuk menampung bitplane
# untuk mempermudah perhitungan kompleksitas, pbc->cgc
class Bitplane:
	def __init__(self):
		self.bits = []
		self.complexity = 0

	def fillBits(self, bit, bitPlaneNumber):
		self.bits.append(int(bit[7-bitPlaneNumber]))

	def convertPBCCGC(self):
		i = 1
		# print(self.bits)
		converted = [self.bits[0]]
		while i < len(self.bits):
			converted.append(self.bits[i-1] ^ self.bits[i])
			i+=1

		self.bits = converted

	def calculateComplexity(self):
		i = 0
		change = 0
		while i < len(self.bits):
			if i < 55 and i % 8 != 0:
				change += abs(self.bits[i]-self.bits[i-1])+abs(self.bits[i]-self.bits[i+8])
			elif i % 8 == 0 and i < 55:
				change += abs(self.bits[i]-self.bits[i+8])
			elif i > 55:
				change += abs(self.bits[i]-self.bits[i-1])
			i+=1

		self.complexity = float(change)/float(maxChange)

	def conjugateBitplane(self):
		i = 0
		while i < len(self.bits):
			self.bits[i] ^= chessBoard[i]
			i+=1

class BPCS :

	def __init__(self, imagePath, filename):
		self.imagePath = imagePath
		self.image = Image.open(self.imagePath)
		self.blocks = []
		self.bitPlanes = []
		self.fileMsgName = filename
		self.msgBlocks = []
		self.notAllowed = []

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

	def dividingPixel(self):
		i = 1
		idx = 0
		limit = 0
		col, row = self.definePixelBoundary()

		px = self.image.load() # load pixel dari gambar
		while i < col:
			bits = []
			j = 1
			while j < row:

				if j < self.height + 1 and i < self.height + 1: # iterasi masih kurang dari jumlah pixel
					if isinstance(px[i-1, j-1], int): # gambar grayscale
						tup = (px[i-1, j-1], )
						bits.append([bin(x)[2:].zfill(8) for x in tup])
					else: # gambar berwarna
						bits.append([bin(x)[2:].zfill(8) for x in px[i-1,j-1]])
				else:
					exc =  bin(256)[2:].zfill(8)
					bits.append((exc, exc, exc)) 
					if idx not in self.notAllowed:
						self.notAllowed.append(idx)

				if j % 8 == 0 or (j > self.height and len(bits) == 8):

					self.blocks[idx].append(bits)
					idx += 1
					bits = []

				j+=1

			if i % 8 == 0: 
				limit = idx

			idx = limit
			i+=1

	def initializeBlock(self, blocksize):
		# buat tempatnya bloknya dulu
		i = 0
		blocks = []
		while i < blocksize :
			blocks.append([])
			i+=1
		return blocks

	def dividePixels(self):

		i = 0 

		#jumlah blok
		blockSize = self.defineBlockSize()

		self.blocks = self.initializeBlock(blockSize)

		self.dividingPixel()

		# ubah list langsung jadi 8x8
		i = 0
		while i < len(self.blocks):
			colorList = []
			for colors in self.blocks[i]:
				for color in colors:
					colorList.append(color)

			self.blocks[i] = colorList
			i += 1

	def createBitplanes(self): 

		for block in self.blocks:
			i = 0
			bitplaneForAllColor = []
			while i < len(block[0]): # 3 for rgb, 1 for grayscale
				j = 0
				bitplaneForEachColor = []
				while j < 8: # 8 bit dari setiap warna pada rgb
					k = 0
					bitplane = Bitplane()
					while k < 64: # 64 jumlah kelompok warna

						bitplane.fillBits(block[k][i], j)
						k += 1
					j += 1

					# ubah dari PBC ke CGC
					bitplane.convertPBCCGC()
					bitplane.calculateComplexity()
					bitplaneForEachColor.append(bitplane)
					# bitplane.bits  = []
				bitplaneForAllColor.append(bitplaneForEachColor)
			
				i+=1
			self.bitPlanes.append(bitplaneForAllColor) # list dari bitplane semua warna, len = 1 untuk grayscale, 3 untuk rgb

	def defineMsgLen(self):
		if self.msglen % 8 == 0:
			return self.msglen
		else:
			return self.msglen + (8 - self.msglen % 8) + 1

	def divideMessage(self):
		file = open(self.fileMsgName, 'r')
		self.message = file.read()
		file.close()

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

	def createMsgBitplane(self):
		self.msgBitplanes = []

		for block in self.msgBlocks:
			i = 0
			bitplane = Bitplane()
			while i < 8: # 8 bit pada pesan
				j = 0
				while  j < 8: #jumlah bit pesan dalam 1 block
					bitplane.fillBits(block[j], i)
					j+=1
				i+=1
			bitplane.calculateComplexity()

			if bitplane.complexity < threshold:
				bitplane.conjugateBitplane()
				bitplane.calculateComplexity()

			self.msgBitplanes.append(bitplane)

	def sequentialEmbedding(self):
		# pass
		msgBitplaneIdx = 0
		idx = 0

		for colors in self.bitPlanes:
			if idx not in self.notAllowed:
				for bitplanes in colors: # 1 for grayscale, 3 for rgb
					i = 0
					while i < len(bitplanes): 
						if bitplanes[i].complexity > threshold and msgBitplaneIdx < len(self.msgBitplanes):
							bitplanes[i].bits = self.msgBitplanes[msgBitplaneIdx].bits
							msgBitplaneIdx += 1

						if msgBitplaneIdx == len(self.msgBitplanes):
							break

						i+=1
					if msgBitplaneIdx == len(self.msgBitplanes):
						break
			idx += 1

	def createImage(self):
		blocks = []
		for block in self.bitPlanes:
			pass


if __name__ == "__main__":
	filename = raw_input("Image name: ")
	bpcs = BPCS(filename, 'example.txt')
	bpcs.dividePixels()
	bpcs.createBitplanes()
	bpcs.divideMessage()
	bpcs.createMsgBitplane()
	bpcs.sequentialEmbedding()
	bpcs.createImage()
		# print(bpcs.msgBitplanes[0].bits)