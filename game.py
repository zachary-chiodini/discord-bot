from asyncio import sleep
from typing import Dict, Optional, Union

from discord import (CategoryChannel, Color, Embed, File, Guild,
    Member, Permissions, PermissionOverwrite, Role, TextChannel)
from discord.ext.commands import Context

from paint import Paint
from stats import Stats


class Item:

    def __init__(self, color: str, desc: str, filename: str, points: int, price: Union[int, str],
                 perms: Optional[Permissions] = None):
        self.color = color
        self.desc = desc
        self.filename = filename
        self.points = points
        self.price = price
        self.perms = perms


class Game:

    def __init__(self, guild: Guild):
        self.admin = ('🐈', Item('#FFFF00',
            '🌟 Imbues owner with God-like prowess 🦄🌈✨',
            'neko', 99999, '♾️', Permissions(administrator=True)))
        self.guild = guild
        self.items = {
            '👺': Item('#000000',
                '⭐ Causes transitory intermittent blindness\n⚠️ **Removes**: ❤️',
                'mask', 0, 4, Permissions(read_message_history=False, read_messages=False)),
            '❤️': Item('#BE1931', '⭐ Used to stay alive\n⚠️ **Extra**: +1 ❤️ every 10 levels',
                'heart', 250, '♾️'),
            '🪬': Item('#917EB3', '⭐ Enables one to enter the church',
                'idol', 1000, '♾️'),
            '🛡️': Item('#006769',
                '⭐ Shields wearer from an attack\n⚠️ **Extra**: Blocks imprisonment',
                'shield', 250, 4),
            '☣️': Item('#78443E',
                '⭐ Temporarily removes -1 points per second\n⚠️ **Removes**: ❤️',
                'virus', -10, 4),
            '☢️': Item('#FAE500',
                '⭐ Temporarily removes -1 points per second\n⚠️ **Removes**: ❤️',
                'waste', -10, 4),
            '🔫': Item('#808080', '⭐ **Removes**: ❤️❤️\n⚠️ **Extra**: May cause bleeding 🩸⏱️',
                'gun', 250, 4),
            '🔪': Item('#401B1B', '⭐ **Removes**: ❤️\n⚠️ **Extra**: May cause bleeding 🩸⏱️',
                'knife', 250, 2),
            '🪙': Item('#D4AF37', '⭐ Used to purchase items ☝🤓', 'coin', 250, '♾️'),
            '📜': Item('#FFFFC5', '⭐ Enables reader to change their name', 'scroll', 100, 4,
                Permissions(change_nickname=True)),
            '💎': Item('#809CA7', '⭐ Enables holder to react', 'charm', 75, 3,
                Permissions(add_reactions=True)),
            '🔮': Item('#D580FF',
                '⭐ Enables caster to attach files, connect to voice channels, embed links and use external emojis and stickers',
                'wand', 50, 2, Permissions(attach_files=True, connect=True, embed_links=True,
                    use_external_emojis=True, use_external_stickers=True)),
            '🕹️': Item('#4169E1',
                f'⭐ Enables user to control {self.guild.me.mention} with /',
                'remote', 25, 1, Permissions(use_application_commands=True)),
            '🪨': Item('#7DA27E', '⭐ Enables holder to post', 'rune', 25, 1,
                Permissions(send_messages=True, send_messages_in_threads=True,
                    create_polls=True, create_public_threads=True))
        }
        self.paint = Paint()
        self.prime = {
            'Priest': '#67080B',
            'Scientist': '#DFFF00',
            'Guard': '#9EB37B',
            'Nurse':  '#FA82A2',
            'TOWG': '#4169E1',
            'Outsider': '#FF6600',
            'Hospitalized': '#00692B',
            'Psychotic': '#BF00FF',
            'Prisoner': '#964B00',
            'Solitary': '#000000',
            'Ghost': '#FFFFFF'
        }
        self.roles = {}
        self.stats = Stats()
        self.stackable = {'👺', '❤️', '🛡️', '☣️', '☢️', '🔫', '🔪'}
        self._post = PermissionOverwrite(view_channel=True, send_messages=True,
            add_reactions=True, create_polls=True, create_public_threads=True,
            create_private_threads=True)
        self._post_limited = PermissionOverwrite(view_channel=True, send_messages=True)
        self._view = PermissionOverwrite(view_channel=True)
        self._view_only = {self.guild.default_role: PermissionOverwrite(
            send_messages=False, create_public_threads=False, create_polls=False)}
        self._collect_roles()

    async def create_alert_channel(self, category: CategoryChannel,
            filename: str, note: str, role: Role, title: str) -> None:
        channel = await category.create_text_channel(
            name=title, overwrites= self._view_only | {role: self._view})
        await self.send_img(role, channel, filename, note, role.name)
        return None

    async def create_all_channels(self) -> None:
        await self.create_bulletin()
        await self.create_outskirts()
        await self.create_rules()
        await self.create_main_channels()
        await self.create_hospital()
        await self.create_prison()
        return None

    async def create_all_roles(self) -> None:
        await self.guild.default_role.edit(permissions=Permissions(
            create_instant_invite = True, mention_everyone = True,
            read_message_history = True, send_voice_messages = True, speak = True,
            stream = True, use_voice_activation = True))
        await self.create_role('0', '#FF6600', alias='Level')
        name, item = self.admin[0], self.admin[1]
        await self.create_role(name, item.color, hoist=True, perms=item.perms)
        for name, item in self.items.items():
            await self.create_role(name, item.color, perms=item.perms)
        for name, hex_code in self.prime.items():
            await self.create_role(name, hex_code, hoist=True)
        return None

    async def create_bulletin(self) -> None:
        bulletin = await self.guild.create_category('🧾📌BULLETIN BOARD🗺️🗡️⁉️')
        note = (f"⭐ You're an {self.roles['Outsider'].mention} 🌿🦥\n"
            f"⭐ Speak to a {self.roles['TOWG'].mention} citizen ☝🤓")
        await self.create_alert_channel(
            bulletin, 'meilanliu', note, self.roles['Outsider'], '🦧-outsider⚠️')
        note = f"⭐ Use 🕹️ to control {self.guild.me.mention} with / ☝🤓"
        await self.create_alert_channel(
            bulletin, 'bot', note, self.roles['🕹️'], '🕹️-commands')
        note = (f"⭐ Your're {self.roles['Hospitalized'].mention} 👩🏻‍⚕️💉\n"
            f"⭐ Speak to a {self.roles['Nurse'].mention} ☝🤓")
        await self.create_alert_channel(
            bulletin, 'hospital', note, self.roles['Hospitalized'], '😵-hospitalized⚠️')
        note = (f"⭐ Your're {self.roles['Psychotic'].mention} 📋🩻\n"
            f"⭐ Speak to a {self.roles['Scientist'].mention} ☝🤓")
        await self.create_alert_channel(
            bulletin, 'psycho', note, self.roles['Psychotic'], '🎭-psychotic⚠️')
        note = (f"⭐ Your're a {self.roles['Prisoner'].mention} 🐎💂🏼\n"
            f"⭐ Speak to a {self.roles['Guard'].mention} ☝🤓")
        await self.create_alert_channel(
            bulletin, 'prison', note, self.roles['Prisoner'], '🪳-prisoner⚠️')
        note = (f"⭐ Your're in {self.roles['Solitary'].mention} 🔒⛓️\n"
            f"⭐ Speak to a {self.roles['Priest'].mention} ☝🤓")
        await self.create_alert_channel(
            bulletin, 'solitary', note, self.roles['Solitary'], '💀-solitary⚠️')
        note = (f"⭐ Your're a {self.roles['Ghost'].mention} 🕊️🪦\n"
            f"⭐ Speak to a {self.roles['Ghost'].mention} ☝🤓")
        await self.create_alert_channel(
            bulletin, 'ghost', note, self.roles['Ghost'], '👻-ghost⚠️')
        # Market Channel
        market_perms = self._view_only | self._main_perms() | {self.roles['Outsider']: self._view}
        channel = await bulletin.create_text_channel('🌳🏬-market', overwrites=market_perms)
        name, item = self.admin[0], self.admin[1]
        await self.send_img(self.roles[name], channel, item.filename,
            f"{item.desc}\n🅿️ **Points**: {item.points}\n🪙 **Coins**: {item.price}",
            f"God-like Neko {name}")
        for name, item in self.items.items():
            await self.send_img(self.roles[name], channel, item.filename,
                f"{item.desc}\n🅿️ **Points**: {item.points}\n🪙 **Coins**: {item.price}",
                f"{item.filename.title()} {name}")
        return None

    async def create_color(self, context: Context, name: str, hex_code) -> str:
        role = await self.create_role(name, hex_code, ref_role=self.guild.me.top_role)
        self.paint.update(role.id, hex_code)
        await self.send_img(role, context.channel, hex_code.lstrip('#').upper(),
            f"**Created**: {role.mention}", '')
        return '**New Color Created!**'

    async def create_hospital(self) -> None:
        hospital_perms = {self.roles['Scientist']: self._view,
            self.roles['Nurse']: self._view, self.roles['Hospitalized']: self._view}
        category = await self.guild.create_category('🏥🚑Hospital University🧬🔬')
        await category.create_text_channel(
            name='🛋️visitation💔🌡️💀', overwrites=hospital_perms | self._main_perms())
        await category.create_text_channel(
            name='👥building-center💊', overwrites=hospital_perms)
        cafeteria = await category.create_text_channel(
            name='🍽️cafeteria🍊🥪🧃', overwrites=self._view_only | hospital_perms)
        await self.send_img(self.roles['Nurse'], cafeteria, 'sloppyjoes', '', '')
        await category.create_text_channel(
            name='🩻padded-cell📋🧑🏻‍🔬',
            overwrites=self._view_only | hospital_perms | {
                self.roles['Scientist']: self._post,
                self.roles['Psychotic']: self._post_limited})
        await category.create_text_channel(
            name='🔒doctors-office💉',
            overwrites=self._view_only | hospital_perms | {
                self.roles['Scientist']: self._post, self.roles['Nurse']: self._post})
        await category.create_voice_channel(
            name='🛋️visitation💔🌡️💀', overwrites=hospital_perms | self._main_perms())
        return None

    async def create_main_channels(self) -> None:
        category = await self.guild.create_category(
            '🏰🐉Town Square🏤🏦🌈🏨', overwrites=self._main_perms())
        for name in ['🏙️center👥⛲🦢🏞️', '🎼orchestra👥📻🎵', '🎞️playhouse📽️🎬🎭',
                '🌃blue🍇bar🍺🥃🥜', '💨blue🫐smoke🌬️🍃', '🏚️blue🟦block🍚🗞️',
                '🫂emotional-supp❤️‍🩹']:
            await category.create_text_channel(name=name)
        await category.create_voice_channel(name='🏰town-hall🧝🏼‍♀️🤴🏻🧝🏼‍♀️')
        await category.create_voice_channel(name='🆘crisis-assistance☎️')
        return None

    async def create_outskirts(self) -> None:
        outsider_perms = self._main_perms() | {self.roles['Outsider']: self._view}
        category = await self.guild.create_category(
            '🏕️🦌Outskirts🌿🐦🌳🌰🐿️', overwrites=outsider_perms)
        await category.create_text_channel(name='🐾🍂wilderness⛰️🍄')
        system_channel = await category.create_text_channel(name='🌀🪞gay-portal🪞🌀')
        await self.guild.edit(system_channel=system_channel)
        await category.create_voice_channel(name='🐾🍂wilderness⛰️🍄')
        return None

    async def create_prison(self) -> None:
        prison_perms = {self.roles['Guard']: self._view, self.roles['Prisoner']: self._view}
        category = await self.guild.create_category('🏢🚓Gay Factory Prison 👮🏻🇺🇸')
        await category.create_text_channel(
            name='🪑visitation💂🏻⛓️😡', overwrites=prison_perms | self._main_perms())
        await category.create_text_channel(
            name='👥the-yard🏋🏿👊🏿🤬', overwrites=prison_perms)
        cafeteria = await category.create_text_channel(
            name='🍽️chow-hall🫓🥣🥔', overwrites=self._view_only | prison_perms)
        await self.send_img(self.roles['Guard'], cafeteria, 'prisonfood', '', '')
        await category.create_text_channel(
            name='🕳️the-hole🫷🏿😫🫸🏿', overwrites=self._view_only | prison_perms | {
                self.roles['Solitary']: self._post_limited, self.roles['Guard']: self._post,
                self.roles['Priest']: self._post})
        await category.create_text_channel(
            name='🔒wardens-office🗝️', overwrites=self._view_only | prison_perms | {
                self.roles['Guard']: self._post})
        await category.create_voice_channel('🪑visitation💂🏻⛓️😡', overwrites=self._main_perms())
        return None

    async def create_role(self, name: str, hex_code: str,
            alias='', hoist=False, perms: Optional[Permissions] = None,
            ref_role: Optional[Role] = None) -> Role:
        if len(self.guild.roles) == 250:
            try:
                color_role = self.guild.get_role(self.paint.pop())
            except Exception as e:
                await self.guild.system_channel.send(f"ROLE LIMIT ENCOUNTERED\n{e}")
                return None
            await self.guild.system_channel.send(
                f"Maximum roles encountered. Deleted role {color_role.mention}.")
            await color_role.delete()
            await sleep(2)
        new_role = await self.guild.create_role(
            name=name, color=Color.from_str(hex_code), hoist=hoist)
        if alias:
            self.roles[alias].append(new_role)
        elif name in self.stackable:
            self.roles[name].add(new_role)
        else:
            self.roles[name] = new_role
        if perms:
            await new_role.edit(permissions=perms)
        if ref_role:
            roles = [role for role in self.guild.roles if role.id != new_role.id]
            for index, role in enumerate(roles):
                if role.id == ref_role.id:
                    break
            roles.insert(index, new_role)
            await self.guild.edit_role_positions(
                positions={r: i for i, r in enumerate(roles)})
        await sleep(2)
        return new_role

    async def create_rules(self) -> None:
        rules_perms = self._view_only | self._main_perms() | {self.roles['Guard']: self._post}
        category = await self.guild.create_category(
            '🛡️⚔️COMMANDMENTS⚔️🛡️', overwrites=rules_perms)
        for rule in ['no-anime', 'no-bullying', 'no-gore', 'no-nudes']:
            await category.create_text_channel(name=f"⛔{rule}🗃️")
        return None

    async def create_heart(self, member: Member, n: int = 1) -> None:
        guild_hearts =  self.roles['❤️']
        member_hearts = set()
        for role in member.roles:
            if role in guild_hearts:
                member_hearts.add(role)
        total_hearts = len(member_hearts) + n
        if total_hearts >= len(guild_hearts):
            for heart in guild_hearts:
                for _ in range(total_hearts - len(guild_hearts)):
                    await self.create_role('❤️', self.items['❤️'].color, ref_role=heart)
                break
        new_hearts = 0
        for new_role in self.roles['❤️']:
            if not member.get_role(new_role.id):
                await member.add_roles(new_role)
                new_hearts += 1
                if new_hearts == n:
                    break
        note = (f"Got +{n} {new_role.mention}!\n"
            f"Total: {self.stats.get_health_str(member.id)}")
        await self.send_img(
            new_role, member.guild.system_channel, 'heart', note, 'New Item', member)
        return None

    async def decrease_reacts(self, member: Member) -> None:
        await self.increase_reacts(member, -1)
        return None

    async def decrease_score(self, member: Member, points: int) -> None:
        await self.increase_score(member, -points)
        return None

    async def delete(self, member: Member) -> None:
        self.stats.delete_player(member.id)
        return None

    async def increase_posts(self, member: Member) -> None:
        self.stats.increase_posts(member.id)
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

    async def initialize(self) -> str:
        await self.create_all_roles()
        await self.create_all_channels()
        return 'Game initialized.'

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
                curr_len = len(self.roles['Level']) - 1
                if next_lvl > curr_len:
                    ref_role = old_role
                    for i in range(next_lvl - curr_len):
                        new_lvl = curr_len + i + 1
                        new_role = await self.create_role(str(new_lvl),
                            f"#{Color.random().value:06X}", alias='Level', ref_role=ref_role)
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
            await self.send_img(new_role, channel, str((next_lvl % 7) + 1), note, title, member)
            n_hearts = self.stats.level_hearts(member.id)
            if n_hearts:
                await self.create_heart(member, n_hearts)
        return None

    async def reset(self) -> str:
        m, n = 0, 0
        for role in self.guild.roles:
            if (role.id != self.guild.default_role.id) and (role.id != self.guild.me.top_role.id):
                await role.delete()
                await sleep(2)
                n += 1
        for channel in self.guild.channels:
            if channel.id != self.guild.system_channel.id:
                await channel.delete()
                await sleep(2)
                m += 1
        self.paint.reset()
        self.stats.reset()
        return f"Deleted {n} roles and {m} channels."

    async def send_img(self, color: Role, channel: TextChannel, filename: str,
            note: str, title: str, author: Optional[Member] = None) -> None:
        filepath = f"database/images/{filename}.png"
        file = File(filepath, filename=f"{filename}.png")
        embed = Embed(title=title, description=note, color=color.color)
        embed.set_image(url=f"attachment://{filename}.png")
        if author:
            embed.set_author(name=author.display_name, icon_url=author.display_avatar.url)
        await channel.send(embed=embed, file=file)
        return None

    def _collect_roles(self) -> None:
        self.roles['Level'] = set()
        for icon in self.stackable:
            self.roles[icon] = set()
        for role in self.guild.roles:
            if not self.paint.id_exists(role.id):
                if role.name.isdigit():
                    self.roles['Level'].add(role)
                elif role.name in self.roles:
                    self.roles[role.name].add(role)
                else:
                    self.roles[role.name] = role
        self.roles['Level'] = sorted(self.roles['Level'],key=lambda r: int(r.name))
        return None

    def _main_perms(self) -> Dict:
        return {self.roles['Priest']: self._view, self.roles['Scientist']: self._view,
            self.roles['Guard']: self._view, self.roles['Nurse']: self._view,
            self.roles['TOWG']: self._view}
