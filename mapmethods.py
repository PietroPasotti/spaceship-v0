#'mapmethods
from populatedatabases import attackMultipliersDB, attackModifiersDB, disablingAttackConditionsDB
from populatedatabases import buildingsDB,disablingVisibilityConditionsDB,speedMultipliersDB,spaceshipDB
from math import sqrt as sqrt

import random
import namegen
from copy import deepcopy as deepcopy
import time
import sys
import spaceship

class MapMethodsValueError(ValueError):
	pass



existing_Buildings = []		#list of buildings
buildableItems = []			#list of asteroids
buildablePlots = []			#is a list with one nested list of tuples

def symmetry(mpcode):
	newmap = []
	i = len(mpcode)		
	for i in range(0,i,1):
		newmap.append(mpcode[len(mpcode) - i - 1])
	print('Reordering map...')
	return newmap
def createMapCode(height = 100,width = 100,asteroidratio = 0):
	"""Given height and width, plus optional asteroid ratio, produces a mapcode (randomized 0/1 matrix)."""	
	
	mapCode = {}
	
	probabPlotAsteroid = float( 0.01 + asteroidratio)
	
	print('Generating mapcode...')
	
	for y in range(height):
		for x in range(width):
			if random.random() > probabPlotAsteroid:
				pass
			else:
				mapCode[(x,y)] = 1
				pass
	
	return (mapCode,height,width)  
def LdistX(point,Map):
	return {dot for dot in Map.body.keys() if dot[0] in [(point[0] + 1), (point[0] - 1), point[0]]}			
def LdistY(point,Map):	
	return {dot for dot in Map.body.keys() if dot[1] in [(point[1] + 1), (point[1] - 1), point[1]]}
def	neighbourCount(point,dictionary):
	count = 0
	
	oripoint = deepcopy(point)
	
	if point in dictionary.keys():
		del dictionary[point]  #removes a dict entry from the mapcode
		pass
	else:
		pass
		
	pointX = point[0]
	pointY = point[1]
		 
		#set of dots which are max one column distant from point
	LdistX = {dot for dot in dictionary.keys() if dot[0] in [(pointX + 1), (pointX - 1), pointX]}
		#set of dots which are one row distant:
	LdistY = {dot for dot in dictionary.keys() if dot[1] in [(pointY + 1), (pointY - 1), pointY]}
	
	Lprox = LdistX.intersection(LdistY)
	
	dictionary[oripoint] = 1
	
	return len(Lprox)
def propagate2(mapcodeheightwidth,threshold,numiters):
	"""Propagation algorithm 2"""
	
	mapcode,height,width = mapcodeheightwidth
	
	# mapdode comes as a dictionary 'mapcode'	

	astrocount = 0

	print('Running mapcode experimental propagation algorithm... Looping ... ')
	
	Propagated_MAPCODE = deepcopy(mapcode)
	
	for a in range(numiters):
		for obj in mapcode.keys():
			for s in range(numiters):
				if random.random() > threshold:
					Propagated_MAPCODE[(obj[0]+random.randint(-1,1),obj[1]+random.randint(-1,1))] = 1
					astrocount += 1
				else:
					pass
		print( str(a) + ' ... ' )				
					
	print('Rounding algorithm running...')
	
	Rounded_MAPCODE = deepcopy(Propagated_MAPCODE) # initializes a new dictionary 
	
	for (x,y) in mapcode:
		if 6 >= neighbourCount((x,y), mapcode) >= 4:  # condition on the OLD dictionary
			for i in range(5):
				Rounded_MAPCODE[(x+random.randint(-1,1),y+random.randint(-1,1))] = 1	 # add to the NEW dictionary! otherwise...
	
	croppedRounded_MAPCODE = {pos : Rounded_MAPCODE[pos] for pos in Rounded_MAPCODE if pos[1] <= height and pos[0] <= width}
	
	print('\n ' + str(astrocount) + ' asteroids created!')
	return croppedRounded_MAPCODE
