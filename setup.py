from asyncio import sleep
from typing import Dict, List, Optional, Union

from discord import (CategoryChannel, Color, Embed, File, Guild, Member, Permissions,
    PermissionOverwrite, Role, TextChannel)

class Item:

    def __init__(self, color: str, name: str, points: int, price: Union[int, str],
                 desc: str = '', perms: Optional[Permissions] = None):
        self.color = color
        self.desc = desc
        self.name = name
        self.points = points
        self.price = price
        self.perms = perms


class Setup:

    Roles = Dict[str, Union[Role, List[Role]]]

    def __init__(self, guild: Guild, roles: Roles):
        self.admin = {'🐈': Item('#FFFF00', 'neko', 9999, '♾️',
            '🌟 Imbues owner with God-like prowess 🦄🌈✨', Permissions(administrator=True))}
        self.coins = {'🪙🪙🪙🪙🪙': 'coin5', '🪙🪙🪙🪙': 'coin4', '🪙🪙🪙': 'coin3',
            '🪙🪙': 'coin2', '🪙': 'coin1'}
        self.extra = {'🪙': Item('', '', 250, ''), '❤️': Item('', '', 250, '')}
        self.guild = guild
        self.items = {
            '🎖️': Item('#7851A9', 'medal', 1000, '♾️',
                '⭐ Identifies top achievers\n⚠️ **Extra**: Acts as a shield when critical'),
            '⭐': Item('#D4AF37', 'star', 500, '♾️', '⭐ Means you did a good job!'),
            '🪬': Item('#917EB3', 'idol', 1000, '♾️', '⭐ Enables one to enter the church'),
            '👺': Item('#000000', 'mask', 0, 4,
                '⭐ Causes transitory intermittent blindness\n⚠️ **Removes**: ❤️'),
            '🛡️': Item('#006769', 'shield', 250, 4,
                '⭐ Shields wearer from an attack\n⚠️ **Extra**: Blocks imprisonment'),
            '☣️': Item('#78443E', 'virus', -10, 4,
                '⭐ Temporarily removes -10 points per second\n⚠️ **Removes**: ❤️'),
            '☢️': Item('#FAE500', 'waste', -10, 4,
                '⭐ Temporarily removes -10 points per second\n⚠️ **Removes**: ❤️'),
            '🔫': Item('#808080', 'gun', 500, 4,
                '⭐ **Removes**: ❤️❤️\n⚠️ **Extra**: May cause bleeding 🩸⏱️'),
            '🔪': Item('#401B1B', 'knife', 250, 2,
                '⭐ **Removes**: ❤️\n⚠️ **Extra**: May cause bleeding 🩸⏱️'),
            '🍅': Item('#401B1B', 'tomato', -250, 1,
                '⭐ **Removes**: 250 Points\n⚠️ **Extra**: Mortification'),
        }
        self.lives = {'❤️': 'heart1', '❤️❤️': 'heart2', '❤️❤️❤️': 'heart3', '❤️❤️❤️❤️': 'heart4',
            '❤️❤️❤️❤️❤️': 'heart5', '❤️❤️❤️❤️❤️❤️': 'heart6', '❤️❤️❤️❤️❤️❤️❤️': 'heart7',
            '❤️❤️❤️❤️❤️❤️❤️❤️': 'heart8', '❤️❤️❤️❤️❤️❤️❤️❤️❤️': 'heart9',
            '❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️': 'heart10', '💀': 'skull', '👻': 'ghost1',
            '👻👻': 'ghost2', '👻👻👻': 'ghost3'}
        self.roles = roles
        self.rules = ['no-anime', 'no-bullying', 'no-gore', 'no-nudes']
        # Note: Permission roles are overly complicated
        # Creating stacked items that act as combined permissions is way more complicated
        # but it looks cool
        self.app = Permissions(use_application_commands=True)
        self.base = Permissions(add_reactions=True, attach_files=True, change_nickname=True,
            connect=True, create_polls=True, create_public_threads=True, embed_links=True,
            send_messages=True, send_messages_in_threads=True, use_application_commands=True,
            use_external_emojis=True, use_external_stickers=True)
        self.mog = Permissions(change_nickname=True)
        self.post = Permissions(create_polls=True, create_public_threads=True,
            send_messages=True, send_messages_in_threads=True)
        self.post_and_view = PermissionOverwrite(view_channel=True, send_messages=True,
            add_reactions=True, create_polls=True, create_public_threads=True,
            send_messages_in_threads=True)
        self.react = Permissions(add_reactions=True)
        self.share = Permissions(attach_files=True, connect=True, embed_links=True,
            use_external_emojis=True, use_external_stickers=True)
        self.post_limited = PermissionOverwrite(view_channel=True, send_messages=True)
        self.view = PermissionOverwrite(view_channel=True)
        self.view_only = PermissionOverwrite(view_channel=True, send_messages=False,
            create_public_threads=False, create_polls=False)
        self.view_only_channel = {self.guild.default_role: PermissionOverwrite(
            send_messages=False, create_public_threads=False, create_polls=False)}
        self.perm_stacks = {
            '📜🔮💎🪨🕹️': Item('#DFFF00', 'scrollwandcharmruneremote', 0, 0, '', self.base),
            '🔮💎🪨🕹️': Item('#7A1F3D', 'wandcharmruneremote', 0, 0, '',
                Permissions(self.base.value & ~self.mog.value)),
            '📜🔮🪨🕹️': Item('#FFE135', 'scrollwandruneremote', 0, 0, '',
                Permissions(self.base.value & ~self.react.value)),
            '📜💎🪨🕹️': Item('#40E0D0', 'scrollcharmruneremote', 0, 0, '',
                Permissions(self.base.value & ~self.share.value)),
            '📜🔮💎🕹️': Item('#FA8072', 'scrollwandcharmremote', 0, 0, '',
                Permissions(self.base.value & ~self.post.value)),
            '📜🔮💎🪨': Item('#737C3E', 'scrollwandcharmrune', 0, 0, '',
                Permissions(self.base.value & ~self.app.value)),
            '🔮💎🕹️': Item('#065535', 'wandcharmremote', 0, 0, '',
                Permissions(self.app.value | self.react.value | self.share.value)),
            '🔮🪨🕹️': Item('#00FFFF', 'wandruneremote', 0, 0, '',
                Permissions(self.app.value | self.post.value | self.share.value)),
            '📜💎🕹️': Item('#CCCCFF', 'scrollcharmremote', 0, 0, '',
                Permissions(self.app.value | self.mog.value | self.react.value)),
            '📜🔮🕹️': Item('#CD7F32', 'scrollwandremote', 0, 0, '',
                Permissions(self.app.value | self.mog.value | self.share.value)),
            '📜🪨🕹️': Item('#E97451', 'scrollruneremote', 0, 0, '',
                Permissions(self.app.value | self.mog.value | self.post.value)),
            '💎🪨🕹️': Item('#954535', 'charmruneremote', 0, 0, '',
                Permissions(self.app.value | self.post.value | self.react.value)),
            '📜💎🪨': Item('#9A2A2A', 'scrollcharmrune', 0, 0, '',
                Permissions(self.mog.value | self.post.value | self.react.value)),
            '📜🔮🪨': Item('#CC7722', 'scrollwandrune', 0, 0, '',
                Permissions(self.mog.value | self.post.value | self.share.value)),
            '🔮💎🪨': Item('#A0522D', 'wandcharmrune', 0, 0, '',
                Permissions(self.post.value | self.react.value | self.share.value)),
            '📜🔮💎': Item('#8A9A5B', 'scrollwandcharm', 0, 0, '',
                Permissions(self.mog.value | self.react.value | self.share.value)),
            '📜💎': Item('#7FFFD4', 'scrollcharm', 0, 0, '',
                Permissions(self.mog.value | self.react.value)),
            '🔮💎': Item('#008080', 'wandcharm', 0, 0, '',
                Permissions(self.react.value | self.share.value)),
            '📜🔮': Item('#FBCEB1', 'scrollwand', 0, 0, '',
                Permissions(self.mog.value | self.share.value)),
            '🪨🕹️': Item('#DA70D6', 'runeremote', 0, 0, '',
                Permissions(self.app.value | self.post.value)),
            '💎🪨': Item('#AA98A9', 'charmrune', 0, 0, '',
                Permissions(self.react.value | self.post.value)),
            '🔮🪨': Item('#FFBF00', 'wandrune', 0, 0, '',
                Permissions(self.post.value | self.share.value)),
            '📜🪨': Item('#FDDA0D', 'scrollrune', 0, 0, '',
                Permissions(self.mog.value | self.post.value)),
            '💎🕹️': Item('#B4C424', 'charmremote', 0, 0, '',
                Permissions(self.app.value | self.react.value)),
            '🔮🕹️': Item('#FCF55F', 'wandremote', 0, 0, '',
                Permissions(self.app.value | self.share.value)),
            '📜🕹️': Item('#EDEADE', 'scrollremote', 0, 0, '',
                Permissions(self.app.value | self.mog.value))
        }
        self.perm_single_items = {
            '📜': Item('#FFFFC5', 'scroll', 100, 4, '⭐ Enables reader to change their name',
                self.mog),
            '🔮': Item('#D580FF', 'wand', 50, 2,
                ('⭐ Enables caster to attach files, connect to voice channels, embed links '
                 'and use external emojis and stickers'), self.share),
            '💎': Item('#809CA7', 'charm', 75, 3, '⭐ Enables wearer to react', self.react),
            '🪨': Item('#7DA27E', 'rune', 25, 1, '⭐ Enables holder to post', self.post),
            '🕹️': Item('#4169E1', 'remote', 25, 1,
                f'⭐ Enables user to control {self.guild.me.mention} with /', self.app)}
        self.perm_items = self.perm_stacks | self.perm_single_items
        self.all_items = self.admin | self.extra | self.items | self.perm_items
        self.primary_roles = {
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
        self._collect_roles()

    async def alert_channel(self, category: CategoryChannel, filename: str,
            note: str, role: Role, title: str) -> None:
        channel = await category.create_text_channel(
            name=title, overwrites=self.view_only_channel | {role: self.view})
        await self.send_img(role, filename, note, role.name, channel=channel)
        return None

    async def all(self) -> str:
        await self._all_roles()
        await self._all_channels()
        return 'Game initialized.'

    async def bulletin(self) -> None:
        bulletin = await self.guild.create_category('🧾📌BULLETIN BOARD🗺️🗡️⁉️')
        note = (f"⭐ You're an {self.roles['Outsider'].mention} 🌿🦥\n"
            f"⭐ Speak to a {self.roles['TOWG'].mention} citizen ☝🤓")
        await self.alert_channel(
            bulletin, 'meilanliu', note, self.roles['Outsider'], '🦧-outsider⚠️')
        note = f"⭐ Use 🕹️ to control {self.guild.me.mention} with / ☝🤓"
        await self.alert_channel(
            bulletin, 'bot', note, self.roles['🕹️'], '🕹️-commands')
        note = (f"⭐ Your're {self.roles['Hospitalized'].mention} 👩🏻‍⚕️💉\n"
            f"⭐ Speak to a {self.roles['Nurse'].mention} ☝🤓")
        await self.alert_channel(
            bulletin, 'hospital', note, self.roles['Hospitalized'], '💀-hospitalized⚠️')
        note = (f"⭐ Your're {self.roles['Psychotic'].mention} 📋🩻\n"
            f"⭐ Speak to a {self.roles['Scientist'].mention} ☝🤓")
        await self.alert_channel(
            bulletin, 'psycho', note, self.roles['Psychotic'], '🎭-psychotic⚠️')
        note = (f"⭐ Your're a {self.roles['Prisoner'].mention} 🐎💂🏼\n"
            f"⭐ Speak to a {self.roles['Guard'].mention} ☝🤓")
        await self.alert_channel(
            bulletin, 'prison', note, self.roles['Prisoner'], '🪳-prisoner⚠️')
        note = (f"⭐ Your're in {self.roles['Solitary'].mention} 🔒⛓️\n"
            f"⭐ Speak to a {self.roles['Priest'].mention} ☝🤓")
        await self.alert_channel(
            bulletin, 'solitary', note, self.roles['Solitary'], '👤-solitary⚠️')
        note = (f"⭐ Your're a {self.roles['Ghost'].mention} 🕊️🪦\n"
            f"⭐ Speak to a {self.roles['Ghost'].mention} ☝🤓")
        await self.alert_channel(
            bulletin, 'death', note, self.roles['Ghost'], '👻-ghost⚠️')
        # Market Channel
        channel = await bulletin.create_text_channel('🌳🏬-market',
            overwrites=self.view_only_channel | self._main_perms() | {
                self.roles['Outsider']: self.view})
        for name, item in self.admin.items():
            await self.send_img(self.roles[name], item.name,
                f"{item.desc}\n🅿️ **Points**: {item.points}\n🪙 **Coins**: {item.price}",
                f"God-like Neko {name}", channel=channel)
        for name, item in self.items.items():
            await self.send_img(self.roles[name], f"{item.name}1",
                f"{item.desc}\n🅿️ **Points**: {item.points}\n🪙 **Coins**: {item.price}",
                f"{item.name.title()} {name}", channel=channel)
        for name, item in self.perm_single_items.items():
            await self.send_img(self.roles[name], item.name,
                f"{item.desc}\n🅿️ **Points**: {item.points}\n🪙 **Coins**: {item.price}",
                f"{item.name.title()} {name}", channel=channel)
        return None

    async def hospital(self) -> None:
        hospital_perms = {self.roles['Scientist']: self.view,
            self.roles['Nurse']: self.view, self.roles['Hospitalized']: self.view}
        category = await self.guild.create_category('🏥🚑Hospital University🧬🔬')
        await category.create_text_channel(
            name='🛋️visitation💔🌡️💀', overwrites=hospital_perms | self._main_perms())
        await category.create_text_channel(
            name='👥building-center💊', overwrites=hospital_perms)
        cafeteria = await category.create_text_channel(
            name='🍽️cafeteria🍊🥪🧃', overwrites=self.view_only_channel | hospital_perms)
        await self.send_img(self.roles['Nurse'], 'sloppyjoes', '', '', channel=cafeteria)
        await category.create_text_channel(
            name='🩻padded-cell📋🧑🏻‍🔬',
            overwrites=self.view_only_channel | hospital_perms | {
                self.roles['Scientist']: self.post_and_view,
                self.roles['Psychotic']: self.post_limited})
        await category.create_text_channel(
            name='🔒doctors-office💉',
            overwrites=self.view_only_channel | hospital_perms | {
                self.roles['Scientist']: self.post_and_view, self.roles['Nurse']: self.post_and_view})
        await category.create_voice_channel(
            name='🛋️visitation💔🌡️💀', overwrites=hospital_perms | self._main_perms())
        return None

    async def inventory(self) -> None:
        category = await self.guild.create_category('🎒👛Special Items💼🍬👝')
        for name, filename in self.lives.items():
            channel = await category.create_text_channel(
                name=name, overwrites=self.view_only_channel | {self.roles[name]: self.view})
            await self.send_img(
                self.roles[name], filename, self.roles[name].mention, '', channel=channel)
        for name, filename in self.coins.items():
            channel = await category.create_text_channel(
                name=name, overwrites=self.view_only_channel | {self.roles[name]: self.view})
            await self.send_img(
                self.roles[name], filename, self.roles[name].mention, '', channel=channel)
        for name, item in self.perm_single_items.items():
            channel = await category.create_text_channel(
                name=name, overwrites=self.view_only_channel | {self.roles[name]: self.view})
            await self.send_img(self.roles[name], item.name, self.roles[name].mention, '', channel=channel)
        for name, item in self.perm_stacks.items():
            channel = await category.create_text_channel(
                name=name, overwrites=self.view_only_channel | {self.roles[name]: self.view})
            await self.send_img(self.roles[name], item.name, self.roles[name].mention, '', channel=channel)
        category = await self.guild.create_category('🧰⚙️Tactical Items📕🛠️🪖')
        for name, item in self.items.items():
            for i in range(1, 4):
                role_name = name * i
                channel = await category.create_text_channel(
                    name=role_name, overwrites=self.view_only_channel | {
                        self.roles[role_name]: self.view})
                await self.send_img(
                    self.roles[role_name], f"{item.name}{i}", self.roles[role_name].mention,
                    '', channel=channel)
        return None

    async def main_channels(self) -> None:
        category = await self.guild.create_category(
            '🏰🐉Town Square🏤🏦🌈🏨', overwrites=self._main_perms())
        channel = await category.create_text_channel(name='🏙️center👥⛲🦢🏞️')
        for name in ['🎼orchestra👥📻🎵', '🎞️playhouse📽️🎬🎭',
                '🌃blue🍇bar🍺🥃🥜', '💨blue🫐smoke🌬️🍃', '🏚️blue🟦block🍚🗞️',
                '🫂emotional-supp❤️‍🩹']:
            await category.create_text_channel(name=name)
        await category.create_voice_channel(name='🏰town-hall🧝🏼‍♀️🤴🏻🧝🏼‍♀️')
        await category.create_voice_channel(name='🆘crisis-assistance☎️')
        return None

    async def outskirts(self) -> None:
        outsider_perms = self._main_perms() | {self.roles['Outsider']: self.view}
        category = await self.guild.create_category(
            '🏕️🦌Outskirts🌿🐦🌳🌰🐿️', overwrites=outsider_perms)
        channel = await category.create_text_channel(name='🐾🍂wilderness⛰️🍄')
        system_channel = await category.create_text_channel(name='🌀🪞gay-portal🪞🌀')
        await self.guild.edit(system_channel=system_channel)
        await category.create_voice_channel(name='🐾🍂wilderness⛰️🍄')
        return None

    async def prison(self) -> None:
        prison_perms = {self.roles['Guard']: self.view, self.roles['Prisoner']: self.view}
        category = await self.guild.create_category('🏢🚓Gay Factory Prison 👮🏻🇺🇸')
        await category.create_text_channel(
            name='🪑visitation💂🏻⛓️😡', overwrites=prison_perms | self._main_perms())
        await category.create_text_channel(
            name='👥the-yard🏋🏿👊🏿🤬', overwrites=prison_perms)
        cafeteria = await category.create_text_channel(
            name='🍽️chow-hall🫓🥣🥔', overwrites=self.view_only_channel | prison_perms)
        await self.send_img(self.roles['Guard'], 'prisonfood', '', '', channel=cafeteria)
        await category.create_text_channel(
            name='🕳️the-hole🫷🏿😫🫸🏿', overwrites=self.view_only_channel | prison_perms | {
                self.roles['Solitary']: self.post_limited, self.roles['Guard']: self.post_and_view,
                self.roles['Priest']: self.post_and_view})
        await category.create_text_channel(
            name='🔒wardens-office🗝️', overwrites=self.view_only_channel | prison_perms | {
                self.roles['Guard']: self.post_and_view})
        await category.create_voice_channel('🪑visitation💂🏻⛓️😡', overwrites=self._main_perms())
        return None

    async def role(self, name: str, hex_code: str,
            alias='', hoist=False, perms: Optional[Permissions] = None,
            ref_role: Optional[Role] = None) -> Role:
        # Maximum of 250 roles per guild.
        if len(self.guild.roles) == 250:
            await self.guild.system_channel.send(f"ERROR: ROLE LIMIT ENCOUNTERED")
            return None
        new_role = await self.guild.create_role(
            name=name, color=Color.from_str(hex_code), hoist=hoist)
        if alias:
            # These are only Level roles (alias='Level').
            self.roles[alias].append(new_role)
        else:
            self.roles[name] = new_role
        if perms:
            await new_role.edit(permissions=perms)
        if ref_role:
            # New role is positioned under reference role.
            roles = [role for role in self.guild.roles if role.id != new_role.id]
            for index, role in enumerate(roles):
                if role.id == ref_role.id:
                    break
            roles.insert(index, new_role)
            await self.guild.edit_role_positions(
                positions={r: i for i, r in enumerate(roles)})
        # Discord rate limits role creation.
        await sleep(2)
        return new_role

    async def rules(self) -> None:
        rules_perms = self.view_only_channel | self._main_perms() | {self.roles['Guard']: self.post_and_view}
        category = await self.guild.create_category('🛡️⚔️COMMANDMENTS⚔️🛡️', overwrites=rules_perms)
        for rule in self.rules:
            await category.create_text_channel(name=f"⛔{rule}🗃️")
        return None

    async def send_img(
            self, color: Role, filename: str, note: str, title: str,
            author: Optional[Member] = None, channel: TextChannel = None) -> None:
        file = File(f"database/images/{filename}.png", filename=f"{filename}.png")
        embed = Embed(title=title, description=note, color=color.color)
        embed.set_image(url=f"attachment://{filename}.png")
        if author:
            embed.set_author(name=author.display_name, icon_url=author.display_avatar.url)
        if not channel:
            channel = self.guild.system_channel
        await channel.send(embed=embed, file=file)
        return None

    async def _all_channels(self) -> None:
        await self.bulletin()
        await self.outskirts()
        await self.rules()
        await self.inventory()
        await self.main_channels()
        await self.hospital()
        await self.prison()
        return None

    async def _all_roles(self) -> None:
        await self.guild.default_role.edit(permissions=Permissions(
            create_instant_invite = True, mention_everyone = True,
            read_message_history = True, send_voice_messages = True, speak = True,
            stream = True, use_voice_activation = True))
        if 'Level' not in self.roles:
            await self.role('0', '#FF6600', alias='Level')
        for name, item in self.admin.items():
            if name not in self.roles:
                await self.role(name, item.color, hoist=True, perms=item.perms)
        for name in self.lives:
            if name not in self.roles:
                await self.role(name, '#BE1931')
        for name, item in self.items.items():
            if name not in self.roles:
                # Allows stacking 3 of the same item.
                for i in range(1, 4):
                    await self.role(name * i, item.color)
        for name in self.coins:
            if name not in self.roles:
                await self.role(name, '#D4AF37')
        for name, item in self.perm_stacks.items():
            if name not in self.roles:
                await self.role(name, item.color, perms=item.perms)
        for name, item in self.perm_single_items.items():
            if name not in self.roles:
                await self.role(name, item.color, perms=item.perms)
        for name, hex_code in self.primary_roles.items():
            if name not in self.roles:
                await self.role(name, hex_code, hoist=True)
        return None

    def _main_perms(self) -> Dict[Role, PermissionOverwrite]:
        return {self.roles['Priest']: self.view, self.roles['Scientist']: self.view,
            self.roles['Guard']: self.view, self.roles['Nurse']: self.view,
            self.roles['TOWG']: self.view}

    def _collect_roles(self) -> None:
        self.roles['Level'] = set()
        for role in self.guild.roles:
            if role.name.isdigit():
                self.roles['Level'].add(role)
            else:
                self.roles[role.name] = role
        self.roles['Level'] = sorted(self.roles['Level'],key=lambda r: int(r.name))
        return None
