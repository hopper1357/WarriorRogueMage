class Objective:
    def __init__(self, description):
        self.description = description
        self.is_complete = False

    def update(self, event):
        """Update the objective's status based on a game event."""
        pass

class KillObjective(Objective):
    def __init__(self, description, target_name, required_count=1):
        super().__init__(description)
        self.target_name = target_name
        self.required_count = required_count
        self.current_count = 0

    def update(self, event):
        if event["type"] == "monster_killed" and event["name"] == self.target_name:
            self.current_count += 1
            if self.current_count >= self.required_count:
                self.is_complete = True
                print(f"Objective complete: {self.description}")

class Quest:
    def __init__(self, title, description, objectives, reward_func):
        self.title = title
        self.description = description
        self.objectives = objectives
        self.reward_func = reward_func
        self.is_complete = False

    def update(self, event):
        for objective in self.objectives:
            if not objective.is_complete:
                objective.update(event)

        if all(obj.is_complete for obj in self.objectives):
            self.is_complete = True

    def give_reward(self, player):
        if self.is_complete:
            self.reward_func(player)
            print(f"Quest '{self.title}' complete! Reward received.")

class CollectObjective(Objective):
    def __init__(self, description, target_item):
        super().__init__(description)
        self.target_item = target_item

    def update(self, event):
        if event["type"] == "inventory_updated" and event["item"].name == self.target_item.name:
            self.is_complete = True
            print(f"Objective complete: {self.description}")
