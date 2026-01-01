from pathlib import Path

from player import Player


class Game:

    file = Path('database/files/stats.txt')

    def __init__(self):
        self._stats = {}
        if self.file.exists():
            with open(str(self.file)) as f:
                for i, line in enumerate(f.readlines()):
                    stats = line.split(',')
                    player_id = int(stats[0])
                    self._stats[player_id] = Player(i, *map(int, stats))
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
        del self._stats[player_id]
        with open(str(self.file), 'w') as f:
            for i, player in enumerate(self._stats.values()):
                player.index = i
                f.write(player.format())
        return None

    def get_player(self, player_id: int) -> Player:
        if player_id in self._stats:
            return self._stats[player_id]
        self._create_player(player_id)
        return self._stats[player_id]

    def increase_health(self, player_id: int) -> None:
        player = self.get_player(player_id)
        player.health += 1
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

    def place(self, player_id: int) -> int:
        suffix_map = {'0': 'th', '1': 'th', '2': 'nd', '3': 'rd', '4': 'th', '5': 'th',
                      '6': 'th', '7': 'th', '8': 'th', '9': 'th', 'first': 'st'}
        place = 1
        player = self._stats[player_id]
        for player_i in self._stats.values():
            if player_i.score > player.score:
                place += 1
        suffix_key = str(place)
        if (place == 1) or ((suffix_key[-1] == '1') and (len(suffix_key) > 2)):
            suffix_key = 'first'
        else:
            suffix_key = suffix_key[-1]
        return str(place) + suffix_map[suffix_key]

    def _create_player(self, player_id: int) -> Player:
        player = Player(len(self._stats), player_id, 0, 0, 0, 0, 0, 0)
        self._stats[player_id] = player
        self._update(player)
        return player

    def _update(self, player: Player) -> None:
        data = player.format()
        with open(str(self.file), 'r+') as f:
            f.seek(player.index * len(data))
            f.write(data)
