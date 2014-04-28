from populatedatabases import attackMultipliersDB, attackModifiersDB, disablingAttackConditionsDB
from populatedatabases import buildingsDB,disablingVisibilityConditionsDB,speedMultipliersDB,spaceshipDB
from diceset import d as roll
from math import sqrt as sqrt
from namegen import newname as newname
from savemethods import populateObjectUniverse,loadFromFile,writeToFile
import mapmethods
import string,random,copy

existing_Objects = []  # for the savefile! keeps track of all created and destroyed items.
existing_Fleets = []
existing_Ships = []

class VesselMethodsError(ValueError):
	pass

#turnCounter = 0        # will keep track of turns


def attackables(listOfPlayers):
	return [z for z in (listOfPlayers) if z.states['can_be_attacked'] == True]	 
def can_attack(listOfPlayers):
	return [z for z in (listOfPlayers) if z.states['can_attack'] == True]	
def randomizeFleet(listx):
	randomFleet = random.sample(listx,len(listx))
	return randomFleet
def somebodyActive(listofships):
	for a in displayHealthState(listofships):
		if a != 'destroyed':
			return True
		else:
			pass
	return False
def onlyNotDestroyedPlayers(listOfPlayers): #updates dynamically!
	return [a for a in listOfPlayers if a.states['health'] != 'destroyed']
