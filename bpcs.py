# Untuk penysipan pesan pada gambar berformat bmp dan png yang tidak terkompresi
# gambar memiliki warna 1 byte atau 3 byte

import binascii
import io
import sys
from PIL import Image
import readline
readline.parse_and_bind("tab: complete")

# kelas untuk menampung bitplane
# untuk mempermudah perhitungan kompleksitas, pbc->cgc
class Bitplane:
	def __init__(self):
		self.bits = []
		self.complexity = 0
		self.maxChange = 112

	def fillBits(self, bit, bitPlaneNumber):
		self.bits.append(bit[7-bitPlaneNumber])

	def convertPBCCGC(self):
		i = 1
		converted =[int(self.bits[0])]
		while i < len(self.bits):
			converted.append(int(self.bits[i-1]) ^ int(self.bits[i]))
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
		# print(change)
		self.complexity = float(float(change)/float(self.maxChange))

class BPCS :

	def __init__(self, imagePath):
		self.imagePath = imagePath
		self.image = Image.open(self.imagePath)
		self.blocks = []
		self.bitPlanes = []

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
					bits.append((256, 256, 256)) # diisi dengan value yang sama agar kompleksitas rendah,
													# sehingga tidak dapat dijadikan tempat penyimpanan pesan

				if j % 8 == 0 or (j > self.height and len(bits) == 8):

					self.blocks[idx].append(bits)
					idx += 1
					bits = []

				j+=1

			if i % 8 == 0: 
				limit = idx

			idx = limit
			i+=1

	def dividePixels(self):

		i = 0 

		#jumlah blok
		blockSize = self.defineBlockSize()

		# buat tempatnya bloknya dulu
		while i < blockSize :
			self.blocks.append([])
			i+=1

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

	def createBitplanes(self): # not working WTF!
		bitplane = Bitplane()

		for block in self.blocks:
			i = 0
			bitplaneForAllColor = []
			while i < len(block[0]): # 3 for rgb, 1 for grayscale
				j = 0
				bitplaneForEachColor = []
				while j < 8: # 8 bit dari setiap warna pada rgb
					k = 0
					while k < 64: # 64 jumlah kelompok warna
						# print(block[k][i])
						bitplane.fillBits(block[k][i], j)
						k += 1
					j += 1
					# ubah dari PBC ke CGC
					bitplane.convertPBCCGC()
					bitplane.calculateComplexity()
					bitplaneForEachColor.append(bitplane)
					bitplane.bits  = []

				i+=1
				bitplaneForAllColor.append(bitplaneForEachColor) # list dari bitplane semua warna, len = 1 untuk grayscale, 3 untuk rgb
			self.bitPlanes.append(bitplaneForAllColor)


if __name__ == "__main__":
	filename = raw_input("Image name: ")
	bpcs = BPCS(filename)
	bpcs.dividePixels()
	# print(bpcs.blocks)
	bpcs.createBitplanes()
	# for c in bpcs.bitPlanes:
	# 	for x in c:
	# 		print(x.bits)