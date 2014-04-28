#factionmethods

import namegen
import spaceship
import mapmethods
import routinemethods
import itertools
import collector


existing_Factions = []

def printOptions(dictionary = None, keyword = None, player = None):
	"""Displays nicely some indexed options."""
	
	if dictionary == None:
		dictionary = {}
		dictionary[0] = ('Next_turn', routinemethods.nextTurn)
		dictionary[1] = ('Existing_Vessels', spaceship.existing_Ships)
		dictionary[2] = ('Existing_Fleets', spaceship.existing_Fleets)
		dictionary[3] = ('Existing_Factions', existing_Factions)
		dictionary[98] = ('Command_Center', 	None	)
		dictionary[99] = ('Options',        	None	)
		dictionary[991] = ('Quit interactive menu', None)

	for key in dictionary:
		print('    >' , '(',key,')' , ' '*5 , dictionary[key][0])
	
	choice = input('Which option do you choose? Enter a plain number. ')
	try:
		choice = int(choice)
	except ValueError:
		pass

	while dictionary.get(choice,None) == None or isinstance(choice,int) == False or choice == '': # waits for a correct input
		print('choice is ' + str(choice))
		print('and choice is in dict == ' + str(choice in dictionary))
		print(str(dictionary.keys()))
		choice = input('Wrong input. Available options are: ' + str(dictionary.keys()) + ' : ')
		try:
			choice = int(choice)
		except ValueError:
			pass
			
	result = dictionary[choice][1] # the function or method
	
	if isinstance(result,list):
		counter = 0
		optionsDict = {}
		
		while counter < len(result):
			optionsDict[counter] = (repr(result[counter]) , result[counter])
			counter += 1
			
		printOptions(optionsDict,keyword,player) # lets you choose between the elements of the list
	
	elif isinstance(result,spaceship.Vessel):
		optionsdict = result.VesselChoiceDict() # retrieves the vessel's dictionary
		print(repr(result) + result.stateSum() + ' selected: ')
		printOptions( optionsdict ,keyword,player)
	
	elif isinstance(result,spaceship.Fleet):
		if keyword == 'fleetpick':
			return result # returns the picked fleet
		print(repr(result) + ' selected: ')	
		printOptions(result.FleetChoiceDict(),keyword,player)
		
	elif isinstance(result,mapmethods.Building):
		print(repr(result) + ' selected: ')	
		printOptions(result.BuildingChoiceDict(),keyword,player)
		
	elif isinstance(result, Faction):
		print(repr(result) + ' selected: ')	
		printOptions(result.FactionChoiceDict(),keyword,player)
		
		
		# special menu voices
		
	elif choice == 98:
		print('Not yet implemented')
		# will display mass strategic orders
		#printOptions(Command_Center)
		
	elif choice == 99:
		# will display options for save, load, etc...
		return printOptions({	0 : ('Switch pov', pickAFaction(keyword)),
								1 : ('New Player', Faction(collector.Mainmap))
								#2 : ('Create object', objectCreator())
								},keyword,player)
		
	elif choice == 991:
		# DEBUG hidden function: exits the interactive menu
		return None
		
	else: # parses the order contained in the dictionary <== The base level of the choice has been reached
		try:
			result()
			pass
		except TypeError:
			result
			pass
		collector.Mainmap.brutal_dump
		print('Order executed.')
		
	return printOptions(None,keyword,player)
		
		
def pickAFaction(keyword):
	choicedict = {}
	counter = 0
	for faction in existing_Factions:
		choicedict[counter] = (repr(faction), printOptions(None,keyword,faction))
		counter += 1
		
	return printOptions(choicedict,keyword)