def generalizedBattle(FleetA, FleetB):
	"""attackers and defenders must be Fleet objects. Battle is resolved in turns. Some randomization goes on."""
	
	NotInRangeA = [ z for z in FleetA.states['shiplist'] if z.checkRange(FleetB.states['position']) == False ] 	# those who can not fire from A
	NotInRangeB = [ z for z in FleetB.states['shiplist'] if z.checkRange(FleetA.states['position']) == False ] 	# those who can not fire from B
	
	notinrangeShips = NotInRangeA + NotInRangeB
	
	if NotInRangeA + NotInRangeB == FleetA.states['shiplist'] + FleetB.states['shiplist'] or NotInRangeA == FleetA.states['shiplist']:
		print("The fleets are too far away to kill each other efficiently.")
		return None
	
	nameA= FleetA.states['name']
	nameB= FleetB.states['name']
	
	# ---------------------- UTILITY FUNCTIONS ------------------------- #
	
	def battlingPlayers(listOfPlayers): #the players which are either attackable or able to attack
		return [player for player in set(set(can_attack(listOfPlayers)).union(set(attackables(listOfPlayers)))).difference(set(notinrangeShips))]
	
	oriFleetA = copy.deepcopy(FleetA)
	oriFleetB = copy.deepcopy(FleetB)	
	
	if isinstance(FleetA,Fleet):
		FleetA = FleetA.shiplist   # redefines FleetA, FleetB to be their shiplists: it's them who will fight.
	else:
		pass
	
	if isinstance(FleetB,Fleet):
		FleetB = FleetB.shiplist 
	else:
		pass	
				
	def checkstate(v=False):
		"""Checks all the disabling conditions for the fight to go on."""
		finalNoOfShips = len(onlyNotDestroyedPlayers(FleetA)) + len(onlyNotDestroyedPlayers(FleetB))
		deathcount = initialNoOfShips - finalNoOfShips
		if v == True:
			if onlyNotDestroyedPlayers(FleetA) == [] and onlyNotDestroyedPlayers(FleetB) == []:
				print('What a gruesome battle! The teams have annichilated each other! Deathcount = ' + str(deathcount))
				return False
			elif onlyNotDestroyedPlayers(FleetA) == [] and onlyNotDestroyedPlayers(FleetB) != []:
				print('The battle is over: the attackers lost and were annichilated. Deathcount = ' + str(deathcount) + ' The leftovers of the defenders are:\n ' + repr(onlyNotDestroyedPlayers(FleetB)))
				return False
			elif onlyNotDestroyedPlayers(FleetA) != [] and onlyNotDestroyedPlayers(FleetB) == []:
				print('The battle is over: the defenders lost and were annichilated. Deathcount = ' + str(deathcount) + '. The leftovers of the attackers are:\n ' + repr(onlyNotDestroyedPlayers(FleetA)))
				return False
			elif battlingPlayers(FleetA) == [] and battlingPlayers(FleetB) == []:
				print('The teams are unable to continue with the fight. Deathcount = ' + str(deathcount))
				return False
			elif can_attack(FleetA) + can_attack(FleetB) == []:
				print('The teams are unable to continue with the fight. Deathcount = ' + str(deathcount))
				return False
			else:
				return True
		else:
			if onlyNotDestroyedPlayers(FleetA) == [] and onlyNotDestroyedPlayers(FleetB) == []:
				return False
			elif onlyNotDestroyedPlayers(FleetA) == [] and onlyNotDestroyedPlayers(FleetB) != []:
				return False
			elif onlyNotDestroyedPlayers(FleetA) != [] and onlyNotDestroyedPlayers(FleetB) == []:
				return False
			elif battlingPlayers(FleetA) == [] and battlingPlayers(FleetB) == []:
				return False
			elif can_attack(FleetA) + can_attack(FleetB) == []:
				return False
			else:
				return True
		
	#-----------------------------------------------------------------------------------------------------#
	
	FleetA = onlyNotDestroyedPlayers(FleetA)  # prunes already destroyed players # oneday will be useless
	FleetB = onlyNotDestroyedPlayers(FleetB)
	
	initialNoOfShips = len(FleetA) + len(FleetB)
	
	FleetA = list(FleetA)
	FleetB = list(FleetB)
	
	FleetA = randomizeFleet(onlyNotDestroyedPlayers(FleetA)) #only keeps nondestroyed players
	FleetB = randomizeFleet(onlyNotDestroyedPlayers(FleetB)) #and randomizes the sequence
	
	#these lists will update dynamically! If a player is destroyed, the list does not include it anymore.
	attackersA = [player for player in FleetA if player.states['can_attack'] == True and player not in notinrangeShips ]  		#those in A who can attack
	attackersB = [player for player in FleetB if player.states['can_attack'] == True and player not in notinrangeShips ]			#those in B who can attack
	defendersB = [player for player in FleetB if player.states['can_be_attacked'] == True and player not in notinrangeShips ]		#those in B who can defend
	defendersA = [player for player in FleetA if player.states['can_be_attacked'] == True and player not in notinrangeShips ]		#those in A who can defend

			#terminates when either coalition is totally destroyed, or has no player able to inflict or receive damage
	while  checkstate() == True: 

		if attackables(defendersB) != [] and can_attack(attackersA) != []: #all attackers attack some defender
			print('The attacking fleet fires...')
			for ship in can_attack(attackersA):
				ship.attack(random.choice(attackables(defendersB)))
				
				if checkstate() == False:   ####
					break  # Ends the routine if this is not passed!
				else:
					pass
		
		elif attackables(defendersB) != []:
			print("The " + nameA + " fleet cannot attack, because " + nameB + ' has no attackable players.')
			pass
		elif can_attack(attackersA) == []:
			print("The " + nameA + " fleet cannot attack! No ship is able to fire.")
			pass
		else:
			print('This round nothing happened... The few survivors of the battle are staring at each other.')
			pass
			
		if checkstate() == False:   ####
			break
		else:
			pass
		
		if  attackables(defendersA) != [] and can_attack(attackersB) != []: #all defenders attack some attacker
			print('The enemy fleet fires back...')
			for ship in can_attack(attackersB):
				ship.attack(random.choice(attackables(defendersA)))
				
				if checkstate() == False:   ####
					break # Ends the routine if this is not passed!
				else:
					pass
				
		elif attackables(defendersA) != []:
			print("The " + nameB + " fleet cannot attack, because " + nameA + ' has no attackable players.')
			pass
		elif can_attack(attackersB) == []:
			print("The " + nameB + " fleet cannot attack! No ship is able to fire.")
			pass
		else:
			print('This round nothing happened... The few survivors of the battle are staring at each other.')
			pass
	
	
	checkstate(True) # prints the most appropriate outcome.
	return None	
def displayHealthState(listofships):
	ships_states = []
	for ship in listofships:
		if ship.states['hull_integrity'] > -10:
			hull = ': ' + str(ship.states['hull_integrity'])
		else: 
			hull = ''
		ship.assessHealth
		ships_states.append(ship.states['health'] + hull)
	return ships_states
def existing_all():
	return existing_Objects + existing_Fleets + existing_Ships
def save(name=None):
	"""Saves the game."""
	for i in existing_Ships:
		i.updateStates 	# updates all existing ship's states
						# this should also eliminate 'destroyed' ships...
	
	list_serial_1 = [ship.states for ship in existing_Ships if ship.states['health'] != 'destroyed']      	#WARNING! will be a list of DICTs
	
	for Fleet in existing_Fleets:        # adds nondestroyed Fleets to serial list 1
		if onlyNotDestroyedPlayers(Fleet.states['shiplist']) != []:
			list_serial_1 = list_serial_1 + [Fleet]    	# Fleet _is_ a dictionary!
															#and list_serial_1 is a _list of dictionaries_.

	list_serial_2 = [objecT.states for objecT in existing_Objects if objecT.states['health'] != 'destroyed']
	
	ContentsToSave = (list_serial_1,list_serial_2)       # TUPLE
	
	#for o in existing_Objects:
	#	o.updateStates
	
	print('Saving Game...')
	savemethods.writeToFile(ContentsToSave, name)
	print('Game saved!')
	return None
