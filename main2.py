from discord import Color, Guild, Role

from paint import Paint
from player import Player



class Item:

    def __init__(self, color: str, filename: str, points: int):
        self.color = color
        self.filename = filename
        self.points = points


class DiscordGame:
    ADMIN_ID = 1380323054479085648
    GUILD_ID = 1455730008273195032

    def __init__(self, guild: Guild):
        self.color = Paint()
        self.guild = guild
        self.items = {
            '❤️': Item('#BE1931', 'heart', 0),
            '👁️': Item('#87CEEB', 'eye', 10000),
            '🔫': Item('#808080', 'gun', 1000),
            '🪙': Item('#D4AF37', 'coin', 250),
            '💎': Item('#809CA7', 'charm', 25),
            '🪨': Item('#7DA27E', 'rune', 25),
            '📜': Item('#FFFFC5', 'scroll', 25),
            '🔮': Item('#D580FF', 'wand', 25)
        }
        self.roles = {}
        self.stats = {}
        self._collect_roles()
        self._collect_stats()

    async def create_all_channels() -> None:
        
        return None

    async def create_all_roles(self) -> None:
        await self.create_role('0', '#FF6600', alias='Level')
        await self.create_role('TOWG', '#4169E1', hoist=True)
        await self.create_role('Outsider', '#FF6600', hoist=True)
        await self.create_role('Hospitalized', '#00692B', hoist=True)
        await self.create_role('Psychotic', '#BF00FF', hoist=True)
        await self.create_role('Prisoner', '#964B00', hoist=True)
        await self.create_role('Solitary', '#000000', hoist=True)
        await self.create_role('Ghost', '#FFFFFF', hoist=True)
        for name, item in self.items.items:
            await self.create_role(name, item.color)
        return None

    def create_player(self, player_id: int) -> Player:
        player = Player(len(self.stats), player_id, 0, 0, 0, 0, 0, 0)
        player.update()
        self.stats[player_id] = player
        return player

    async def create_role(self, name: str, hex_code: str, alias='', hoist=False) -> Role:
        if len(self.guild.roles) == 250:
            try:
                color_role = self.guild.get_role(self.color.pop())
            except Exception as e:
                await self.guild.system_channel.send(f"ROLE LIMIT ENCOUNTERED\n{e}")
                return None
            await self.guild.system_channel.send(
                f"Maximum roles encountered. Deleted role {color_role.mention}.")
            await color_role.delete()
        new_role = await self.guild.create_role(name=name, color=Color.from_str(hex_code))
        new_role.edit(hoist=hoist)
        if alias:
            name = alias
        if name in self.roles:
            self.roles[name].add(new_role)
        else:
            self.roles[name] = {new_role}
        return new_role

    async def initialize(self) -> None:
        await self.create_all_roles()
        return None

    async def _collect_roles(self) -> None:
        for role in self.guild.roles:
            if role.name.isdigit():
                name = 'Level'
            else:
                name = role.name
            if name in self.roles:
                self.roles[name].add(role)
            else:
                self.roles[name] = {role}
        return None

    async def _collect_stats(self) -> None:
        if Player.file.exists:
            with open(str(Player.file)) as f:
                for i, line in enumerate(f.readlines()):
                    stats = line.split(',')
                    player_id = int(stats[0])
                    self.stats[player_id] = Player(i, *map(int, stats))
        else:
            Player.file.touch()
        return None
