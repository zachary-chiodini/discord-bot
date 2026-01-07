from asyncio import sleep
from typing import Dict, Optional, Union

from discord import (CategoryChannel, Color, Embed, File, Guild,
    Member, Permissions, PermissionOverwrite, Role, TextChannel)
from discord.ext.commands import Context

from paint import Paint
from stats import Stats


class Item:

    def __init__(self, color: str, name: str, points: int, price: Union[int, str],
                 desc: str = '', perms: Optional[Permissions] = None):
        self.color = color
        self.desc = desc
        self.name = name
        self.points = points
        self.price = price
        self.perms = perms


class Game:

    def __init__(self, guild: Guild):
        self.paint = Paint()
        self.guild = guild
        self.admin = {'🐈': Item('#FFFF00', 'neko', 9999, '♾️',
            '🌟 Imbues owner with God-like prowess 🦄🌈✨', Permissions(administrator=True))}
        self.coins = {'🪙🪙🪙🪙🪙': 'coin5', '🪙🪙🪙🪙': 'coin4', '🪙🪙🪙': 'coin3', '🪙🪙': 'coin2', '🪙': 'coin1'}
        self.lives = {'❤️': 'heart1', '❤️❤️': 'heart2', '❤️❤️❤️': 'heart3', '❤️❤️❤️❤️': 'heart4',
            '❤️❤️❤️❤️❤️': 'heart5', '❤️❤️❤️❤️❤️❤️': 'heart6', '❤️❤️❤️❤️❤️❤️❤️': 'heart7',
            '❤️❤️❤️❤️❤️❤️❤️❤️': 'heart8', '❤️❤️❤️❤️❤️❤️❤️❤️❤️': 'heart9',
            '❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️': 'heart10', '💀': 'skull', '👻': 'ghost1',
            '👻👻': 'ghost2', '👻👻👻': 'ghost3'}
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
        self.perm_single_items = {
            '📜': Item('#FFFFC5', 'scroll', 100, 4, '⭐ Enables reader to change their name',
                self._mog),
            '🔮': Item('#D580FF', 'wand', 50, 2,
                ('⭐ Enables caster to attach files, connect to voice channels, embed links '
                 'and use external emojis and stickers'), self._share),
            '💎': Item('#809CA7', 'charm', 75, 3, '⭐ Enables wearer to react', self._react),
            '🪨': Item('#7DA27E', 'rune', 25, 1, '⭐ Enables holder to post', self._post),
            '🕹️': Item('#4169E1', 'remote', 25, 1,
                f'⭐ Enables user to control {self.guild.me.mention} with /', self._app)}
        self.perm_items = {
            '📜🔮💎🪨🕹️': Item('#DFFF00', 'scrollwandcharmruneremote', 0, 0, '', self._base),
            '🔮💎🪨🕹️': Item('#7A1F3D', 'wandcharmruneremote', 0, 0, '',
                Permissions(self._base.value & ~self._mog.value)),
            '📜🔮🪨🕹️': Item('#FFE135', 'scrollwandruneremote', 0, 0, '',
                Permissions(self._base.value & ~self._react.value)),
            '📜💎🪨🕹️': Item('#40E0D0', 'scrollcharmruneremote', 0, 0, '',
                Permissions(self._base.value & ~self._share.value)),
            '📜🔮💎🕹️': Item('#FA8072', 'scrollwandcharmremote', 0, 0, '',
                Permissions(self._base.value & ~self._post.value)),
            '📜🔮💎🪨': Item('#737C3E', 'scrollwandcharmrune', 0, 0, '',
                Permissions(self._base.value & ~self._app.value)),
            '🔮💎🕹️': Item('#065535', 'wandcharmremote', 0, 0, '',
                Permissions(self._app.value | self._react.value | self._share.value)),
            '🔮🪨🕹️': Item('#00FFFF', 'wandruneremote', 0, 0, '',
                Permissions(self._app.value | self._post.value | self._share.value)),
            '📜💎🕹️': Item('#CCCCFF', 'scrollcharmremote', 0, 0, '',
                Permissions(self._app.value | self._mog.value | self._react.value)),
            '📜🔮🕹️': Item('#CD7F32', 'scrollwandremote', 0, 0, '',
                Permissions(self._app.value | self._mog.value | self._share.value)),
            '📜🪨🕹️': Item('#E97451', 'scrollruneremote', 0, 0, '',
                Permissions(self._app.value | self._mog.value | self._post.value)),
            '💎🪨🕹️': Item('#954535', 'charmruneremote', 0, 0, '',
                Permissions(self._app.value | self._post.value | self._react.value)),
            '📜💎🪨': Item('#9A2A2A', 'scrollcharmrune', 0, 0, '',
                Permissions(self._mog.value | self._post.value | self._react.value)),
            '📜🔮🪨': Item('#CC7722', 'scrollwandrune', 0, 0, '',
                Permissions(self._mog.value | self._post.value | self._share.value)),
            '🔮💎🪨': Item('#A0522D', 'wandcharmrune', 0, 0, '',
                Permissions(self._post.value | self._react.value | self._share.value)),
            '📜🔮💎': Item('#8A9A5B', 'scrollwandcharm', 0, 0, '',
                Permissions(self._mog.value | self._react.value | self._share.value)),
            '📜💎': Item('#7FFFD4', 'scrollcharm', 0, 0, '',
                Permissions(self._mog.value | self._react.value)),
            '🔮💎': Item('#008080', 'wandcharm', 0, 0, '',
                Permissions(self._react.value | self._share.value)),
            '📜🔮': Item('#FBCEB1', 'scrollwand', 0, 0, '',
                Permissions(self._mog.value | self._share.value)),
            '🪨🕹️': Item('#DA70D6', 'runeremote', 0, 0, '',
                Permissions(self._app.value | self._post.value)),
            '💎🪨': Item('#AA98A9', 'charmrune', 0, 0, '',
                Permissions(self._react.value | self._post.value)),
            '🔮🪨': Item('#FFBF00', 'wandrune', 0, 0, '',
                Permissions(self._post.value | self._share.value)),
            '📜🪨': Item('#FDDA0D', 'scrollrune', 0, 0, '',
                Permissions(self._mog.value | self._post.value)),
            '💎🕹️': Item('#B4C424', 'charmremote', 0, 0, '',
                Permissions(self._app.value | self._react.value)),
            '🔮🕹️': Item('#FCF55F', 'wandremote', 0, 0, '',
                Permissions(self._app.value | self._share.value)),
            '📜🕹️': Item('#EDEADE', 'scrollremote', 0, 0, '',
                Permissions(self._app.value | self._mog.value))
        }
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
        self._app = Permissions(use_application_commands=True)
        self._base = Permissions(add_reactions=True, attach_files=True, change_nickname=True,
            connect=True, create_polls=True, create_public_threads=True, embed_links=True,
            send_messages=True, send_messages_in_threads=True, use_application_commands=True,
            use_external_emojis=True, use_external_stickers=True)
        self._mog = Permissions(change_nickname=True)
        self._post = Permissions(create_polls=True, create_public_threads=True,
            send_messages=True, send_messages_in_threads=True)
        self._post_and_view = PermissionOverwrite(view_channel=True, send_messages=True,
            add_reactions=True, create_polls=True, create_public_threads=True)
        self._react = Permissions(add_reactions=True)
        self._share = Permissions(attach_files=True, connect=True, embed_links=True,
            use_external_emojis=True, use_external_stickers=True)
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
        await self.create_inventory()
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
        for i in range(1, 100):
            await self.create_role(str(i), f"#{Color.random().value:06X}", alias='Level')
        for name, item in self.admin.items():
            await self.create_role(name, item.color, hoist=True, perms=item.perms)
        for name in self.lives:
            await self.create_role(name, '#BE1931')
        for name in self.coins:
            await self.create_role(name, '#D4AF37')
        for name, item in self.items.items():
            # Allows stacking 3 of the same item.
            for i in range(1, 4):
                await self.create_role(name * i, item.color)
        for name, item in self.perm_items.items():
            await self.create_role(name, item.color, perms=item.perms)
        for name, item in self.perm_single_items.items():
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
        for name, item in self.admin.items():
            await self.send_img(self.roles[name], channel, item.name,
                f"{item.desc}\n🅿️ **Points**: {item.points}\n🪙 **Coins**: {item.price}",
                f"God-like Neko {name}")
        for name, item in self.items.items():
            await self.send_img(self.roles[name], channel, f"{item.name}1",
                f"{item.desc}\n🅿️ **Points**: {item.points}\n🪙 **Coins**: {item.price}",
                f"{item.name.title()} {name}")
        for name, item in self.perm_single_items.items():
            await self.send_img(self.roles[name], channel, item.name,
                f"{item.desc}\n🅿️ **Points**: {item.points}\n🪙 **Coins**: {item.price}",
                f"{item.name.title()} {name}")
        return None

    async def create_color(self, context: Context, name: str, hex_code) -> str:
        role = await self.create_role(name, hex_code, ref_role=self.guild.me.top_role)
        self.paint.update(role.id, hex_code)
        await self.send_img(role, context.channel, hex_code.lstrip('#').upper(),
            f"**Created**: {role.mention}", '')
        return '**New Color Created!**'

    async def create_heart(self, member: Member) -> None:
        for role in member.roles:
            if role.name.startswith('💀'):
                new_role = self.roles['❤️']
                image = 'heart'
                title = 'Animation'
                notes = f"{member.mention} just animated!\n**Vigor**: {new_role.mention}"
                break
            elif role.name.startswith('❤️'):
                count = role.name.count('❤️')
                if count == 10:
                    return None
                new_role = self.roles['❤️' * (count + 1)]
                image = 'heart'
                if (count + 1) == 10:
                    title = 'Achieved Maximum Potency'
                    notes = f"{member.mention} achieved maximum potency!\n**Vigor**: {new_role.mention}"
                else:
                    title = 'Got a Heart!'
                    notes = f"{member.mention} got +1 ❤️!\n**Vigor**: {new_role.mention}"
                break
            elif role.name.startswith('👻'):
                count = role.name.count('👻')
                if count > 1:
                    new_role = self.roles['👻' * (count - 1)]
                    image = 'ghost'
                    title = 'Rematerialization'
                    notes = f"{member.mention} is rematerializing!\n**Vigor**: {'👻' * (count - 1)}"
                else:
                    new_role = self.roles['💀']
                    image = 'meilanliu'
                    title = 'Transmutation'
                    notes = f"{member.mention} is liminal.\n**Vigor**: 💀"
                    await member.remove_roles(*[role for role in member.roles if role.name in self.prime])
                    await member.add_roles(self.roles['Hospitalized'])
                break
        await member.remove_roles(role)
        await member.add_roles(new_role)
        await self.send_img(
            new_role, member.guild.system_channel, image, notes, title, member)
        return None

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
                self.roles['Scientist']: self._post_and_view,
                self.roles['Psychotic']: self._post_limited})
        await category.create_text_channel(
            name='🔒doctors-office💉',
            overwrites=self._view_only | hospital_perms | {
                self.roles['Scientist']: self._post_and_view, self.roles['Nurse']: self._post_and_view})
        await category.create_voice_channel(
            name='🛋️visitation💔🌡️💀', overwrites=hospital_perms | self._main_perms())
        return None

    async def create_inventory(self) -> None:
        category = await self.guild.create_category('🎒👛Designer Bag💼💄👝🍬')
        for name, filename in self.lives.items():
            channel = await category.create_text_channel(name=name, overwrites=self._view_only | {
                self.roles[name]: self._view})
            await self.send_img(self.roles[name], channel, filename, self.roles[name].mention, '')
        for name, filename in self.coins.items():
            channel = await category.create_text_channel(name=name, overwrites=self._view_only | {
                self.roles[name]: self._view})
            await self.send_img(self.roles[name], channel, filename, self.roles[name].mention, '')
        for name, item in self.perm_single_items.items():
            channel = await category.create_text_channel(name=name, overwrites=self._view_only | {
                self.roles[name]: self._view})
            await self.send_img(self.roles[name], channel, item.name, self.roles[name].mention, '')
        for name, item in self.perm_items.items():
            channel = await category.create_text_channel(name=name, overwrites=self._view_only | {
                self.roles[name]: self._view})
            await self.send_img(self.roles[name], channel, item.name, self.roles[name].mention, '')
        category = await self.guild.create_category('🧰⚙️Paraphernalia📕🛠️🚧💥')
        for name, item in self.items.items():
            for i in range(1, 4):
                role_name = name * i
                channel = await category.create_text_channel(name=role_name, overwrites=self._view_only | {
                    self.roles[role_name]: self._view})
                await self.send_img(
                    self.roles[role_name], channel, f"{item.name}{i}", self.roles[role_name].mention, '')
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
                self.roles['Solitary']: self._post_limited, self.roles['Guard']: self._post_and_view,
                self.roles['Priest']: self._post_and_view})
        await category.create_text_channel(
            name='🔒wardens-office🗝️', overwrites=self._view_only | prison_perms | {
                self.roles['Guard']: self._post_and_view})
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
        await sleep(5)
        return new_role

    async def create_rules(self) -> None:
        rules_perms = self._view_only | self._main_perms() | {self.roles['Guard']: self._post}
        category = await self.guild.create_category(
            '🛡️⚔️COMMANDMENTS⚔️🛡️', overwrites=rules_perms)
        for rule in ['no-anime', 'no-bullying', 'no-gore', 'no-nudes']:
            await category.create_text_channel(name=f"⛔{rule}🗃️")
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
        curr_lvl = int(old_role.name)
        next_lvl = self.stats.level_up(member.id)
        if next_lvl != curr_lvl:
            if next_lvl > curr_lvl:
                title = 'New Level Unlocked'
                prefix = 'Up'
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
            for _ in range(self.stats.level_hearts(member.id)):
                await self.create_heart(member)
        return None

    async def remove_heart(self, member: Member) -> None:
        for role in member.roles:
            if role.name.startswith('💀'):
                new_role = self.roles['👻']
                image = 'ghost'
                title = 'Dead'
                notes = f"{member.mention} just died!\n**Vigor**: {new_role.mention}"
                await member.remove_roles(*[role for role in member.roles if role.name in self.prime])
                await member.add_roles(self.roles['Ghost'])
                break
            elif role.name.startswith('❤️'):
                image = 'heart'
                count = role.name.count('❤️')
                if count > 1:
                    new_role = self.roles['❤️' * (count - 1)]
                    title = 'Ouch'
                    notes = f"{member.mention} lost a heart!\n**Vigor**: {new_role.mention}"
                else:
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
                image = 'ghost'
                title = 'Transmogrification'
                notes = f"{member.mention} is transmogrifying!\n**Vigor**: {new_role.mention}"
                break
        await member.remove_roles(role)
        await member.add_roles(new_role)
        await self.send_img(
            new_role, member.guild.system_channel, image, notes, title, member)

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
        for role in self.guild.roles:
            if not self.paint.id_exists(role.id):
                if role.name.isdigit():
                    self.roles['Level'].add(role)
                else:
                    self.roles[role.name] = role
        self.roles['Level'] = sorted(self.roles['Level'],key=lambda r: int(r.name))
        return None

    def _main_perms(self) -> Dict:
        return {self.roles['Priest']: self._view, self.roles['Scientist']: self._view,
            self.roles['Guard']: self._view, self.roles['Nurse']: self._view,
            self.roles['TOWG']: self._view}