def propagate(mapcode,threshold,numiters):
	"""Propagation algorithm 1"""
	height,width = mapcode['_special'] 	#retrieves the data	
	del mapcode['_special']				#destroys the dict entry
	
	#now the mapcode has no special contents
	
	astrocount = 0
	
	newmapcode = deepcopy(mapcode)
	
	print('Running mapcode propagation algorithm... Looping')
	
	
		#for tupl in _ASTR:
		#ASTEROIDS[tupl[0]] = tupl[1]
		#---------------------------------------------------------------#
	for counter in range(numiters):
		for x in range(width):
			for y in range(height):	
				coords = (x,y)															#determines how many already existing asteroids there are close to (y,x	
				neighb = neighbourCount((x,y),newmapcode) 
				
				if mapcode.get(coords,0) == 1:
					pass					#there must be at least threshold neighbour(s)	LOWER BOUND															               
				elif neighb >= threshold:  #the more neighbours there are, the more probable it is that a new plot will be placed there
					if random.random() > (0.30 - neighb * 0.1): # 60% will create an asteroid							
						mapcode[coords] = 1							#update the mapcode with the new asteroid!
						astrocount += 1 
				else:
					pass
		sys.stdout.write('\n loop '+ str(counter + 1) +' \n')
		#---------------------------------------------------------------#
	
	
	print('\n ' + str(astrocount) + ' asteroids created!')
	
	
	mapcode['_special'] = (height,width)  #restores the special information string
	return mapcode
def pruneDestroyed(ListOfShipsOrFleet):
	"""Removes all destroyed ships from a listof ships or from a Fleet's shiplist, and possibly destroys them.
	If the fleet gets empty by doing this, removes the Fleet as well from its map.
	Also accepts mixed lists of ships and Fleets (such as those you get in map.OBJECTS' dictionary).
	"""
	newitemlist = []
	
	fleetlist = [ item for item in ListOfShipsOrFleet if isinstance(item,spaceship.Fleet) ]
	
	vessellist = [ item for item in ListOfShipsOrFleet if isinstance(item,spaceship.Vessel) ]
	
	alivevessellist = [ ship for ship in vessellist if ship.states['health'] != 'destroyed' ]
	
	alivefleetlist = [fleet for fleet in fleetlist if fleet.states['health'] != 'destroyed' ]
	
	newitemlist = alivevessellist + alivefleetlist
			
	return newitemlist
def findfactor(dimension,number):
	"""Returns how many times number is in dimension."""
	
	number = sqrt(number ** 2)
	counter = 0	
	while dimension < number:
		number -= dimension
		counter += 1
			
	return counter	
def distance(obj1,obj2):
	"""
	As general as possible, returns the distance between two objects on the map.
	Possibly, even the distance between an object and any tuple of coordinates.
	"""
	
	# transform obj1 and obj2 into tuples
	
	def redef(obj):
		if isinstance(obj,spaceship.Vessel) == True or isinstance(obj,spaceship.Fleet) == True or isinstance(obj,Building) == True:
			return obj.states['position']	
		elif isinstance(obj1,tuple):
			return obj
		
	obj1 = redef(obj1)
	obj2 = redef(obj2)	
	
	diffX = max(obj1[0],obj2[0]) - min(obj1[0],obj2[0])
	diffY = max(obj1[1],obj2[1]) - min(obj1[1],obj2[1])
	
	dist = int(sqrt(diffX ** 2 + diffY ** 2)) # pitagora
	return dist

