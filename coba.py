import math
import numpy

class Nyoba :
	
	def __init__(self):
		pass

	# img1 or img2 must be a matrix
	def isImgSameSize(img1, img2):
		if (len(img1)==len(img2)) and (len(img1[0])==len(img2[0])):
			return True
		else:
			return False

	# img1 and img2 have to be matrix and must have the same the exact same size
	# def getMSE(img1, img2):
	# 	for arr1 in img1:


	def getPSNR(rms, max_diff):
		if (rms!=0):
			return 20*math.log(max_diff/rms,10)
		else:
			return 9999999999999999999999999999999999999999999999

	def printPSNR(rms, max_diff):
		psnr = Nyoba.getPSNR(rms, max_diff)
		if (psnr==9999999999999999999999999999999999999999999999):
			print("Tidak ada perbedaan image")
		else:
			print("Image berbeda dengan PSNR = ", end="")
			print(psnr)

Nyoba.printPSNR(0.00000001, 256)
print(Nyoba.isImgSameSize([[1,0],[0,1]],[[2,3],[5,7]]))