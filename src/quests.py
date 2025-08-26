from quest import Quest, KillObjective
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

all_quests = {
    "goblin_menace": goblin_menace,
}
