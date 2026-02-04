from math import sqrt
from pathlib import Path
from typing import Dict


class Player:

    def __init__(self, index: int, player_id: int, active: int = 0, health: int = 0, level: int = 0,
            mood: int = 0, posts: int = 0, reacts: int = 0, score: int = 0, items: str = ''):
        self.active = active
        self.health = health
        self.id = player_id
        self.index = index
        self.level = level
        self.mood = mood
        self.posts = posts
        self.reacts = reacts
        self.score = score
        self.items = items.split(',') if items else []

    def calc_level(self) -> int:
        if not self.score:
            return 0
        A = 9910.10197
        a, b, c  = A / 9801, 0.89797, self.score - 1
        x = 1 + (sqrt(abs(b*b - 4*a*c)) - b) / (2*a)
        level = int(x)
        if level > 99:
            level = 99
        return level

    def format(self) -> str:
        return (f"{self.id:<20},{self.active:0>3},{self.health:0>3},{self.level:0>2},"
                f"{self.mood:0>2},{self.posts:0>20},{self.reacts:0>20},{self.score:0>20}\n"
                f"{','.join(self.items)}\n")


class Stats:

    file = Path('petto/stats.txt')

    def __init__(self):
        self._stats: Dict[int, Player] = {}
        if self.file.exists():
            with open(str(self.file)) as f:
                i, line = 0, f.readline()
                while line:
                    stats = line.split(',')
                    player_id = int(stats[0])
                    self._stats[player_id] = Player(i, *map(int, stats), f.readline().strip())
                    i, line = i + 1, f.readline()
        else:
            self.file.touch()

    def create_player(self, player_id: int) -> Player:
        player = Player(len(self._stats), player_id)
        self._stats[player_id] = player
        self._update(player)
        return player

    def delete(self, player_id: int) -> None:
        del self._stats[player_id]
        with open(str(self.file), 'w') as f:
            for i, player in enumerate(self._stats.values()):
                player.index = i
                f.write(player.format())
        return None

    def get_player(self, player_id: int) -> Player:
        if player_id in self._stats:
            return self._stats[player_id]
        player = self.create_player(player_id)
        return player

    def update_posts(self, player_id: int, n: int) -> None:
        player = self.get_player(player_id)
        player.posts += n
        player.score += n
        self._update(player)
        return None

    def update_reacts(self, player_id: int, n: int) -> None:
        player = self.get_player(player_id)
        player.reacts += n
        player.score += n
        self._update(player)
        return None

    def update_score(self, player_id: int, n: int) -> None:
        player = self.get_player(player_id)
        player.score += n
        self._update(player)
        return None

    def _update(self, player: Player) -> None:
        data = player.format()
        with open(str(self.file), 'r+') as f:
            f.seek(player.index * len(data))
            f.write(data)
        return None
