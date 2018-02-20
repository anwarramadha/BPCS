import math
import numpy
from PIL import Image
import time
# gambar = Image.open("lena512.bmp") #Can be many different formats.
# pixel = gambar.load()
# print gambar.size #Get the width and hight of the image for iterating over
# print pixel[0,0] #Get the RGBA Value of the a pixel of an image

global max_diff
max_diff = 255

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
			return 0
		else:
			# image is very different
			return max_diff

# 	# img1 and img2 have to be matrix and must have the same the exact same size
# 	def getMSE(img1, img2):
# 		row = len(img1)
# 		column = len(img1[0])
# 		size = row*column
# 		totalSelisihKuadrat = 0.0
# 		for i in range(row):
# 			for j in range(column):
# 				selisih = img1[i][j]-img2[i][j]
# 				totalSelisihKuadrat += math.pow(selisih,2)
# 		return math.pow(totalSelisihKuadrat/size,0.5)

	def getPSNR(self):
		mse = self.getMSE
		if (mse!=0):
			return 20*math.log(max_diff/rms,10)
		else:
			return 9999999999999999999999999999999999999999999999


	def printPSNR(self):
		psnr = self.getPSNR()
		if (psnr==9999999999999999999999999999999999999999999999):
			print("Tidak ada perbedaan image")
		else:
			print("Image berbeda dengan PSNR = ".format(psnr))

if __name__ == "__main__":
	# INPUT
	filename1 = raw_input("Image 1 name: ")
	filename2 = raw_input("Image 2 name: ")

	# PROSES
	start_time = time.time()
	comparer = ImageComparer(filename1, filename2)
	print(comparer.isImgSameColorType())
	print(comparer.image1.size[0])
	print(comparer.pixel2[0,0])

	# OUTPUT
	print("Run time")
	print("--- %s seconds ---" % (time.time() - start_time))
