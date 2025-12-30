from math import sqrt

from player import Player


class Game:

    def __init__(self):
        self._stats = {}
        # Database
        with open(Player.FILE) as f:
            for i, line in enumerate(f.readlines()):
                stats = line.split(',')
                player_id = int(stats[0])
                self._stats[player_id] = Player(i, *map(int, stats))

    def get_place(self, player_id: int) -> int:
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
        return place + suffix_map[suffix_key]

    def get_player(self, player_id: int) -> Player:
        return self._stats[player_id]

    def create_player(self, player_id: int) -> Player:
        player = Player(len(self._stats), player_id, 0, 0, 0, 0, 0, 0)
        player.update()
        self._stats[player_id] = player
        return player

    def delete_player(self, player_id: int) -> None:
        del self._stats[player_id]
        # Rewrite file
        with open(Player.FILE, 'w') as f:
            for i, player in enumerate(self._stats.values()):
                player.index = i
                f.write(f"{player.format()}\n")
        return None