def load(filename=None):
	FILE_BUFFER = savemethods.loadFromFile(filename)
	return savemethods.populateObjectUniverse(FILE_BUFFER)
def generalizedMove(listOfShips,direction=None,distance=None):
	"""
	Moves each ship up to its own top speed in one direction between NO, SE, NE, SO.
	works even if they are distant from one another, or in a fleet! Currently clashes with fleet movement.
	"""		
	
	if direction == None:
		direction = input('Enter the direction: must be maximum two of [l,r,u,d]: ')
	else:
		pass
		
	if distance == None:
		distance = input('Enter the speed you want to move: cap is the speed of the ship(s): ')
		
	else:
		pass	
	
	for ship in listOfShips:
		if ship.states['current_speed'] <= 0:
			pass
		else:
			ship.updateStates  # to make sure the speed is up to date...
			oldpos = ship.states['position']
			distance = int(min(distance, ship.states['current_speed']))    # cap, and makes it an integer rounded down
						
			if 'l' in direction:
				if 'u' in direction:
					newpos = ( (oldpos[0] - int(distance* 0.7) ),( oldpos[1] - int(distance* 0.7) ) ) 
				elif 'd' in direction:
					newpos = ( (oldpos[0] - int(distance* 0.7) ),( oldpos[1] + int(distance* 0.7) ) ) 				
				else: # if only L:
					newpos = ( oldpos[0] - distance , oldpos[1] ) 
			
			elif 'r' in direction:
				if 'u' in direction:
					newpos = ( (oldpos[0] + int(distance* 0.7) ),( oldpos[1] - int(distance* 0.7) ) ) 
				elif 'd' in direction:
					newpos = ( (oldpos[0] + int(distance* 0.7) ),( oldpos[1] + int(distance* 0.7) ) ) 				
				else: # if only R:
					newpos = ( oldpos[0] + distance , oldpos[1] ) 

			elif 'd' in direction:
				newpos = ( oldpos[0]  , oldpos[1] + distance) 
			
			elif 'u' in direction:		
				newpos = ( oldpos[0]  , oldpos[1] - distance) 
			
			else:
				print('Something went wrong. Bad input.')
				return generalizedMove(listOfShips,None,None)
	
		ship.states['position'] = newpos
		ship.GROUNDMAP.addToTracker(self)
				
	return None		
def sortByPower(listofships):
	"""Orders a list of ships from the most powerful to the least. 
	Can parse list of arbitrary objects. Those which are not ships are pushed at the end.
	If there is a fleet, the fleet comes first."""
	newlist = []
	for elem in listofships:
		newlist = newlist + [maxpow(listofships)]
	return newlist
def maxpow(listofships):
	"""Returns the most powerful ship of a list of ships."""
	ldic = {ship:spaceshipDB[ship.states['ship_class']][1] for ship in listofships}
	upperbound = [ship for ship in ldic if ldic[ship] == max(ldic.values()) ]   #all maximal power ships
	return upperbound.pop
									
