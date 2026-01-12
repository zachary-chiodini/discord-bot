from random import randint
from typing import Dict, Generator, Union

from discord import Color, Embed, File, Guild, Member, TextChannel, User

from npc import NPC, Skyevolutrex
from setup import Setup
from stats import Stats


class Game:

    Gamer = Union[Member, User]

    def __init__(self, guild: Guild):
        self.npcs: Dict[int, NPC] = {}
        self.roles = {}
        self.setup = Setup(guild, self.roles)
        self.stats = Stats()
        self._npcs = {Skyevolutrex.alias: Skyevolutrex}

    async def add_heart(self, member: Gamer) -> None:
        player = self.stats.get_player(member.id)
        if player.health == 10:
            return None
        if player.health == 0:
            new_role = self.roles['❤️']
            image = 'heart1'
            title, note = 'Animation', 'just animated!'
        elif 0 < player.health < 10:
            new_role = self.roles['❤️' * (player.health + 1)]
            image = f"heart{player.health + 1}"
            if player.health + 1 == 10:
                title, note = 'Achieved Maximum Potency', 'achieved maximum potency!'
            else:
                title, note = 'Got a Heart!', f"got +1 {self.roles['❤️'].mention}!"
        elif player.health == -1:
            new_role = self.roles['💀']
            image = 'skull'
            title, note = 'Transmutation', 'is liminal.'
        else:
            new_role = self.roles['👻' * abs(player.health + 1)]
            image = f"ghost{abs(player.health + 1)}"
            title, note = 'Rematerialization', 'is rematerializing!'
        if isinstance(member, User):
            name = f"**{member.name}**"
            author = member.name
            avatar = member.avatar
        else:
            member = await member.guild.fetch_member(member.id)
            name = member.mention
            author = member.display_name
            avatar = member.display_avatar
            for role in member.roles:
                if role in self.setup.lives:
                    await member.remove_roles(role)
                    break
            await member.add_roles(new_role)
        self.stats.increase_health(member.id, 1)
        file = File(f"database/images/{image}.png", filename=f"{image}.png")
        embed = Embed(title=title, description=f"{name} {note}\n**Vigor**{new_role.mention}", color=new_role.color)
        embed.set_image(url=f"attachment://{image}.png")
        embed.set_author(name=author, icon_url=avatar.url)
        await self.setup.guild.system_channel.send(embed=embed, file=file)
        return None

    async def decrease_posts(self, member: Gamer) -> None:
        await self.increase_posts(member, -1)
        return None

    async def decrease_reacts(self, member: Gamer) -> None:
        await self.increase_reacts(member, -1)
        return None

    async def decrease_score(self, member: Gamer, points: int) -> None:
        await self.increase_score(member, -points)
        return None

    async def delete(self, member: Gamer) -> None:
        self.stats.delete(member.id)
        return None

    async def increase_posts(self, member: Gamer, points: int = 1) -> None:
        self.stats.increase_posts(member.id, points)
        await self.level_up(member)
        return None

    async def increase_reacts(self, member: Gamer, points: int = 1) -> None:
        self.stats.increase_reacts(member.id, points)
        await self.level_up(member)
        return None

    async def increase_score(self, member: Gamer, points: int) -> None:
        self.stats.increase_score(member.id, points)
        await self.level_up(member)
        return None

    async def level_up(self, member: Gamer) -> int:
        player = self.stats.get_player(member.id)
        curr_lvl = player.level
        next_lvl = self.stats.level_up(member.id)
        if next_lvl != curr_lvl:
            if next_lvl > curr_lvl:
                title = 'New Level Unlocked'
                prefix = 'Up'
                if next_lvl > len(self.roles['Level']) - 1:
                    # Can't create 100+ roles in a row.
                    ref_role = self.roles['Level'][-1]
                    for i in range(len(self.roles['Level']), next_lvl + 1):
                        new_role = await self.setup.role(str(i), f"#{Color.random().value:06X}",
                            alias='Level', ref_role=ref_role)
                        ref_role = new_role
            else:
                title = 'Level Lost'
                prefix = 'Down'
            new_role = self.roles['Level'][next_lvl]
            old_role = self.roles['Level'][curr_lvl]
            if isinstance(member, User):
                author = member.name
                avatar = member.avatar
            else:
                author = member.display_name
                avatar = member.display_avatar
                await member.remove_roles(old_role)
                await member.add_roles(new_role)
            self.stats.level_up(member.id)
            image = str((next_lvl % 7) + 1)
            file = File(f"database/images/{image}.png", filename=f"{image}.png")
            note = f"{prefix}graded From Level {old_role.mention} to Level {new_role.mention}" 
            embed = Embed(title=title, description=note, color=new_role.color)
            embed.set_image(url=f"attachment://{image}.png")
            embed.set_author(name=author, icon_url=avatar.url)
            await self.setup.guild.system_channel.send(embed=embed, file=file)
            for _ in range(self.stats.level_hearts(member.id)):
                await self.add_heart(member)
        return None

    async def load_npcs(self) -> None:
        for webhook in await self.setup.guild.webhooks():
            if webhook.name in self._npcs:
                player = self.stats.get_player(webhook.id)
                self.npcs[webhook.id] = self._npcs[webhook.name](player, self.roles, webhook)
        return None

    async def remove_heart(self, member: Gamer) -> None:
        player = self.stats.get_player(member.id)
        if player.health == -3:
            if isinstance(member, User):
                await member.delete()
                return None
            await member.kick(reason='**Vigor**: -4')
            return None
        if player.health == 1:
            new_role = self.roles['💀']
            image = 'skull'
            title, note = 'Critical', 'is critical!'
        elif 1 < player.health <= 10:
            new_role = self.roles['❤️' * (player.health - 1)]
            image = f"heart{player.health - 1}"
            title, note = 'Ouch', f"lost -1 {self.roles['❤️'].mention}!"
        else:
            new_role = self.roles['👻' * abs(player.health - 1)]
            image = f"ghost{abs(player.health - 1)}"
            title, note = 'Transmogrification', 'is transmogrifying!'
        if isinstance(member, User):
            name = f"**{member.name}**"
            author = member.name
            avatar = member.avatar
        else:
            member = await member.guild.fetch_member(member.id)
            name = member.mention
            author = member.display_name
            avatar = member.display_avatar
            for role in member.roles:
                if role in self.setup.lives:
                    await member.remove_roles(role)
                    break
            await member.add_roles(new_role)
        self.stats.increase_health(member.id, -1)
        file = File(f"database/images/{image}.png", filename=f"{image}.png")
        embed = Embed(title=title, description=f"{name} {note}\n**Vigor**: {new_role.mention}", color=new_role.color)
        embed.set_image(url=f"attachment://{image}.png")
        embed.set_author(name=author, icon_url=avatar.url)
        await self.setup.guild.system_channel.send(embed=embed, file=file)
        return None

    def roll(self) -> Generator:
        # Come-out Roll
        point = randint(1, 6) + randint(1, 6)
        if (point == 7) or (point == 11):
            yield True
            return None
        if (point == 2) or (point == 3) or (point == 12):
            yield False
            return None
        # The Point Phase
        while True:
            score = randint(1, 6) + randint(1, 6)
            yield(score)
            if score == point:
                yield True
                break
            elif score == 7:
                yield False
                break
        return None

    async def spawn(self, channel: TextChannel, npc: type[NPC]) -> None:
        webhook = await self.setup.webhook(channel, npc)
        player = self.stats.create_player(webhook.id)
        new_npc = npc(player, self.roles, webhook)
        self.npcs[webhook.id] = new_npc
        await new_npc.send_passive_dialogue()
        return None
