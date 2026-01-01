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

    def calc_level(self) -> int:
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

    def get_health_str(self) -> str:
        if self.health:
            return self.health * '❤️'
        return '💀'

    def level_up(self) -> int:
        next_lvl = self.calc_level()
        prev_lvl = self.level
        if next_lvl != prev_lvl:
            self.level = next_lvl
            lvls_since_heart = next_lvl - self.level_heart
            if (next_lvl == 1) & (self.level_heart == 0):
                # First level gets a health.
                self.health += 1
            elif (lvls_since_heart > 0) and (lvls_since_heart == 10):
                self.health += 1
                self.level_heart = next_lvl
            self.update()
            return bool(next_lvl > prev_lvl)
        return -1