class Vessel(object):
	"""All spaceships are objects of this class."""
	
	def __init__(self,subClass,MAP=None,coords=(0,0)):
		"""Creates a spaceship of the class 'subClass', e.g. 'fighter', by default at (0,0)."""

		topspeed, maxpower, armor, shields, rangeE,warp,specialattrs = spaceshipDB[subClass]
		
		if MAP == None or isinstance(MAP,mapmethods.Map) == False:
			raise MapMethodsValueError('Bad input for the Map parameter when initializing Vessel Object. Aborting...')
			return None
		else:
			pass		
		
		self.GROUNDMAP = MAP # a special attribute; the reference GROUNDMAP
		
		self.states = 	{ 'obj_class' :'ship',
						'ship_class' : subClass,
						'name' : newname(),
						'code' : specialattrs[0],
						'top_speed' : topspeed,
						'shields' : shields,
						'armor' : armor,
						'range' : rangeE,
						'fleet' : None,   # by default, it is in no fleet.
						'max_power' : maxpower,
						'warp' : warp,
						'health' : 'intact',
						'faction' : None, # will be replaced by a string, corresponding to Faction.name
						'current_speed' : 0,
						'hull_integrity': armor ** 2 ,
						'max_hull_integrity': armor ** 2	,
						'cargo': None,
						'position': coords }
						
		self.updateStates
		
		existing_Ships.extend([self])
		
		self.GROUNDMAP.addToTracker(self)
		
		print('|| '+repr(self) + ' was created.')
		return None 

	def __str__(self):
		return str(self.states)
	
	def __repr__(self):
		representation = "{0} {1}".format(self.states['ship_class'], self.states['name'])
		return representation
	
	@property
	def health(self):
		print(self.assessHealth, self.states['hull_integrity'])
		return self.assessHealth

	@property
	def updateStates(self):
		"""Should do a complete checkup and update everything."""
		self.assessHealth                          	#updates states[health] and states[hull_integrity]
		self.checkAttackProperties
		self.updateSpeedProperties	
		#check: if destroyed erase from existing_Ships
		return None


	@property
	def die(self):
		"""Makes a ship severely_damaged."""
		self.hullInt = -5
		self.updateStates
		return None
		
	def warp(self,xy = None, cheats = None):
		
		if cheats == 'override':
			pass
		elif self.states['warp'] == False:
			return None
				
		if xy == None:
			xy = input("Enter x and y coordinates for the warp, in this form: '(x,y)' ")
		self.states['position'] = xy
		print('Now '+ repr(self) + ' is at ' + str(xy))
		return None
	
	def destroy(self):
		"""Makes quickly a ship destroyed"""
		self.states['hull_integrity'] = -15
		self.states['fleet'] = None # if it was in a fleet, now it is no more.
		self.updateStates
		
		existing_Ships.remove(self)
		
		try:
			self.GROUNDMAP.TRACKER.remove(self)
		except KeyError:
			pass
		
		try:
			self.GROUNDMAP.OBJECTS[self.states['position']].remove(self)
		except KeyError:
			pass
		except ValueError:
			pass # the ship is already not there (FOR SOME REASON??)
		return None
		
	def repair(self):
		"""Restores a ship's health to its full hull capacity (max_hull_integrity)."""
		self.states['hull_integrity'] = self.states['armor'] ** 2 
		self.updateStates
		self.GROUNDMAP.TRACKER.add(self)
		
		try:
			self.GROUNDMAP.OBJECTS[self.states['position']].extend([self])
		except KeyError:
			self.GROUNDMAP.OBJECTS[self.states['position']] = [self]
		
		return None
		
	@property
	def movementSpeed(self):
		"""Actual movement speed is a function of the ship's own speed and its current speed_multipliers"""
		if speedMultipliersDB[self.states['health']] == False:
			return 0
		else:
			return (computeSpeedMultiplier(self) * self.states['max_speed'])
		return None
			
	@property
	def checkAttackProperties(self):
		"""If the attack multiplier is 0, the ship cannot attack."""
		#listattackconditions is a list of 3-tuples; ((str)state, (bool)canbeattacked ,(bool)canattack)
		
		toCheckStates = [i for i in self.states.keys() if self.states[i] == True] # list of the states which the ship has
		
		toCheckStates.append(self.states['health']) #adds also the health!
		
		attackPosConditions = {cond for cond in [a for a in attackMultipliersDB if attackMultipliersDB[a] == False]}
			
		attackabilityConditions = {cond for cond in [a for a in disablingAttackConditionsDB if disablingAttackConditionsDB[a] == False]}	
		
		if set(attackabilityConditions).intersection(set(toCheckStates)) == set():
			canBeAttacked = True
		else:
			canBeAttacked = False
			
		if 	set(attackPosConditions).intersection(set(toCheckStates)) == set():
			canAttack = True
		else:
			canAttack = False

		self.states['can_attack'] = canAttack
		self.states['can_be_attacked'] = canBeAttacked
		self.states['attack'] = self.computeAttackMultiplier * self.states['max_power']
		
		return None

	@property
	def attackValue(self):
		"""Returns the current attack power of the ship."""
		return roll(self.computeAttackMultiplier * self.states['max_power'])
		
	@property
	def name(self):
		return self.states['name']
		
	@property	
	def defenceValue(self):
		return (self.states['armor'])

	@property	
	def updateSpeedProperties(self):
		"""Computes its current_speed, which is a function of the health 
		and the maximum speed, plus (not yet implemented) environmental variables."""
		
		maxspeed = self.states['top_speed']
		speedfactor = speedMultipliersDB[self.states['health']]
		#extra_factors = speedMultipliersDB[self.states['']]  environmental...
		
		if speedfactor == False:
			curspeed = 0
		else:
			curspeed = maxspeed * speedfactor
			
		self.states['current_speed'] = curspeed
		return None

	def dealDamage(self,x):
		"""Inflicts some gratuitous pain."""
		self.states['hull_integrity'] = self.states['hull_integrity'] - x
		self.updateStates
	
	def stats(self):
		return (self.attackValue(), self.defenseValue())
		
	@property
	def assessHealth(self):
		life = self.states['hull_integrity']
		maxlife = self.states['max_hull_integrity']
		
		if life<=-10:
			healthState = 'destroyed'
		elif -10<life<=0:
			healthState = 'severely_damaged'
		elif 0< life <= (maxlife / 3):
			healthState = 'seriously_damaged'
		elif (maxlife / 3) < life <= ((2 * maxlife) / 3):
			healthState = 'damaged'
		elif ((2 * maxlife) / 3) < life < maxlife:
			healthState = 'lightly_damaged'
		elif life == maxlife:
			healthState = 'intact'
		
		self.states['health'] = healthState
		return healthState
	
	@property
	def computeAttackMultiplier(self):
		"""Sums all the modifiers to the attack of the ship in that moment."""
		attackMultiplier = 0      # the base is 0
		for required_state in attackMultipliersDB.keys():
			if required_state in self.states.keys() or required_state == self.states['health']:  # if the ship has that state, apply the modifier
				attackMultiplier = attackMultiplier + float(attackMultipliersDB[required_state])
			else:
				pass
		return float(attackMultiplier)
	
	@property
	def computeSpeedMultiplier(self):
		"""Sums all the modifiers to the attack of the ship in that moment."""
		speedMultiplier = 0      # the base is 0
		for required_state in speedMultipliersDB.keys():
			if required_state in self.states.keys() or required_state == self.states['health']: 						  # if the ship has that state, apply the modifier
				speedMultiplier = speedMultiplier + float(speedMultipliersDB[required_state])
			else:
				pass
		return speedMultiplier

	def checkRange(self,coordinatesOrShip):
		"""Returns Frue if coordinates are in range for firing; False otherwise."""
		if isinstance(coordinatesOrShip,Vessel) or isinstance(coordinatesOrShip,Fleet):
			coordinatesOrShip = coordinatesOrShip.states['position']
		elif isinstance(coordinatesOrShip, tuple) and len(coordinatesOrShip) == 2:
			if type(coordinatesOrShip[0]) != int or type(coordinatesOrShip[1]) != int or coordinatesOrShip[0] + coordinatesOrShip[1] > 1000:
				raise VesselMethodsError("Bad input for checkRange function. Should be a tuple of integers or an object with a 'position' state.")	
		else:
			raise VesselMethodsError("Bad input for checkRange function. Should be a tuple of integers or an object with a 'position' state.")	
		
		if self.states['range'] == None:
			dist = 0
		else:
			dist = mapmethods.distance(self,coordinatesOrShip)
		
		if dist <= self.states['range']:
			return True		
		else:
			return False
					
	def attack(self,enemy):
		"""Computes the damages of a battle. Should update the hullIntegrity and 
		'health' states of both accordingly."""
		
		if self is enemy:
			raise VesselMethodsError('SelfDestruct is not yet supported.')
		
		if self.checkDifferentFaction(enemy) != True:
			raise VesselMethodsError('Cannot attack ships of the same Faction.')
		
		if enemy == 'nearest':
			
			tempodict = {}
			
			for ship in existing_Ships:
				if self.checkDifferentFaction(ship) == True:
					dist_self_ship = mapmethods.distance(self,ship)
					tempodict[dist_self_ship] = ship
					
			vsl = tempodict[min(tempodict.keys())]
			enemy = vsl
		
		enemy.updateStates
		self.updateStates
		
		if self.checkRange(enemy.states['position']) == True:
			pass
		else:
			print('Enemy out of range.')
			return None
		
		if enemy.states['can_be_attacked'] == False:
			print("Enemy can't be attacked!")
			return None
		elif self.states['can_attack'] == False:
			print("This ship cannot attack!")
			return None
		else:
			if enemy.checkRange(self.states['position']) == True:
				enemy_damagedealt = enemy.attackValue
				pass
			else:
				enemy_damagedealt = 0
			
			
			self_damagedealt = self.attackValue
			
			self.states['hull_integrity'] = self.states['hull_integrity'] - enemy_damagedealt
			enemy.states['hull_integrity'] = enemy.states['hull_integrity'] - self_damagedealt
			
			enemy.updateStates
			self.updateStates
		
		if self_damagedealt == 0 and enemy_damagedealt == 0:
			print('No damage whatsoever!')
			return None
		elif self_damagedealt != 0 and enemy_damagedealt == 0:
			print('> ' + self.name + ' fires... Hit! ' + str(self_damagedealt) + ' damage to '+ enemy.name + ' which is now ' + enemy.states['health'])
			return None
		elif enemy_damagedealt != 0:
			print('> ' + self.name + ' Has been hit! ' + str(enemy_damagedealt) + ' damage to '+ enemy.name + ' which is now ' + self.states['health'])
			return None
		else:
			print('> ' + self.name + ' Hit! ' + str(self_damagedealt) + ' damage to '+ enemy.name + ' which is now ' + enemy.states['health'])
			print('          Enemy replied! ' + str(enemy_damagedealt) + ' damage to '+ self.name + ' which is now ' + self.states['health'])
			return None
	
	def checkDifferentFaction(self,otherObject):
		"""Returns true if the objects belong to hostile factions."""
		
		try:
			if otherObject.states['faction'] == self.states['faction'] and self.states['faction'] != None:
				# if they are of the same faction (and that is NOT None)
				return False
			else:
				return True

		except AttributeError:
			raise VesselMethodsError('The object cannot belong to any faction. Is it an asteroid maybe?')
			return None
	
	def assignToFleet(self, Fleet = None):
		
		if Fleet == None:
			
			if self.states['faction'] != None:
			
				Fleet = self.states['faction'].FLEETS[0] # picks the first one. TO FIX!
				Fleet.states['shiplist'].extend([self]) # adds himself to the shiplist all orders will now be redirected to the vessel. To implement : distance constraints!
				
			else:
				pass
		else:
			
			return None
				

	def attackToDeath(self,defender):
		"""Goes on attacking until either fighter is down."""
		
		if self is enemy:
			raise VesselMethodsError('SelfDestruct is not yet supported.')
			
		if self.checkDifferentFaction(enemy) != True:
			return 'Cannot attack ships of the same Faction'
			raise VesselMethodsError('Cannot attack ships of the same Faction.')
		
		if checkRange(self,enemy.states['position']) == True:
			pass
		else:
			return 'Cannot attack: out of range.'
		
		print(repr(self) + '  is defying  ' + repr(defender))
		self.updateStates
		defender.updateStates
		while self.states['can_attack'] == True and defender.states['can_be_attacked'] == True:
			
			self.attack(defender)
			
			self.updateStates #checks what has happened after the first attack round
			defender.updateStates
			
			if self.states['can_attack'] == False and defender.states['health'] == 'destroyed':
				print("The enemy is destroyed, but the attacker has been severely damaged!")
				return None
			elif self.states['can_attack'] == True and defender.states['health'] == 'destroyed':
				print("The enemy is destroyed! Victory!")
				return None
			elif self.states['can_attack'] == False and defender.states['health'] != 'destroyed':
				print("The enemy is too strong: the attacker is severely damaged! \n      The enemy counters!")
				return(defender.attackToDeath(self))
			else:
				pass
			
		return None
		
		
	def	VesselChoiceDict(self):
		"""Produces a dictionary of numbered options and bound methods; to make user-accessible giving orders to the ship."""
		
		counter = 0
		selfchoicedict = {}
		if self.states['can_attack'] == True: # attack
			
			selfchoicedict[counter] = ('Attack_nearest', self.attack)			
			counter += 1
		
		if self.states['warp'] == True: # warp
			 
			 selfchoicedict[counter] = ('Warp', self.warp)
			 counter += 1
		
		if self.states['health'] != 'destroyed':
			 
			 selfchoicedict[counter] = ('Self_destruction', self.destroy)
			 counter += 1			
		
		selfchoicedict[counter] = ('Add_to_fleet', self.pickaFleet)
		counter += 1
							
		return selfchoicedict
							
	def pickaFleet(self):
		"""Calls a printOptions function: displays all the faction's fleets (by name)
		and allows the user to choose one."""
		if self.states['faction'] == None:
			return 'Impossible. Some error underway.'

		return factionmethods.printOptions({oz.next() : fleet.name for fleet in self.states['faction'].FLEETS }, 'fleetpick')
		
	def stateSum(self):
		return ' stationed at ' + str(self.states['position']) + ', ' + self.states['health']


				
