import math
import numpy
from PIL import Image
import time
global max_diff
max_diff = 255.0

class ImageComparer :
	def __init__(self, image1_name, image2_name):
		self.image1_name = image1_name
		self.image2_name = image2_name
		self.image1 = Image.open(self.image1_name)
		self.image2 = Image.open(self.image2_name)
		self.pixel1 = self.image1.load()
		self.pixel2 = self.image2.load()

	def isImgSameSize(self):
		if self.image1.size[0] == self.image2.size[0] and self.image1.size[1] == self.image2.size[1]:
			return True
		else:
			return False

	def isImgSameColorType(self):
		if isinstance(self.pixel1[0,0],int) == isinstance(self.pixel2[0,0],int): # harus sama2 warna atau sama2 item putih
			return True
		else:
			return False

	def getMSE(self):
		if self.isImgSameSize() and self.isImgSameColorType():
			# proses
			width = self.image1.size[0] # image1 or image2 does not matter
			height = self.image1.size[1] # image1 or image2 does not matter
			size = width*height
			# check color
			if isinstance(self.pixel1[0,0],int):
				grayscale = True
			else:
				grayscale = False
				size *= 3 # RGB, jadi ada 3

			total_selisih_kuadrat = 0.0
			i = 0
			while i < width:
				j = 0
				while j < height:
					if grayscale:
						selisih = self.pixel1[i,j] - self.pixel2[i,j]
						total_selisih_kuadrat += math.pow(selisih,2)
					else: # RGB
						k = 0
						while k < 3:
							selisih = self.pixel1[i,j][k] - self.pixel2[i,j][k]
							total_selisih_kuadrat += math.pow(selisih,2)

							k += 1

					j += 1

				i += 1

			return math.pow(total_selisih_kuadrat/size,0.5)
		else:
			# image is very different
			return max_diff


	def getPSNR(self):
		mse = self.getMSE()
		if (mse!=0):
			return 20*math.log(max_diff/mse,10)
		else:
			return 0


	def printPSNR(self):
		psnr = self.getPSNR()
		if (psnr==9999999999999999999999999999999999999999999999):
			print("Tidak ada perbedaan image")
		else:
			print('Image berbeda dengan PSNR = {}'.format(psnr))

if __name__ == "__main__":
	# INPUT
	filename1 = raw_input("Image 1 name: ")
	filename2 = raw_input("Image 2 name: ")

	# PROSES
	start_time = time.time()
	comparer = ImageComparer(filename1, filename2)
	comparer.printPSNR()

	# OUTPUT
	print("Run time")
	print("--- %s seconds ---" % (time.time() - start_time))
