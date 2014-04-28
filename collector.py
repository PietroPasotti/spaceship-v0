# collector.py
import mapmethods 
import spaceship 
import factionmethods
import sys
import imp
import random
import routinemethods

Mainmap = ''



def randomship():
	return random.choice(spaceship.existing_Ships)
	
def randomfleet():
	return random.choice(spaceship.existing_Fleets)


A = mapmethods.Asteroid_Field(30,100) 
B = mapmethods.Map(A)

Mainmap = B #(only for debugging purposes)

P1 = factionmethods.Faction(B,'Gorillas')

K = spaceship.Fleet(B,'Gargoyles',('fighter','fighter'),(16,9))

B1 = mapmethods.Building('base',A,P1)

P1.assign(K)
P1.assign(B1)

L = spaceship.Fleet(B,'Superstars',('fighter','fighter'),(10,10))
Z = spaceship.Fleet(B,'Smashers',('bomber','bomber','bomber','mothership'),(10,9))	
B2 = mapmethods.Building('generator',A,P1)
B3 = mapmethods.Building('battery',A,P1)  #  def __init__(self,className,AsteroidField,faction,coordinates=None):

P2 = factionmethods.Faction(B,'Gundams')

P2.assign(L)
P2.assign(Z)
P2.assign(B3)

#P1Base = P1.build('base',A.randomPlot)

#launch(self,building = None, classname = None):
#P1.launch(P1Base, 'fighter')

B.brutal_dump

L.battle(K)