class Fleet(object):
	def __init__(self,GROUNDMAP,name = None, fleet=None, position=None):
		"""Input a MAP object, a classname, a tuple of (classnames of) ships and outputs a fleet. 
		E.g.: Fleet('Gargoyles',('fighter','fighter','destroyer'))"""
		
		####### Guided initialization procedure
		if name == None:
			name = str(input('Enter the name of the Fleet: '))
			pass
		else:
			pass
		
		if position == None:
			position = input('Enter the coordinates of the fleet in this exact form: ( x , y ): ')
		else:
			pass		

		if position[1] > GROUNDMAP.height or position[0] > GROUNDMAP.width:
			position = input('Indices out of range: there is only blank space there. Please input coordinates between (0,0) and ' + str((GROUNDMAP.width,GROUNDMAP.height)) + ':'  )
		else:
			pass
		
		if fleet == None:
			fleet = input(""" Enter, separated by commas, the ships you want to initialize as part of the """ + name + """. E.g. "fighter,fighter,destroyer": """)
			fleet = tuple(fleet.split(','))
			#fleet is now a list!
			pass
		else:
			pass			
		finalFleet = []
		# processes a list of classnames into a list of ships		
		
		for ship in list(fleet): # list of len 0-infty, which can be either a list of names ['fighter', 'swarmer'...] or a list of existing ships.
			if isinstance(ship,Vessel):
				finalFleet.append(ship)
				pass
			elif isinstance(ship,str):
				if ship in [classname for classname in spaceshipDB.keys()]: # checks whether the name provided is compatible
					newship = Vessel(ship,GROUNDMAP,position) #instantiates a new ship
					finalFleet.append(newship)
					newship.states['fleet'] = self
					newship.states['fleet_name'] = name
					
				else:
					print('Error: wrong ship class_name.')
					return None 
			pass
		
		self.GROUNDMAP = GROUNDMAP  # Special object, which is set at initialization.
		
		self.states = {'name': name,
						'shiplist': finalFleet,		   		# must be a list -- will be a list of Vessel objects!
						'obj_class': 'fleet', 		 		# important! every object class has to have it
						'ship_class': 'Fleet',			 	# special, disposable
						'position': position,
						'faction' : None,
						'health' : 'Intact', 				# will depend on the ships!
						'code': 'O'}
		
		existing_Fleets.extend([self])

		self.updatePosition       # stores itself in the groundmap registry
		print('|| Fleet ' + str(self.states['name']) + ' was created: ' + str(self.states['shiplist']))
		
	def shiplist(self):
		return self.states['shiplist']
		
	@property
	def updateStates(self):
		shiplist = self.states['shiplist']
		for ship in shiplist:
			ship.updateStates
			
		listofHealthstates = [ ship.states['health'] for ship in shiplist ]
		
		groundcounter = 0
		
		for elem in listofHealthstates:
			if elem == 'intact':
				groundcounter += 1
			elif elem == 'lightly_damaged':
				groundcounter += 0.8
			elif elem == 'damaged':
				groundcounter += 0.5
			elif elem == 'seriously_damaged':
				groundcounter += 0.3
			elif elem == 'severely_damaged':
				groundcounter += 0.1
			else:
				pass # adds nothing if it is destroyed
		
		if groundcounter == 0 and self.states['health'] != 'destroyed':
			self.destroy()
			return None
		
		relativecounter = groundcounter / len(shiplist) # total health divided by number of ships
		
		if relativecounter == 1:
			_health = 'intact'
		elif 0.8 <= relativecounter < 1:
			_health = 'lightly_damaged'
		elif 0.5  <= relativecounter < 0.8:
			_health = 'damaged'
		elif 0.3 <= relativecounter < 0.5:
			_health = 'lightly_damaged'
		elif relativecounter < 0.3:
			_health = 'lightly_damaged'
		else:
			return 'Bad value for Fleet.updateStates function'
		
		self.states['health'] = _health
		
		return None
		
	
	def __repr__(self):
		return self.states['name'] + ' Fleet '
	
	#its string will be: set of states of all the ships, and its own ones.
	
	def move(self,path=None):
		"""Guided procedure for moving _a fleet_."""
		
		oriposition = copy.deepcopy(self.states['position'])
		
		if path == None:
			path = input('>> Which path should it follow? [l,r,u,d]; example = lluuddr. ')
		else:
			pass
			
		POS = list(self.states['position']) # is a 2-tuple (x,y) ; to edit we transform it into a list
			
		for letter in path:     # computes the new position, following the orders
			if letter == 'l':
				POS[0] -= 1
			elif letter == 'r':
				POS[0] += 1
			elif letter == 'u':
				POS[1] -= 1
			elif letter == 'd':
				POS[1] += 1											
			else:
				print('Error: invalid direction. [l,r,u,d]')
				return self.move()

		#del self.states['position']
		self.states['position'] = tuple(POS)  # we lock the value again in a tuple
		
		self.updatePosition       # should erase the old position and write the new one
		
		for ship in self.states['shiplist']:
			ship.warp((POS[0],POS[1]), 'override')        # does the same for all of its ships! since the speed is locked, we can warp them all even if the could not
		
		
		return None										
	
	def attack(self,otherObject):
		"""Each of the ships of the fleet attack the object once."""
		
		if self is otherObject:
			raise VesselMethodsError('SelfDestruct is not yet supported.')
		
		if isinstance(otherObject, Vessel) or isinstance(otherObject, mapmethods.Building):
			[ ship.attack(otherObject) for ship in self.states['shiplist'] ]
		else:
			return None
	
	def battle(self,otherFleet=None):
		"""Calls generalizedBattle on self and the otherFleet."""
		# first: check the states of all of its ships
		
		if otherFleet == None:
			otherFleet = self.nearest('fleet')
		
		if self is otherFleet:
			raise VesselMethodsError('SelfDestruct is not yet supported.')
		
		if (isinstance(otherFleet,Fleet) == False and isinstance(otherFleet,Vessel) == False and isinstance(otherFleet,mapmethods.Building) == False) or otherFleet is self: 
			raise VesselMethodsError('The Fleet cannot attack but a different Fleet')
			# some day this will be actually false.
			return None
		else:
			pass
			
		if otherFleet.states['faction'] != self.states['faction'] or otherFleet.states['faction'] == None:
			pass
		else:
			raise VesselMethodsError('The Fleet cannot attack a member of its own faction.')
		generalizedBattle(self,otherFleet)
		return None
	
	@property
	def updatePosition(self):
		"""Displays in the current map the fleet position, represented by an O."""
		self.GROUNDMAP.addToTracker(self) #adds itself to the object list for that square		
		
		return None
		
	def warp(self,xy):
		self.states['position'] = xy
		for ship in self.states['shiplist']:
			ship.warp(xy)
		return None
	
	def destroy(self):
		"""Destroys all of its ships and eliminates itself from the existing_Fleets tracker."""	
		if self.states['health'] == 'destroyed' and [ship for ship in self.shiplist() if ship.states['health'] == 'destroyed'] == self.shiplist():
			print('Nothing to do; the fleet is already destroyed.')
			return None
		else:
			pass
		
		for ship in self.states['shiplist']:
			ship.destroy()
			
		self.states['shiplist'] = []
			
		self.states['health'] = 'destroyed'
		#print('now selfstates health is ' + self.states['health'])
		
		try:
			existing_Fleets.remove(self)
		except ValueError:
			print(str(existing_Fleets))
			#raise VesselMethodsError("""Horrible! This should  not happen. The vessel which 
