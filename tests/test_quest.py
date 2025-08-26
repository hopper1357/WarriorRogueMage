import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from quest import Quest, KillObjective
from event_manager import event_manager

def test_kill_objective_update():
    objective = KillObjective("Kill a goblin", "Goblin", 1)

    event_manager.subscribe("monster_killed", objective.update)

    # Post an irrelevant event
    event_manager.post({"type": "monster_killed", "name": "Rat"})
    assert not objective.is_complete

    # Post the relevant event
    event_manager.post({"type": "monster_killed", "name": "Goblin"})
    assert objective.is_complete

def test_quest_completion():
    obj1 = KillObjective("Kill a goblin", "Goblin", 1)
    obj2 = KillObjective("Kill a rat", "Rat", 1)

    reward_called = False
    def reward_func(player):
        nonlocal reward_called
        reward_called = True

    quest = Quest("Test Quest", "A test quest.", [obj1, obj2], reward_func)

    event_manager.subscribe("monster_killed", quest.update)

    assert not quest.is_complete

    event_manager.post({"type": "monster_killed", "name": "Goblin"})
    assert not quest.is_complete

    event_manager.post({"type": "monster_killed", "name": "Rat"})
    assert quest.is_complete

    # Test reward
    quest.give_reward(None) # player object is not needed for this test
    assert reward_called is True
