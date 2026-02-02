from pathlib import Path


class State:

    file = Path('state.txt')
    friends = {}

    def __init__(self):
        self.age = 0
        self.health = 0
        self.hunger = 0
        self.hygiene = 0
        self.mood = 0
        self.posts = 0
        self.power = 0
        self.stage = 0
        self.thirst = 0
        self.weight = 0
        if self.file.exists():
            with open(str(self.file)) as f:
                stats = f.readline().split(',')
                for field, stat in zip(self.__dict__, stats):
                    setattr(self, field, stat)
                for friend in f.readlines():
                    friend_id, strength = map(int, friend.split(','))
                    self.friends[friend_id] = strength
        else:
            self.file.touch()

    def format(self) -> str:
        form = (f"{self.age:0>3},{self.health:0>3},{self.hunger:0>3},{self.hygiene:0>3},"
            f"{self.mood:0>3},{self.power:0>3},{self.stage:0>2},{self.thirst:0>3},"
            f"{self.weight:0>3}")
        for friend_id, strength in self.friends.items():
            form = f"{form}\n{friend_id},{strength}"
        return f"{form}\n"

    def _save(self) -> None:
        with open(str(self.file), 'w') as f:
            f.write(self.format())
