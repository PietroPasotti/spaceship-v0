# NAMES FACTORY
import random
import string

def getname(param=None):
	if param != None:
		if param == 'short':
			return newname('s')
		elif param == 'long':
			return newname('l')
		else:
			raise 'Error: wrong input'
	else:
		return newname('m')
		
def newname(length='m'):
	"""Returns a randomized name."""
	
	listofnamesINI = sorted(['Chimney',
	 'Burzons',
	 'Peaceful',
	 'Happy',
	 'Brutal',
	 'Killing',
	 'Gambling',
	 'Sodomizing',
	 'Astonishing',
	 'Shameful',
	 'Dingling',
	 'Wooden',
	 'Longing',
	 'Diamond',
	 'Coral',
	 'Hard',
	 'Hardcore',
	 'Barbaric',
	 'Swedish',
	 'Soft',
	 'Mistress',
	 'Silent',
	 'Farting',
	 'Laughing',
	 'Trivial',
	 'Shameless',
	 'Black'])

	listofnamesEND = sorted(['Buddha',
	 'Cabron',
	 'Certainty',
	 'Cheetah',
	 'Claw',
	 'Demolisher',
	 'Dominator',
	 'Dragon',
	 'Fang',
	 'Hammer',
	 'Iron',
	 'Light',
	 'Melody',
	 'Metal',
	 'Naught',
	 'Neutron',
	 'Proof',
	 'Purger',
	 'Purr',
	 'Raper',
	 'Reaper',
	 'Shadow',
	 'Shark',
	 'Slowliness',
	 'Sparrow',
	 'Teeth',
	 'Theorem',
	 'Wittgenstein'])
	
	if length == 'a': #FOR ASTEROIDS
		LENGTH = 8
		name = ''
		for a in range(LENGTH):
			name = name + random.choice(list(string.digits))
		return name
			
	elif length =='l':
		LENGTH = 5
	elif length == 's':
		LENGTH = 2
	else:
		LENGTH = 3
		
	numberz = ''
	for i in range(LENGTH):
		numberz = numberz + random.choice(list(string.digits))
		
	if random.choice([0,1,2]) == 0:   #the name is either...
		name = random.choice(listofnamesINI) + random.choice(listofnamesEND) + '_' + numberz
		return name
	elif random.choice([0,1,2]) == 1: #or...
		name = random.choice(listofnamesEND) + 'Of' + random.choice(listofnamesINI) + '_' + numberz
		return name
	else: #random.choice([0,1,2]) == 2: #or...
		name = numberz  + '_' + random.choice(listofnamesINI) + random.choice(listofnamesEND)
		return name

def newFactionName():
	
	name = random.choice(	['Brutalizers','Gogglers','The_Disadvantaged','Cabrones','Dummies','Zombies','Venus_Tearers','The_Peones',
							'The_GangBangers','Yrghyghhyschykush','The_Optimizers','FairPlayers','The_Bad_Kingdom','Sudoku','The_Shimpanzees',
							'The_Gorillas','Babblers','AlphaBetaGagas','TruthMakers','PeaceKeepers','MommyMummies','The_Chefs',
							'The_Randomizers','The_Silencers','Existentialists','KarlMarx','Empire','Alliance','Rebels','Axis','Pirates',
							'Barbarians','Lvl1Paladins','Terminators'])
	
	return name
