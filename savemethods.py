#SAVEMETHODS!
import os.path
import re
import pickle
import spaceship


def already_exists(string):
	if os.path.isfile(string + '.txt') or os.path.isfile(string + '.py') or os.path.isfile(string + '.universe') or os.path.isfile(string):
		return True
	else:
		return False

def writeToFile(Map,name=None, split=False):
	"""
	Should snapshot in a file the existing ships and their states.
	Takes as input a Map objects.
	"""
	

	
	# now we add to universe all the things we need to save: ships, buildings, asteroids and whatever
	
	#shiporfleetlist = []      		#1	
	#buildingslist = []
	
	
	#for shipOrFleet in Map.TRACKER:
	#	shiporfleetlist = shiporfleetlist + [str(shipOrFleet)]
	
	
	
	
############################### _universe ###########################
#																	#
	_universe = Map #[shiporfleetlist, buildingslist,Map]				#
#																	#
#####################################################################
	
		
	if name == None:
		string = raw_input("Enter the name of the savefile you want to save the universe to: ")
	else:
		string = name
		pass
	
	if isinstance(string,str) == True:
		pass
	else:
		print('Invalid name: must be a string.')
		return writeToFile(_universe)
	
	string = str(string) + '.universe'
	
	print('Saving to ' + string + '...')
	
	if already_exists(string) == True:
		print('The file already exists!')
		if raw_input('Are you sure you want to overwrite the previous savefile? [y/n] ') in 'Yesyes':
			pass
		else:
			string = raw_input('Insert a new name then: ')
			writeToFile(_universe,string)	
	else:
		pass
		
	
	# separates the savefile with all the states and the mapcode (the aim is to have a separate mapcode, if split = True)
	
	if split == True:
		
		filename = raw_input('Enter the name of the mapfile you want to create (warning: this will overwrite any previously saved map):\n' + ' '*10 +'>>> ') + '.asteroid'
		#with  open(string, mode='w') as FILE:
		
		oristdout = sys.stdout 
		sys.stdout = open(filename, "w") # redirects the print function
		
		_universe.brutal_dump # dumps the map as is into the newly created file
	
		sys.stdout = oristdout # resets the stdout after you're done
	
	else:
		pass
	
	with open(string, mode='w') as FILE:
		pickle.dump(_universe, FILE)
		
	return None

 # currently the savefile is a tuple of lists. The first of such lists is a dictionary, and they are the ships' complete description.

def loadFromFile(fileName=None):
	if fileName == None:
		fileName = raw_input('Enter the name of the savefile which you would like to load: ')
	else:
		try:
			fileName = str(fileName)
		except NameError:
			print('Error: name is badly defined.')
			fileName = raw_input('Try again: ')
			return loadFromFile(fileName)
	
	if already_exists(fileName) == False:
		print('Error: the savefile '+ fileName + ' does not exist.')
		return loadFromFile()
	else:
		pass
	
	if bool(re.search( ' *\.universe' , fileName)) == True: 
		pass  # the name already contains '.universe' (the user may have typed it such)
	else:
		fileName = fileName + '.universe'
	
	print('Loading ' + fileName + '...')
	
	with open(fileName, mode='r') as savefile:
		structure = pickle.load(savefile)
		
		return structure
	
	return None

def populateObjectUniverse(structure):
	"""Reads what is loaded by the loadFromFile function and spawns all the objects which were stored there."""
	print('Populating universe...')	 
	counter = 0
	# the data is stored as a tuple of lists. the first list is a list of dictionaries
	
	
	for num in range(len(structure)): # element of a tuple
		print(' Checking Substructure ' + str(counter) + '...' )
		
		subcounter = 0
		
		for subnum in range(len(structure[num])): # parse each list in the tuple
			print('  Checking Subsubstructure ' + str(subcounter) + '...' )
			
			substructure = structure[num][subnum] # element of the list must be a dictionary
			
			if substructure['obj_class'] == 'ship':
				print('  	> Parsing a ship...' )
				newship = spaceship.Vessel(substructure['ship_class']) 	# initializes a Vessel of the same class
				newship.states = substructure							# gives the ship the same states
				pass
			elif substructure['obj_class'] == 'faction':
				print('    > Parsing a faction substructure...')
				newfaction = spaceship.Faction(substructure['name'],substructure['fleet'])
				pass
			else:
				print('No list found in serialized database. There must be some error around...')
				break
				
			subcounter += 1
			pass
		
		counter += 1
		pass
	pass
		
	
	print('Universe populated!')
	return None