#we are trying to remove from the tracker was not kept track of!""")
			print('This should not happen. However, presumably that is only a minor mistake.')
		return 'Boom.'
	
	def repair(self):
		"""Full repair of all ships."""
		for ship in self.states['shiplist']:
			ship.repair
			
		existing_Fleets.extend([self])
		return 'Whee'
	
	def __str__(self):
		"""The string representation of a Fleet is the dictionary with its states!"""
		return str(self.states)
	
	def nearest(self,kwargs = None):
		"""Returns a pointer to the closest enemy vessel or fleet."""
		_enemies = []
		distances_enemy_dictionary = {}
		
		optlist = []
		
		if kwargs == 'fleets':
			optlist = existing_Fleets
		
		elif kwargs == 'vessels':
			optlist = existing_Ships
			
		else:
			optlist =  existing_Ships + existing_Fleets
		
		for maybeenemy in optlist:
			if maybeenemy.states['faction'] == self.states['faction']: # not same faction
				pass
			else:
				_enemies.extend([maybeenemy])
		if _enemies == []:
			print('There is no enemy in view!')
			return None
		else:	
			for enemy in _enemies:
				distance = mapmethods.distance(self,enemy.states['position'])
				distances_enemy_dictionary[distance] = enemy
				#adds to the dictionary a pointer to the enemy fleet or ship
		
		minimaldistance = min({distance for distance in distances_enemy_dictionary})
		
		return distances_enemy_dictionary[minimaldistance]
	
	def FleetChoiceDict(self):
		"""Returns a dictionary of options for the factionmethods.printOptions function."""
		
		dictionary = {	0 : ('Destroy', self.destroy),
						1 : ('Nearest', self.nearest),
						2 : ('Move', self.move),
						3 : ('Show_status', self.states),
						4 : ('Repair', self.repair),
						5 : ('Attack_nearest', self.battle)
						}
		
		return dictionary
		
	def stateSum(self):
		return 'stationed at ' + str(self.states['position']) + ', ' + self.states['health']
				
#----------------------------------------------DEBUG ZONE--------------------------------------------#

			
def flatten(input_list):         # UTILITY
	output_list = []
	for element in input_list:
		if type(element) == list:
			output_list.extend(flatten(element))
		else:
			output_list.append(element)
	return output_list			

def clone(ship):  #just for debug-utility!
	"""Creates a copy ship with the same name and class."""
	Ship = Vessel(ship.states['ship_class'])
	Ship.states['name'] = ship.states['name']
	Ship.name = ship.states['name']
	Ship.updateStates
	return Ship
