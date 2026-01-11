from typing import Set, Tuple

from discord import Color, Guild, Member
from emoji import distinct_emoji_list

from setup import Setup
from stats import Stats


class Game:

    def __init__(self, guild: Guild):
        self.roles = {}
        self.setup = Setup(guild, self.roles)
        self.stats = Stats()

    async def add_heart(self, member: Member) -> None:
        for role in member.roles.copy():
            if role.name.startswith('💀'):
                new_role = self.roles['❤️']
                image = 'heart1'
                title = 'Animation'
                notes = f"{member.mention} just animated!\n**Vigor**: {new_role.mention}"
                await member.remove_roles(role)
                break
            elif role.name.startswith('❤️'):
                count = role.name.count('❤️')
                if count == 10:
                    return None
                new_role = self.roles['❤️' * (count + 1)]
                image = f"heart{count + 1}"
                if (count + 1) == 10:
                    title = 'Achieved Maximum Potency'
                    notes = f"{member.mention} achieved maximum potency!\n**Vigor**: {new_role.mention}"
                else:
                    title = 'Got a Heart!'
                    notes = f"{member.mention} got +1 ❤️!\n**Vigor**: {new_role.mention}"
                await member.remove_roles(role)
                break
            elif role.name.startswith('👻'):
                count = role.name.count('👻')
                if count > 1:
                    new_role = self.roles['👻' * (count - 1)]
                    image = f"ghost{count - 1}"
                    title = 'Rematerialization'
                    notes = f"{member.mention} is rematerializing!\n**Vigor**: {'👻' * (count - 1)}"
                else:
                    new_role = self.roles['💀']
                    image = 'meilanliu'
                    title = 'Transmutation'
                    notes = f"{member.mention} is liminal.\n**Vigor**: 💀"
                    await member.remove_roles(*[role for role in member.roles if role.name in self.prime])
                    await member.add_roles(self.roles['Hospitalized'])
                await member.remove_roles(role)
                break
        else:
            new_role = self.roles['❤️']
            title = 'Got a Heart!'
            image = 'heart1'
            notes = f"{member.mention} got +1 ❤️!\n**Vigor**: {new_role.mention}"
        await member.add_roles(new_role)
        await self.setup.send_img(
            new_role, member.guild.system_channel, image, notes, title, member)
        return None

    async def decrease_posts(self, member: Member) -> None:
        await self.increase_posts(member, -1)
        return None

    async def decrease_reacts(self, member: Member) -> None:
        await self.increase_reacts(member, -1)
        return None

    async def decrease_score(self, member: Member, points: int) -> None:
        await self.increase_score(member, -points)
        return None

    async def delete(self, member: Member) -> None:
        self.stats.delete(member.id)
        return None

    async def increase_posts(self, member: Member, points: int = 1) -> None:
        self.stats.increase_posts(member.id, points)
        await self.level_up(member)
        return None

    async def increase_reacts(self, member: Member, points: int = 1) -> None:
        self.stats.increase_reacts(member.id, points)
        await self.level_up(member)
        return None

    async def increase_score(self, member: Member, points: int) -> None:
        self.stats.increase_score(member.id, points)
        await self.level_up(member)
        return None

    async def level_up(self, member: Member) -> int:
        for old_role in member.roles:
            if old_role in self.roles['Level']:
                break
        else:
            old_role = self.roles['Level'][0]
        curr_lvl = int(old_role.name)
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
            await member.remove_roles(old_role)
            await member.add_roles(new_role)
            self.stats.level_up(member.id)
            note = f"{prefix}graded From Level {old_role.mention} to Level {new_role.mention}" 
            channel = member.guild.system_channel
            await self.setup.send_img(new_role, channel, str((next_lvl % 7) + 1), note, title, member)
            for _ in range(self.stats.level_hearts(member.id)):
                member = await member.guild.fetch_member(member.id)
                await self.add_heart(member)
        return None

    async def remove_heart(self, member: Member) -> None:
        for role in member.roles:
            if role.name.startswith('💀'):
                new_role = self.roles['👻']
                image = 'death'
                title = 'Dead'
                notes = f"{member.mention} just died!\n**Vigor**: {new_role.mention}"
                await member.remove_roles(*[role for role in member.roles if role.name in self.prime])
                await member.add_roles(self.roles['Ghost'])
                break
            elif role.name.startswith('❤️'):
                count = role.name.count('❤️')
                if count > 1:
                    image = f"heart{count - 1}"
                    new_role = self.roles['❤️' * (count - 1)]
                    title = 'Ouch'
                    notes = f"{member.mention} lost a heart!\n**Vigor**: {new_role.mention}"
                else:
                    image = 'skull'
                    new_role = self.roles['💀']
                    title = 'Critical'
                    notes = f"{member.mention} is critical!\n**Vigor**: {new_role.mention}"
                    await member.remove_roles(*[role for role in member.roles if role.name in self.prime])
                    await member.add_roles(self.roles['Hospitalized'])
                break
            elif role.name.startswith('👻'):
                count = role.name.count('👻')
                if count == 3:
                    await member.kick(reason='**Vigor**: -6')
                    return None
                new_role = self.roles['👻' * (count + 1)]
                image = f"ghost{count + 1}"
                title = 'Transmogrification'
                notes = f"{member.mention} is transmogrifying!\n**Vigor**: {new_role.mention}"
                break
        await member.remove_roles(role)
        await member.add_roles(new_role)
        await self.setup.send_img(
            new_role, member.guild.system_channel, image, notes, title, member)
