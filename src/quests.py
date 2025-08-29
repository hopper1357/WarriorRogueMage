from quest import Quest, KillObjective, CollectObjective
from items import all_items

def goblin_menace_reward(player):
    player.add_xp(100)
    player.inventory.append(all_items["health_potion"])

goblin_menace = Quest(
    title="Goblin Menace",
    description="A goblin has been spotted nearby. Please get rid of it.",
    objectives=[
        KillObjective("Defeat the Goblin", "Goblin", 1)
    ],
    reward_func=goblin_menace_reward
)

def heirloom_reward(player):
    player.add_xp(300)
    player.add_item_to_inventory(all_items["rune_blade"])

stolen_heirloom = Quest(
    title="The Stolen Heirloom",
    description="A bandit leader has stolen a precious family heirloom. Get it back!",
    objectives=[
        KillObjective("Defeat the Bandit Leader", "Bandit Leader", 1),
        CollectObjective("Recover the Stolen Heirloom", all_items["stolen_heirloom"])
    ],
    reward_func=heirloom_reward
)

all_quests = {
    "goblin_menace": goblin_menace,
    "stolen_heirloom": stolen_heirloom,
}