class Map(object):
	"""Map space! The base grid where everything takes place."""
	def __init__(self,asteroidfield=None):
		"""Takes a matrix of 0s and 1s as input."""

		if asteroidfield == None:
			print('No asteroid field here! The space is too uninterestingly empty to live here. Moving elsewhere...')
			asteroidfield = Asteroid_Field(self)
		else:
			pass

		asteroidfield.GROUNDMAP = self
		
		self.asteroidfield = asteroidfield
		self.width = self.asteroidfield.width
		self.height = self.asteroidfield.height
		
		self.TRACKER = set()  # will hold a SET of objects: the ships which the map has to keep track of
		
		self.OBJECTS = {} # keeps track of how many Fleet,Vessel objects there are on the map, their positions and their keys. 
		                  # format = '(x,y) : [listofobjects]' 
		                  #		OBJECTS will hold vessels and fleets
		                  #
		                  #		body will hold asteroids (1s) and buildings
		                  #
		self.BUILDINGS = {} #will take care of buildings
							
		
		print('|| Map object created. Welcome to sector ' + self.asteroidfield.name + '.')
		return None
	
	def __repr__(self):
		return 'Map object; welcome to sector ' + self.asteroidfield.name + '.' 
		
	def resetMap(self):
		"""Builds a completely new map, and propagates it."""
		print('Preparing to build and propagate the new map...')
		
		newField = Asteroid_Field(self)
		
		self.asteroidfield = newField
		
		self.parse(True,True)
		return None
		
	def whatAt(self,xy):
		"""Returns what's written at coords(x,y)"""
		
		ifObj = self.OBJECTS.get( xy , 'Nothing here; just deep space.')
		string = repr(self.body.get( xy , ifObj ))
		
		return string
		
	def printCoords(self,something):
		"""Cycles through the existing building and checks whether there is one that matches the object given as 'something'."""
		for building in builtItems:
			if something != building:
				pass
			else:
				return building.printCoords

		return None
	
	@property
	def updateOBJECTS(self):
		"""REFRESH the objects dictionary and place there all position : shiplists for ships and fleets in TRACKER"""
		
		self.OBJECTS.clear() # erase
		self.TRACKER = set(pruneDestroyed(self.TRACKER)) ## PRUNING goes on here! All destroyed objects are not going to be mapped
														 ## will not track destroyed objects; thus, it won't display them.												 
		for fleetOrVessel in self.TRACKER: 
			objPos = fleetOrVessel.states['position']
			
			if objPos in self.OBJECTS:
				self.OBJECTS[objPos] = self.OBJECTS[objPos] + [fleetOrVessel]
			else:
				self.OBJECTS[objPos] = [fleetOrVessel]
		return None

	@property
	def brutal_dump(self):
		"""Displays in the shell the map itself."""
	
		self.updateOBJECTS 	# REFRESH the objects dictionary and place there all position : shiplists for ships and fleets in TRACKER
		
		self.torusize
		   	
		self.updateOBJECTS 	## HORRIBLE but how to fix it?
		height,width = self.asteroidfield.height, self.asteroidfield.width	#retrieves the data
		
								# picks the code of the FIRST ship in the list! else: it's an 'X'
		listObj = {coords : self.OBJECTS[coords][0].states.get(('code'), 'X') for coords in self.OBJECTS.keys()}
								
								# for each coordinate where there is a ship/vessel object, now there is a code.
		
		for key in listObj:    # Fleets are given 'code' priority.
			for obj in self.OBJECTS[key]:
				if isinstance(obj,spaceship.Fleet):
					listObj[key] = 'O'
				else:
					pass
		
		print('brutal_dump of self_body')
		halfspace = int(((width -3) / 2))
		print('     '+ halfspace * '-' + self.asteroidfield.name + halfspace * '-'  )
		for y in range(height +1):
			line = '     |'
			for x in range(width +1):
				#### important : tries to retrieve fleet or vessel; if fails it tries to retrieve building; final resort = asteroid. else: space.
				
				XY = (x,y)
				
				_letterSpace = listObj.get(XY, self.BUILDINGS.get(XY , self.asteroidfield.plots.get( XY , ' ' ) ) ) ### fundamental. Defines the layers
				#               (1)ships/Fleets            (2)Buildings					(3) 1s
				
				line = line + str(_letterSpace)
		
			print(line + ' - ' + str(y))
		
		print('      '+(width + 2) * '-')
		return None
	
	
	def addToTracker(self,objectS):
		"""
		Takes as input a vessel or a ship, and updates its registries.
		
		1) Checks if it was already somewhere. If so, it deletes its previous position.
		
		2) Retrieves the current position and updates the self.OBJECTS tracker.
		
		Needless to say, this is pretty useless if you use brutal_dump.
		
		"""
		
		if isinstance(objectS,spaceship.Fleet) == True or isinstance(objectS,spaceship.Vessel) == True:
			
			self.TRACKER.add(objectS)   # adds itself to the set, if not yet present.
					
		else: #isinstance(ObjectS,Building):
			# buildings are displayed at creation, and should need no update. But, could be changed.
			return None
			
		return None	
	def parse(self,asteroids = False,DUMP = False):
		"""Reads the asteroid_field, reads the ship and fleet registries and produces an updated map.
		Will take care of objects which have moved or have been placed outside of the edges of the map, by making it a torus."""
		
		print('Parsing Fleets and Vessels layer...')
	
		self.torusize
				
		if asteroids == True:
			print('Parsing Asteroids layer...')
				
			#self.torusize
		else:
			pass	
		
		if DUMP == True:
			self.brutal_dump
		else:
			pass
		
		return None
		
	@property	
	def torusize(self):
		"""
		Iterates through all the ships, vessels and whatever has a warp 
		method and orders to the object corresponding to the position to
		warp at some new position inside of the MAP. Acts on TRACKER! All ships.
		"""
		
		# let's try...
		
		shipsWithoutFleet = [vessel for vessel in self.TRACKER if vessel.states.get('fleet',False) == None ]

		for ship in shipsWithoutFleet:
			shipX,shipY = ship.states['position']
			if shipX > self.width or shipY > self.height:
				factorY = findfactor(self.height,shipY)  	#will be 0 if ship is in Y range
				factorX = findfactor(self.width,shipX)		#same for X
				newX , newY = int(sqrt(shipX ** 2) - self.width*factorX) , int(sqrt(shipY ** 2) - self.height*factorY)		
				ship.warp((newX , newY))
				print('Torusize algorithm... Warping one ship.')
			else:
				pass
		
		for fleet in [ fleet for fleet in self.TRACKER if isinstance(fleet,spaceship.Fleet) == True ]:
			shipX,shipY = fleet.states['position']
			if shipX > self.width or shipY > self.height:
				factorY = findfactor(self.height,shipY)  	#will be 0 if ship is in Y range
				factorX = findfactor(self.width,shipX)		#same for X
				newX , newY = int(sqrt(shipX ** 2) - self.width*factorX) , int(sqrt(shipY ** 2) - self.height*factorY)		
				fleet.warp((newX , newY))
				print('Torusize algorithm... Warping one Fleet.')
			else:
				pass
		
		return None

