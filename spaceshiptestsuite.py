import unittest
import spaceship
import random,sys
import mapmethods
import factionmethods
from copy import deepcopy
	
		
class SpaceshipTestCase(unittest.TestCase):
	
	def setUp(self):
		
		B = mapmethods.Asteroid_Field(30,100) # width 30, height 100
		A = mapmethods.Map(B)
	
		self.dummyshiplist = [ spaceship.Vessel(shipclass,A) for shipclass in ['fighter','fighter', 'bomber',
														'fighter','fighter', 'bomber','bomber','bomber',
														'fighter','fighter', 'bomber','bomber','bomber',
														'mothership', 'bomber','bomber','bomber','bomber',
														'mothership', 'bomber','bomber','bomber','bomber',
														'mothership', 'bomber','bomber','bomber','mothership']]
		
		self.dummyPlayer1 = factionmethods.Faction(A)
		self.dummyPlayer2 = factionmethods.Faction(A)
		
		# building init (self,className,AsteroidField,faction,coordinates=None):     takes no map input
		self.dummyBuilding1 =  mapmethods.Building('generator',B,self.dummyPlayer1)
		self.dummyBuilding2 =  mapmethods.Building('base',B,self.dummyPlayer2)
			
		self.dummyFleet1  = spaceship.Fleet(A,'Smashers',('bomber','bomber','bomber','mothership'),(10,9))	
		self.dummyFleet2  = spaceship.Fleet(A,'Elder Brothers',('bomber','bomber','bomber','mothership'),(11,9))
		
	def test_Spaceship_destroy(self):
		"""spaceship.destroy function."""
		for vsl in self.dummyshiplist:
			vsl.destroy()
			self.assertEqual(vsl.states['health'], 'destroyed')
			
	def test_Spaceship_repair(self):
		"""Checks whether the repair function works."""
		for vsl in self.dummyshiplist:
			vsl.repair()
			self.assertEqual(vsl.states['health'], 'intact')
	
	def test_SomebodyActive(self):
		""" The algorithm should return True if there is some ship still able to either withstand or deal damage in the input shiplist. """
		for vsl in self.dummyshiplist:
			vsl.destroy()
			
		result = spaceship.somebodyActive(self.dummyshiplist)
		self.assertEqual(result,False)
		
		for vsl in self.dummyshiplist:
			vsl.repair()
	
	def test_OnlyNotDestroyedPlayers(self):
		""" Checks the algorithm for picking only not destroyed players out of a shiplist. """
		for vsl in self.dummyshiplist:
			vsl.destroy()
			
		prunedlist = spaceship.onlyNotDestroyedPlayers(self.dummyshiplist)
		
		self.assertEqual(prunedlist, [])
		# all ships have just been destroyed...
		
		for vsl in self.dummyshiplist:
			vsl.repair()
			
		prunedlist2 = spaceship.onlyNotDestroyedPlayers(self.dummyshiplist)
		
		self.assertTrue(prunedlist2 == self.dummyshiplist)
		print('im here')
		# now all ships have been healed
		
		for i in range(100):
			a = random.choice(self.dummyshiplist)
			a.destroy() # destroys it
			updatedlist = spaceship.onlyNotDestroyedPlayers(self.dummyshiplist)
			self.assertNotIn(a, updatedlist)
			a.repair # repairs it, so that the next round he is back again in the self.dummyshiplist
	
	def test_generalizedBattleSubAlgorithm1(self):
		"""The algorithm for attackables and can_attackers should do their work."""	
		for i in range(10):
			self.dummyFleet1.destroy()
			self.dummyFleet2.repair()
			
			shiplist1 = self.dummyFleet1.states['shiplist']
			shiplist2 = self.dummyFleet2.states['shiplist']
			
			fleet1attackables = spaceship.attackables(shiplist1)
			fleet1canattackers = spaceship.can_attack(shiplist1)
			fleet2canattackers = spaceship.attackables(shiplist2)
			fleet2attackables = spaceship.can_attack(shiplist2)
			
			self.assertEqual(fleet1attackables,[])
			self.assertEqual(fleet1canattackers,[])
			self.assertEqual(fleet2canattackers,shiplist2)
			self.assertEqual(fleet2attackables,shiplist2)
			
			a = random.choice(shiplist1)
			a.repair()
			
			fleet1attackables = spaceship.attackables(shiplist1)
			fleet1canattackers = spaceship.can_attack(shiplist1)	
			
			self.assertIn(a,fleet1attackables)
			self.assertIn(a,fleet1canattackers)
			
			self.dummyFleet1.repair()
			self.dummyFleet2.repair()
		
	def test_dieRepairAttackProperties(self):
		""" Destroying a ship should turn its can_attack and can_be_attacked states off. Repairing it should reverse that. """
		[ vsl.destroy() for vsl in self.dummyshiplist ]
		
		self.assertEqual([ vsl for vsl in self.dummyshiplist if vsl.states['can_attack'] == True ] , [] )
		self.assertEqual([ vsl for vsl in self.dummyshiplist if vsl.states['can_be_attacked'] == True ] , [] )
		
		[ vsl.repair() for vsl in self.dummyshiplist ]
		
		self.assertTrue( self.dummyshiplist == [ vsl for vsl in self.dummyshiplist if vsl.states['can_attack'] == True ])

	def test_generalizedBattleAlgorithm(self):
		""" The algorithm for generalized battle should run smoothly. """
		for i in range(20):
			
			Fleet1 = deepcopy(self.dummyFleet1)
			Fleet2 = deepcopy(self.dummyFleet2)
			
			Fleet1.battle(Fleet2)
			
			Fleet1.repair()
			Fleet2.repair()
			
			Fleet2.battle(Fleet1) # mostly will do nothing as they already fought; must be pretty destroyed
	
	def test_distancesAndAttackProperties(self):
		"""Ships and fleets shouldn't be able to attack if out of range."""
		for i in range(10):
			
			a = random.choice(self.dummyshiplist)
			b = random.choice([ ship for ship in self.dummyshiplist if ship != a ])
			
			a.attack(b)
			
			b.warp((10,10))
			a.warp((30,30))
			
			self.assertFalse(a.checkRange(b))
			self.assertFalse(b.checkRange(a))
			self.assertFalse(b.checkRange(a.states['position']))
			self.assertFalse(b.checkRange(a.states['position']))
		
			badinputs = [(1.0,1.3), 
							(10,10,10),
							(10),
							'anystring',
							(1000000,10000123),
							['any','list'],
							[10,10],
							[1.4,1.4]]
			
			for badinput in badinputs:
				self.assertRaises(spaceship.VesselMethodsError, a.checkRange, badinput) 
			
			
			self.assertIsNone(b.attack(a))
			self.assertIsNone(a.attack(b)) # with ships out of range, should return none
			
			a.warp((10,10))
			
			a.attack(b)
			b.attack(a)
	
	def test_attackOneself_Vessels(self):		
		"""Ships shouldn't be able to attack themselves."""
		a = random.choice(self.dummyshiplist)
		b = random.choice([ ship for ship in self.dummyshiplist if ship != a ])	
		
		self.assertRaises(spaceship.VesselMethodsError, a.attack, a)
		self.assertRaises(spaceship.VesselMethodsError, b.attack, b)
		a.attack(b)
		b.attack(a)

	def test_attackOneself_Fleets(self):			
		"""Fleets shouldn't be able to attack themselves."""
		
		self.assertRaises(spaceship.VesselMethodsError, self.dummyFleet1.battle, self.dummyFleet1)
		self.assertRaises(spaceship.VesselMethodsError, self.dummyFleet2.battle, self.dummyFleet2)
		
		
		self.dummyFleet1.battle(self.dummyFleet2) # should go smooth	

	def test_assignToFaction(self):
		"""Check whether assigning a ship, fleet or building to a faction does what it should do."""
		
		self.dummyPlayer1.assign(self.dummyBuilding1)
		self.assertEqual( self.dummyBuilding1.states['faction'], self.dummyPlayer1 )
		
		self.dummyPlayer2.assign(self.dummyBuilding1)
		self.assertEqual( self.dummyBuilding1.states['faction'], self.dummyPlayer2 )
		
		self.dummyPlayer2.assign(self.dummyBuilding2)
		self.assertEqual( self.dummyBuilding2.states['faction'], self.dummyPlayer2 )

	def test_checkDifferentFaction_Vessels(self):
		"""checkDifferentFaction should return true iff the factions are different."""
		
		for ship in self.dummyFleet2.states['shiplist']: # ('bomber','bomber','bomber','mothership')
			b = random.choice(self.dummyshiplist) # picks a random vessel of faction None
			self.assertTrue( ship.checkDifferentFaction( b )  ) # they should be of different factions!
			
			a = random.choice(self.dummyshiplist) # picks another random vessel of faction None
			self.assertTrue( a.checkDifferentFaction( b ) ) # both being none, their factions are different
			
			self.dummyPlayer1.assign(a)
			self.dummyPlayer2.assign(b)
			self.assertTrue( a.states['faction'] == self.dummyPlayer1 )
			self.assertTrue( b.states['faction'] == self.dummyPlayer2 )
			self.assertTrue( a.checkDifferentFaction( b ) ) # now they should indeed belong to different factions
			
			self.dummyPlayer2.assign(a)			
			self.assertFalse( a.checkDifferentFaction( b ) ) # now they should belong to the same faction == dummyPlayer1
			
	def test_attackSameFaction_Vessels(self):		
		"""Ships shouldn't be able to attack objects of their own faction//player."""
		
		a = random.choice(self.dummyshiplist)
		b = random.choice([ ship for ship in self.dummyshiplist if ship != a ])	
		
		a.states['faction'] = 'Gingerrogers'
		b.states['faction'] = 'Gingerrogers'
		
		self.assertRaises(spaceship.VesselMethodsError, a.attack, b)
		
		self.dummyFleet2.states['faction'] = 'AlphaBetaGagas'
		
		a.attack(self.dummyFleet2)  # should go smooth
		
	def test_attackSameFaction_Fleets(self):		
		"""Fleets shouldn't be able to attack objects of their own faction."""

		self.dummyFleet1.states['faction'] = 'Gingerrogers'
		self.dummyFleet2.states['faction'] = 'Gingerrogers'
		
		self.assertRaises(spaceship.VesselMethodsError, self.dummyFleet1.battle, self.dummyFleet2)
		
		self.dummyFleet2.states['faction'] = 'AlphaBetaGagas'
		
		self.dummyFleet1.battle(self.dummyFleet2) # should go smooth


		
				

if __name__ == '__main__':
	sys.stdout = None
	unittest.main()
	sys.stdout = sys.__stdout__
