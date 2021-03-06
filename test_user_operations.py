import unittest
import user
from users import UserDatabase
from users import CapturedState
from users import ComparisonResult

class FakeDatabaseSession:
    def __init__(self):
        self.didCommit = False
        self.things = [ ]
    def commit(self):
        self.didCommit = True
    def add(self, thingToAdd):
        self.things.append(thingToAdd)

class FakeDatabase:
    def __init__(self):
        self.session = FakeDatabaseSession()

class TestUserOperations(unittest.TestCase):
    def setUp(self):
        self.userDB = UserDatabase()
        self.appDB = FakeDatabase()
        self.appDBSession = self.appDB.session

        self.register_ash()
        self.register_misty()
    def tearDown(self):
        self.userDB = None
        self.appDB = None
        self.appDBSession = None

    # Convenience
    def register_ash(self):
        self.userDB.registerUser("AshKetchum", "pallettown123", "000000000000", self.appDB)
    def register_misty(self):
        self.userDB.registerUser("Misty", "cerulean456", "111111111111", self.appDB)
    def ash_user(self):
        return self.appDBSession.things[0]
    def misty_user(self):
        return self.appDBSession.things[1]

    # Registration
    def test_registration(self):
        user = self.ash_user()
        self.assertEqual(user.username, "AshKetchum")
        self.assertTrue(self.appDB.session.didCommit)

    # Catching / Releasing
    def test_catching_pokemon_works(self):
        user = self.ash_user()
        # Catch Pikachu
        self.userDB.catchPokemonForUser(user, 25, self.appDB)
        # Grab the state of the Pokemon @ 25
        state = self.userDB._stateOfPokemonForUser(user, 25)
        self.assertEqual(state, CapturedState.Caught)
    def test_new_user_hasnt_caught_pokemon(self):
        user = self.ash_user()
        # Grab the state of the Pokemon @ 25
        # It should be 0
        state = self.userDB._stateOfPokemonForUser(user, 25)
        self.assertEqual(state, CapturedState.Uncaught)
    def test_catching_then_releasing_pokemon_works(self):
        user = self.ash_user()
        # Catch Pikachu
        self.userDB.catchPokemonForUser(user, 25, self.appDB)
        # Release Pikachu :-(
        self.userDB.uncatchPokemonForUser(user, 25, self.appDB)
        # Grab the state of the Pokemon @ 25
        state = self.userDB._stateOfPokemonForUser(user, 25)
        self.assertEqual(state, CapturedState.Uncaught)

    # Comparison
    ## Keep in mind that comparisonResultBetweenUsers() accepts a 0-indexed
    ## Pokedex index
    def test_comparing_user_without_pokemon_and_user_without_pokemon_returns_neither_having_pokemon(self):
        ash = self.ash_user()
        misty = self.misty_user()
        state_of_pikachu = self.userDB.comparisonResultBetweenUsers(ash, misty, 24)
        self.assertEqual(state_of_pikachu, ComparisonResult.NeitherCaught)
    def test_comparing_user_with_pokemon_and_user_without_pokemon_returns_first_having_pokemon(self):
        ash = self.ash_user()
        misty = self.misty_user()
        self.userDB.catchPokemonForUser(ash, 25, self.appDB)
        state_of_pikachu = self.userDB.comparisonResultBetweenUsers(ash, misty, 24)
        self.assertEqual(state_of_pikachu, ComparisonResult.FirstCaught)
    def test_comparing_user_without_pokemon_and_user_with_pokemon_returns_second_having_pokemon(self):
        ash = self.ash_user()
        misty = self.misty_user()
        self.userDB.catchPokemonForUser(misty, 116, self.appDB)
        state_of_horsea = self.userDB.comparisonResultBetweenUsers(ash, misty, 115)
        self.assertEqual(state_of_horsea, ComparisonResult.SecondCaught)
    def test_comparing_user_with_pokemon_and_user_with_pokemon_returns_both_having_pokemon(self):
        ash = self.ash_user()
        misty = self.misty_user()
        self.userDB.catchPokemonForUser(ash, 128, self.appDB)
        self.userDB.catchPokemonForUser(misty, 128, self.appDB)
        state_of_tauros = self.userDB.comparisonResultBetweenUsers(ash, misty, 127)
        self.assertEqual(state_of_tauros, ComparisonResult.BothCaught)

if __name__ == '__main__':
    unittest.main()
