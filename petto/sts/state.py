from pathlib import Path
from typing import List


class State:

    database = Path('petto/txt/state.txt')
    friends = {}

    def __init__(self, bot_id: int, age: int = 0, hunger: int = 5, hygiene: int = 0,
            power: int = 0, stage: int = 0, thirst: int = 0, weight: int = 10,
            overwrite: bool = False):
        self.id = bot_id
        self.age = age
        self.hunger = hunger
        self.hygiene = hygiene
        self.power = power
        self.stage = stage
        self.thirst = thirst
        self.weight = weight
        if overwrite:
            self._save()
        elif self.database.exists():
            with open(str(self.database)) as f:
                line = f.readline()
                if line:
                    stats = line.split(',')
                    for field, stat in zip(self.__dict__, stats):
                        setattr(self, field, int(stat))
                    for friend in f.readlines():
                        friend_id, strength = map(int, friend.split(','))
                        self.friends[friend_id] = strength
        else:
            self.database.touch()

    def ordered_friends(self) -> List[int]:
        if self.friends:
            return sorted(self.friends, key=self.friends.get)
        return []

    def format(self) -> str:
        form = (f"{self.id:<20},{self.age:0>3},{self.hunger:0>3},{self.hygiene:0>3},"
            f"{self.power:0>3},{self.stage:0>2},{self.thirst:0>3},{self.weight:0>3}")
        for friend_id, strength in self.friends.items():
            form = f"{form}\n{friend_id},{strength}"
        return f"{form}\n"

    def update_hygiene(self, n: int) -> None:
        if self.hygiene + n > 5:
            self.hygiene = 5
        elif self.hygiene + n < 0:
            self.hygiene = 0
        else:
            self.hygiene += n
        self._save()
        return None

    def update_thirst(self, n: int) -> None:
        if self.thirst + n > 5:
            self.thirst = 5
        elif self.thirst + n < 0:
            self.thirst = 0
        else:
            self.thirst += n
        self._save()
        return None

    def _save(self) -> None:
        with open(str(self.database), 'w') as f:
            f.write(self.format())