class Asteroid_Field(object):
	"""Asteroid spacefield. Can be built upon. Is a dictionary. By means of letters, it will display Building objects."""
	
	existing_Asteroids = []
	
	def __init__(self,height=90,width=75,asteroidratio=0.01,thres=0.3,numIters=3):
		"""Generator."""	
		#takes as input a mapcode object, and turns it into an asteroid field
		
		#initialized completely 1s:
		self.plots = propagate2(createMapCode(height,width,asteroidratio),thres,numIters)
		self.name = namegen.newname('a')
		
		self.height = height
		self.width = width
		self.asteroidratio = asteroidratio
		self.threshold = thres
		self.numIters = numIters
		
		
		print('|| ' + self.name +' Asteroid field object created; '  + str(len(self.plots.keys())) + ' squares of astral rubbish parsed.')
	
	def __str__(self):
		return str(self.plots)
		
	def __repr__(self):
		return 'Asteroid field.' + self.name +' : ' + str(len(self.plots.keys())) + ' squares of astral rubbish.'
	
	@property
	def baseMap(self):
		return self.plots

	def boolBuildable(self,coord):
		if self.plots[coord] == 1:
			return True
		else:
			return False

	def clearPlot(self,coord):
		"""Turns one plot in plain asteroid field."""
		self.plots[coord] = 1	
		return None

	def destroyPlot(self,coord):
		"""Makes one plot empty space."""
		del self.plots[coord]
		return None
	
	def randomPlot(self):
		plotcoordslist = [coords for coords in self.plots]
		return random.choice( plotcoordslist )
	
	@property
	def resetPlots(self):
		if str(input('Are you sure?')) in 'Yesyes':
			self.plots = propagate2(createMapCode)
			self.MAP
			self.plots = dict(coordinatesDict)       #only accept dictionary!
		else:
			return 'Ok.'
		return 'Done.'
	
	def put(self,building):
		"""Places a building into itself. _Force!_"""
		self.plots[building.pos] = building.states['code']				#updates its 'plots' dictionary
		self.GROUNDMAP.BUILDINGS[building.pos] = building.states['code']		#updates the GROUNDMAP dictionary
		#self.baseMap.body
		return None
	
	@property	
	def propagateMapcode(self):
		"""Tells the asteroidfield to re-parse and propagate its own mapcode."""
		
		newmpcd = propagate2(createMapCode(self.height, self.width, self.asteroidratio),self.threshold,self.numIters,(self.width,self.height))
		self.plots = newmpcd
		
		self.GROUNDMAP.parse   #tells the groundmap to update its registries and reprint it all
		
		print('New mapcode created, parsed and propagated!')
		
		return None
	
