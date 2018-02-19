import math

class Nyoba :
	
	def __init__(self):
		pass

	def getPNSR(double rms):
		return 10*math.log(256/rms,10)