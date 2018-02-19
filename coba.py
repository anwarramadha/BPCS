import math

class Nyoba :
	
	def __init__(self):
		pass

	def getPNSR(rms):
		if (rms!=0):
			return 20*math.log(256/rms,10)
		else:
			return 9999999999999999999999999999999999999999999999

	def printPNSR(rms):
		pnsr = Nyoba.getPNSR(rms)
		if (pnsr==9999999999999999999999999999999999999999999999):
			print("Tidak ada perbedaan image")
		else:
			print("Image berbeda dengan PNSR = ", end="")
			print(pnsr)

Nyoba.printPNSR(0.00000001)