class Building(object):
	"""Building object. Can be put on asteroids."""
	
	global building_counter
	building_counter = {elem : 0 for elem in buildingsDB.keys()} 
	
	def __init__(self,className,AsteroidField,faction = None,coordinates=None):
		"""Creates the building and places it on an asteroid."""
		
		if className not in buildingsDB.keys():
			raise MapMethodsValueError('Invalid Class_Name, aborting.')
			print('Invalid Class_Name, aborting.')
			return None
			
		_defence,_attack,_shields,_cost,_special_attrs = buildingsDB[className] # retrieves data
	
		if building_counter[className] >= _cost[1]: ## maxLimit
			print("Maximum number of " + className + 's reached. Aborting.')
			return None
		
		if coordinates == None:
			coordinates = AsteroidField.randomPlot()
		
		self.states = {}

		self.states = { 'building_type' : className,
						'health' : 'intact',
						'code' : _special_attrs.split(',')[0],
						'special_attributes' : _special_attrs.split(',')[1:],
						'cost' : _cost[0],
						'hull_integrity': _defence ** 2,
						'shields' : _shields,
						'faction' : faction,
						'defence' : _defence,
						'attack' : _attack, # is either a tuple (attack,range) or None
						'obj_class' : 'building',
						'position' : coordinates } #to begin with
		

		self.asteroidfield = AsteroidField
		
		existing_Buildings.append(self)   
		
		AsteroidField.put(self)		## replaces the 1 in the asteroid field with its code 	##

		if AsteroidField.plots[self.states['position']] != self.states['code']:
			return 'unsuccessful'
			if AsteroidField.GROUNDMAP.BUILDINGS[self.states['position']] != self.states['code']:
				return 'unsuccessful'
			else:
				pass
		else:
			pass
		
		return None

		
	def __repr__(self):
		return 'Building object {0}; code: {1}; \n         located in {2} at {3}'.format(self.states['building_type'],self.states['code'], self.asteroidfield.name,self.pos)
	
	def spawn(self,faction=None, ship_Fleet_orShiplist=None):
		"""Makes the building spawn on himself some vessel, fleet or shiplist."""
		
		if self.states['special_attributes'][0] in ['spawn1','spawn2','spawn3','spawn4']:			
			pass
		else:
			return 'This building cannot spawn vessels.'
		
		if faction != self.states['faction']:
			return 'This faction cannot build from this building.'
		else:
			pass
		
		if faction == None:
			faction = input('What faction? (1) : ')
		else:
			pass
			
		if True == input('Do you want to initialize a fleet? [True/False] : '):
			a = spaceship.Fleet(self.asteroidfield.GROUNDMAP, None,None, self.states['position']) # initializes the fleet creation procedure
		
		else:
			shipclass = input('Do you want to initialize a ship? [ship_class/False] : ')
			if shipclass == False:
				return None
			else:
				a = spaceship.Vessel(shipclass, self.asteroidfield.GROUNDMAP, self.states['position'])

		return a
		
	
	@property
	def pos(self):
		return self.states['position']