class Faction():
	"""Each player will be in a faction. The faction you belong (you 
	channel your orders through) determines where you can spawn your ships
	and which ships and fleets you can move.
	It will also determine how much of the map you can see."""
	
	def __init__(self,MAP,name=None):
		"""Initializes a new faction"""
		
		if name == None:
			name = namegen.newFactionName()
				#name = input('Enter the name of your faction: ')
		else:
			pass
			
		self.name = name
		
		self.GROUNDMAP = MAP
		
		self.BUILDINGS = []
		
		self.SHIPS = []
		
		self.FLEETS = []
		
		#building init == __init__(self,className,AsteroidField,faction,coordinates=None):
		self.BASE = mapmethods.Building('base',self.GROUNDMAP.asteroidfield,self)
		
		self.ALL = [self.name,self.BASE,self.SHIPS,self.FLEETS,self.BUILDINGS,self.GROUNDMAP]

		self.states = {'energy' : 5,
						'points' : 0,
						'runtime' : 0,
						'rank' : 'nullity',
						'charfunction' : self.ALL }
		
		existing_Factions.extend([self])
		
		self.begin()
		return None

	def __str__(self):
		return str(self.states)
		
	def __repr__(self):
		return 'Faction ' + self.name		
		
	def begin(self):
		"""Each player starts with a mothership, a couple of fighters and a base building."""
		print('Initializing player '+self.name )

		newFleet = spaceship.Fleet(self.GROUNDMAP,'Odins',('fighter','fighter','fighter','mothership'),self.BASE.states['position'])
		self.FLEETS.extend([newFleet])
		for ship in newFleet.states['shiplist']:
			self.SHIPS.extend([ship])
		
		return None
		
	def build(self,buildingname = None, position = None):
		"""Guided procedure to initialize a building object."""
		
		asteroidfield = self.GROUNDMAP.asteroidfield
		if position == None:
			position = random.choice(self.GROUNDMAP.asteroidfield.plots)
			#position = input('Enter the position at which you want to initialize the building here [(x,y)] : ')
			# You won't just be able to place it anywhere though.
		else:
			pass
			
		if buildingname == None:
			buildingname = input('Enter the nametype of the building: ')
		
		#costofBuilding IMPLEMENT
		
		building = mapmethods.Building(buildingname,asteroidfield,self,position)
		
		self.BUILDINGS.extend([building])
		return None

	def assign(self,obj):
		"""Assigns to himself a fleet, building or vessel object."""
		if isinstance(obj,spaceship.Vessel):
			self.SHIPS.extend([obj])
			obj.states['faction'] = self
		elif isinstance(obj,spaceship.Fleet):
			self.FLEETS.extend([obj])
			obj.states['faction'] = self
		elif isinstance(obj,mapmethods.Building):
			
			if obj.states['faction'] == self:
				return None
			else:
				obj.states['faction'] = self
			self.BUILDINGS.extend([obj])	
			
		else:
			raise ValueError('Cannot assign ' + str(obj) +'  object to ',str(self))
		
		
	def launch(self,building = None, classname = None):
		"""Guided procedure to initialize a ship object, or a fleet."""
		
		print('Launching procedure initialized...')
		
		CANBUILD = [ 'spawn1', 'spawn2', 'spawn3', 'spawn4' ]
		
		if building == None:
			#building = printOptions(input('Which building do you want to launch from? [index]: '),{ self.buildings.index(building) : building for building in self.BUILDINGS if building.states['special_attributes'] in CANBUILD} )
			pass
		else:
			pass
		#building = self.BUILDINGS[input('Which building do you want to launch from? [index]: ')]
		
		if building == 'here':
			spaceship.Fleet(self.GROUNDMAP,None,None,building.states['position']) 
		else:
			pass
		
		if classname == None:
			classname = input('Of which class?')
		else:  # def __init__(self,GROUNDMAP,name = None, fleet=None, position=None):
			spaceship.Fleet( self.GROUNDMAP, newname('a') ,classname, building.states['position'])

		return None

	def FactionChoiceDict(self):
		"""Defines the options available to a faction."""
		
		optionsdict = {		0 : ('Flag_as_hostile', 0),
							1 : ('Flag_as_friendly', 0),
							2 : ('Diplomacy',0),   # bribe, commerce, sign contracts-pacts...
							3 : ('Subterfuges',0), # send spies, bounty hunters, sabotage...
							4 : ('Sign_surrender',0) # lose the game, but with honour.
							}	
	
		return optionsdict




