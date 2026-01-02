from pathlib import Path

from math import sqrt


class Player:

    def __init__(self, index, player_id: int, health: int, level: int,
                 level_heart: int, posts: int, reacts: int, score: int):
        self.index = index
        self.id = player_id
        self.health = health
        self.level = level
        self.level_heart = level_heart
        self.posts = posts
        self.reacts = reacts
        self.score = score

    def calc_level(self, player_id: int) -> int:
        A = 9910.10197
        a, b, c  = A / 9801, 0.89797, self.score - 1
        x = 1 + (sqrt(abs(b*b - 4*a*c)) - b) / (2*a)
        level = int(x)
        if level > 99:
            level = 99
        return level

    def format(self) -> str:
        return (f"{self.id:<20},"
                f"{self.health:0>3},"
                f"{self.level:0>2},"
                f"{self.level_heart:0>2},"
                f"{self.posts:0>13},"
                f"{self.reacts:0>13},"
                f"{self.score:0>13}\n")


class Stats:

    file = Path('database/files/stats.txt')
    
    def __init__(self):
        self.lvl_hrt = 10
        self.stats = {}
        if self.file.exists():
            with open(str(self.file)) as f:
                for i, line in enumerate(f.readlines()):
                    stats = line.split(',')
                    player_id = int(stats[0])
                    self.stats[player_id] = Player(i, *map(int, stats))
        else:
            self.file.touch()

    def clear_score(self, player_id: int) -> None:
        player = self.get_player(player_id)
        player.score = 0
        self._update(player_id)
        return None

    def decrease_health(self, player_id: int) -> None:
        player = self.get_player(player_id)
        player.health -= 1
        if not self.health:
            player.score = 0
            player.level = 0
            player.level_heart = 0
        self._update(player)
        return None

    def decrease_reacts(self, player_id: int) -> None:
        self.increase_reacts(player_id, -1)
        return None

    def decrease_score(self, player_id: int, points: int) -> None:
        self.increase_score(player_id, -points)

    def delete_player(self, player_id: int) -> None:
        del self.stats[player_id]
        with open(str(self.file), 'w') as f:
            for i, player in enumerate(self.stats.values()):
                player.index = i
                f.write(player.format())
        return None

    def get_health_str(self, player_id: int) -> str:
        player = self.get_player(player_id)
        if player.health:
            return player.health * '❤️'
        return '💀'

    def get_player(self, player_id: int) -> Player:
        if player_id in self.stats:
            return self.stats[player_id]
        self._create_player(player_id)
        return self.stats[player_id]

    def increase_hearts(self, player: Player, n: int) -> None:
        player.health += n
        player.level_heart += n * self.lvl_hrt
        self._update(player)
        return None

    def increase_posts(self, player_id: int) -> None:
        player = self.get_player(player_id)
        player.posts += 1
        self.increase_score(player_id, 1)
        return None

    def increase_reacts(self, player_id: int, points: int = 1) -> None:
        player = self.get_player(player_id)
        player.reacts += points
        self.increase_score(player_id, points)

    def increase_score(self, player_id: int, points: int) -> None:
        player = self.get_player(player_id)
        player.score += points
        self._update(player)
        return None

    def level_hearts(self, player_id: int) -> int:
        player = self.get_player(player_id)
        lvl_since_heart = player.level - player.level_heart
        if lvl_since_heart == 1:
            # First level gets a heart.
            self.increase_hearts(player, 1)
            return 1
        new_hearts = lvl_since_heart // self.lvl_hrt
        if new_hearts > 0:
            self.increase_hearts(player, new_hearts)
            return new_hearts
        return 0

    def level_up(self, player_id: int) -> int:
        player = self.get_player(player_id)
        new_level = player.calc_level()
        if new_level != player.level:
            player.level = new_level
            self._update(player)
        return new_level

    def place(self, player_id: int) -> int:
        suffix_map = {'0': 'th', '1': 'th', '2': 'nd', '3': 'rd', '4': 'th', '5': 'th',
                      '6': 'th', '7': 'th', '8': 'th', '9': 'th', 'first': 'st'}
        place = 1
        player = self.stats[player_id]
        for player_i in self.stats.values():
            if player_i.score > player.score:
                place += 1
        suffix_key = str(place)
        if (place == 1) or ((suffix_key[-1] == '1') and (len(suffix_key) > 2)):
            suffix_key = 'first'
        else:
            suffix_key = suffix_key[-1]
        return str(place) + suffix_map[suffix_key]

    def _create_player(self, player_id: int) -> Player:
        player = Player(len(self.stats), player_id, 0, 0, 0, 0, 0, 0)
        self.stats[player_id] = player
        self._update(player)
        return player

    def _update(self, player: Player) -> None:
        data = player.format()
        with open(str(self.file), 'r+') as f:
            f.seek(player.index * len(data))
            f.write(data)
