from pathlib import Path


class State:

    file = Path('petto/state.txt')
    friends = {}

    def __init__(self, age: int = 0, hunger: int = 0, hygiene: int = 0,
            power: int = 0, stage: int = 0, thirst: int = 0, weight: int = 0,
            overwrite_file: bool = False):
        self.age = age
        self.hunger = hunger
        self.hygiene = hygiene
        self.power = power
        self.stage = stage
        self.thirst = thirst
        self.weight = weight
        if overwrite_file:
            self._save()
        else:
            if self.file.exists():
                with open(str(self.file)) as f:
                    line = f.readline()
                    if line:
                        stats = line.split(',')
                        for field, stat in zip(self.__dict__, stats):
                            setattr(self, field, int(stat))
                        for friend in f.readlines():
                            friend_id, strength = map(int, friend.split(','))
                            self.friends[friend_id] = strength
            else:
                self.file.touch()

    def format(self) -> str:
        form = (f"{self.age:0>3},{self.hunger:0>3},{self.hygiene:0>3},"
            f"{self.power:0>3},{self.stage:0>2},{self.thirst:0>3},{self.weight:0>3}")
        for friend_id, strength in self.friends.items():
            form = f"{form}\n{friend_id},{strength}"
        return f"{form}\n"

    def update(self, field: str, n: int) -> None:
        setattr(self, field, n)
        self._save()
        return None

    def _save(self) -> None:
        with open(str(self.file), 'w') as f:
            f.write(self.format())
