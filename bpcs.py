import binascii
import io
import sys
from PIL import Image
import readline
readline.parse_and_bind("tab: complete")

class BPCS :

	def __init__(self, imagePath):
		self.imagePath = imagePath
		self.blocks = []

	def dividePixels(self):
		image = Image.open(self.imagePath)

		self.width, self.height = image.size

		i = 0 

		#jumlah blok
		blockSize = (self.width / 8 + int(self.width % 8 == 1)) * (self.height / 8 + int(self.height % 8 == 1)) 

		# buat tempatnya bloknya dulu
		while i < blockSize :
			self.blocks.append([])
			i+=1

		i = 1
		idx = 0
		limit = 0
		row = 0
		col = 0

		# tentukan batas pixel
		if self.width % 8 == 0: # pixel kelipatan 8
			col = self.width + 1
		else: # pixel bukan kelipatan 8
			col = self.width + (8 - self.width % 8) + 1

		if self.height % 8 == 0:
			row = self.height + 1
		else:
			row = self.height + (8 - self.height % 8) + 1


		px = image.load() # load pixel dari gambar

		while i < col:
			bits = []
			j = 1
			while j < row:

				if j < self.height + 1: # iterasi masih kurang dari jumlah pixel
					bits.append(px[i-1,j-1])
				else:
					bits.append((999, 999, 999))

				if j % 8 == 0 or (j > self.height and len(bits) == 8):
					self.blocks[idx].append(bits)
					idx += 1
					bits = []

				j+=1

			if i % 8 == 0: 
				limit = idx

			idx = limit
			i+=1

	def extractBytes(self):

		image = Image.open(self.imageName)

		self.width, self.height = image.size


		# with open(self.imagePath, "rb") as imageFile:
		# 	f = imageFile.read()
		# 	b = bytearray(f)

		# 	imageFile.close()
		# 	for byte in b:
		# 		self.imageBin.append(bin(byte)[2:].zfill(8))

	# def dividePixel(self):

if __name__ == "__main__":
	filename = raw_input("Image name: ")
	bpcs = BPCS(filename)
	bpcs.dividePixels()
	print(bpcs.blocks)