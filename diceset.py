# Defining a dice roller

import random
from math import sqrt as sqrt

def d(x):
	if x == 0:
		return 0
	else:
		x = int(sqrt(int(x) ** 2))
		try:
			num = random.randrange(1,int(x)+1,1)
		
		except ValueError:
			
			return 0
		
		return num

