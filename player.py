from math import sqrt


class Player:

    FILE = 'database/text_file/stats.txt'

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

    def __len__(self):
        return len(self.__dict__)

    def __iter__(self):
        return iter(self.__dict__.values())

    def calc_level(self) -> int:
        A = 9910.10197
        a, b, c  = A / 9801, 0.89797, self.score - 1
        x = 1 + (sqrt(abs(b*b - 4*a*c)) - b) / (2*a)
        level = int(x)
        if level > 100:
            level = 100
        return level

    def clear_score(self) -> None:
        self.score = 0
        self.update()
        return None

    def copy(self):
        return Player(*self)

    def decrease_health(self) -> None:
        self.health -= 1
        if not self.health:
            self.clear_score()
            self.level = 0
            self.level_heart = 0
        self.update()
        return None

    def decrease_score(self, points: int) -> None:
        if self.score - points > 0:
            self.score -= points
        else:
            self.score = 0
        self.update()
        return None

    def format(self,) -> str:
        return (f"{self.id:<20},"
                f"{self.health:<20},"
                f"{self.level:0>2},"
                f"{self.level_heart:0>13},"
                f"{self.reacts:0>13},"
                f"{self.score:0>13}\n")

    def get_health_str(self) -> str:
        if self.health:
            return self.health * '❤️'
        return '💀'

    def increase_health(self) -> None:
        self.health += 1
        self.update()
        return None

    def increase_posts(self, posts: int = 1) -> None:
        self.posts += posts
        self.increase_score(posts)
        return None

    def increase_score(self, points: int) -> None:
        self.score += points
        self.update()
        return None

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

    def update(self) -> None:
        with open(self.FILE, 'r+') as f:
            f.seek((self.index * len(self)))
            f.write(self.format())
