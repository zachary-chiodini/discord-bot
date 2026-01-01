from asyncio import sleep
from typing import Dict, Optional, Tuple, Union

from discord import (CategoryChannel, Color, Embed, File, Guild,
    Permissions, PermissionOverwrite, Role, TextChannel)


class Item:

    def __init__(self, color: str, description, filename: str, points: int, price: Union[int, str],
                 perms: Optional[Permissions] = None):
        self.color = color
        self.description = description
        self.filename = filename
        self.points = points
        self.price = price
        self.perms = perms


class Create:

    def __init__(self, guild: Guild):
        self.admin = ('🐈', Item('#FFFF00', 'neko', 99999,
            '❌ Not Purchasable', Permissions(administrator=True)))
        self.guild = guild
        self.main_channels = {
            '🏙️center👥⛲🦢🏞️',
            ''
        }
        self.rules = ['no-anime', 'no-bullying', 'no-gore', 'no-nudity']
        self.prime = {
            'Priest': '#67080B',
            'Scientist': '#DFFF00',
            'Guard': '#9EB37B',
            'Nurse':  '#FA82A2',
            'Lunch Lady': '#B666D2',
            'TOWG': '#4169E1',
            'Outsider': '#FF6600',
            'Hospitalized': '#00692B',
            'Psychotic': '#BF00FF',
            'Prisoner': '#964B00',
            'Solitary': '#000000',
            'Ghost': '#FFFFFF'
        }
        self.items = {
            '👨🏻‍🦯': Item('#000000',
                '⭐ Causes transitory intermittent blindness\n⭐ Removes: ❤️',
                'mask', 0, 4, Permissions(read_message_history=False, read_messages=False)),
            '❤️': Item('#BE1931', '⭐ Used to stay alive\n⭐ +1 ❤️ every 10 levels',
                'heart', 250, '❌ Not Purchasable'),
            '🪬': Item('#917EB3', '⭐ Enables one to enter the church',
                'idol', 1000, '❌ Not Purchasable'),
            '🛡️': Item('#006769',
                '⭐ Shields wearer from an attack\n⭐ Blocks: Imprisonment',
                'shield', 250, 4),
            '☣️': Item('#78443E',
                '⭐ Temporarily removes -1 points per second\n⭐ Removes: ❤️',
                'virus', -10, 4),
            '☢️': Item('#FAE500',
                '⭐ Temporarily removes -1 points per second\n⭐ Removes: ❤️',
                'waste', -10, 4),
            '🔫': Item('#808080', '⭐ Removes: ❤️❤️\n⭐ May Cause: Bleeding 🩸⏱️',
                'gun', 250, 4),
            '🔪': Item('#401B1B', '⭐ Removes: ❤️\n⭐ May Cause: Bleeding 🩸⏱️',
                'knife', 250, 2),
            '🪙': Item('#D4AF37', '⭐ Used to purchase items ☝🤓', 'coin', 250, 0),
            '📜': Item('#FFFFC5', '⭐ Enables reader to change their name', 'scroll', 100, 4,
                Permissions(change_nickname=True)),
            '💎': Item('#809CA7', '⭐ Enables holder to react', 'charm', 75, 3,
                Permissions(add_reactions=True)),
            '🔮': Item('#D580FF',
                '⭐ Enables caster to attach files, connect to voice channels, embed links and use external emojis and stickers',
                'wand', 50, 2, Permissions(attach_files=True, connect=True, embed_links=True,
                    use_external_emojis=True, use_external_stickers=True)),
            '🕹️': Item('#4169E1',
                f'⭐ Enables user to control {self.guild.me.mention} with !slave',
                'remote', 25, 1, Permissions(use_application_commands=True)),
            '🪨': Item('#7DA27E', '⭐ Enables holder to post', 'rune', 25, 1,
                Permissions(send_messages=True, send_messages_in_threads=True,
                    create_polls=True, create_public_threads=True))
        }
        self.roles = {}
        self._collect_roles()

    async def create_bulletin(self) -> None:
        view_only = {self.guild.default_role: PermissionOverwrite(
            send_messages=False, create_public_threads=False, create_polls=False)}
        bulletin = await self.guild.create_category('🧾📌BULLETIN BOARD🗺️🗡️⁉️', overwrites=view_only)
        await self.create_alert_channel(bulletin, self.roles['Outsider'], '🦧-outsider⚠️',
            f"🍂🐾 You're an {self.roles['Outsider'].mention} 🌿🦥",
            f"⭐ Speak to a {self.roles['Priest'].mention} ☝🤓")
        await self.create_alert_channel(bulletin, self.roles['🕹️'], '🕹️-commands',
            f"⭐ Use 🕹️ to control {self.guild.me.mention} with !slave or / ☝🤓")
        await self.create_alert_channel(bulletin, self.roles['Hospitalized'], '😵-hospital⚠️',
            f"🏢🚑 Your're {self.roles['Hospitalized'].mention} 👩🏻‍⚕️💉",
            f"⭐ Speak to a {self.roles['Nurse'].mention} ☝🤓")
        await self.create_alert_channel(bulletin, self.roles['Psychotic'], '🎭psychotic⚠️',
            f"💊🩻 Your're {self.roles['Psychotic'].mention} 📋👩🏻‍⚕️",
            f"⭐ Speak to a {self.roles['Scientist'].mention} ☝🤓")
        await self.create_alert_channel(bulletin, self.roles['Prisoner'], '🪳-prisoner⚠️',
            f"🏢🚓 Your're a {self.roles['Prisoner'].mention} 🐎💂🏼",
            f"⭐ Speak to a {self.roles['Guard'].mention} ☝🤓")
        await self.create_alert_channel(bulletin, self.roles['Solitary'], '💀-solitary⚠️',
            f"🗝️💂🏼 Your're in {self.roles['Solitary'].mention} 🔒⛓️",
            f"⭐ Speak to a {self.roles['Scientist'].mention} ☝🤓")
        await self.create_alert_channel(bulletin, self.roles['Ghost'], '👻-ghost-⚠️',
            f"🪦🚑 Your're a {self.roles['Ghost'].mention} 🕊️☠️",
            f"⭐ Speak to a {self.roles['Priest'].mention} ☝🤓")
        # Market Channel
        view = PermissionOverwrite(view_channel=True)
        perms = {self.roles['Priest']: view, self.roles['Scientist']: view,
            self.roles['Guard']: view, self.roles['Nurse']: view,
            self.roles['Lunch Lady']: view, self.roles['TOWG']: view,
            self.roles['Outsider']: view}
        channel = await bulletin.create_text_channel('🌳🏬market', overwrites=perms)
        name, item = self.admin[0], self.admin[0]
        await self.send_file_embed(channel, self.roles[name],
            '⭐ Imbues owner with God-like prowess 🦄🌈✨', f"database/items/{item.filename}.png",
            f"God-like Neko {name}", ('⭐ Points:', item.points), ('🪙 Coins:', '♾️'))
        for name, item in self.items.items():
            await self.send_file_embed(channel, self.roles[name], item.description,
                f"database/items/{item.filename}.png", f"{item.filename.title()} {name}",
                ('⭐ Points:', item.points), ('🪙 Coins:', item.price))
        return None

    async def create_all_channels(self) -> None:
        await self.create_bulletin()
        await self.create_rules()
        return None

    async def create_all_roles(self) -> None:
        base_perms = Permissions(create_instant_invite = True,
        mention_everyone = True, read_messages = True,
        read_message_history = True, send_voice_messages = True,
        speak = True, stream = True, use_voice_activation = True)
        await self.guild.default_role.edit(permissions=base_perms)
        await self.create_role('0', '#FF6600', alias='Level')
        name, item = self.admin[0], self.admin[1]
        await self.create_role(name, item.color, hoist=True, perms=item.perms)
        for name, item in self.items.items():
            await self.create_role(name, item.color, perms=item.perms)
        for name, hex_code in self.prime.items():
            await self.create_role(name, hex_code)
        await self.roles['Ghost'].edit(permissions=Permissions(view_channel=True))
        return None
 
    async def create_alert_channel(self, category: CategoryChannel,
            role: Role, title: str, *args: str) -> None:
        channel = await category.create_text_channel(name=title,
            overwrites={role: PermissionOverwrite(view_channel=True)})
        embed = Embed(title='', description='', color=role.color)
        for value in args:
            embed.add_field(name='', value=value, inline=False)
        await channel.send(embed=embed)
        return None

    async def create_role(self, name: str, hex_code: str,
            alias='', hoist=False, perms: Optional[Permissions] = None) -> Role:
        if len(self.guild.roles) == 250:
            try:
                color_role = self.guild.get_role(self.color.pop())
            except Exception as e:
                await self.guild.system_channel.send(f"ROLE LIMIT ENCOUNTERED\n{e}")
                return None
            await self.guild.system_channel.send(
                f"Maximum roles encountered. Deleted role {color_role.mention}.")
            await color_role.delete()
            await sleep(2)
        new_role = await self.guild.create_role(name=name, color=Color.from_str(hex_code))
        await sleep(2)
        await new_role.edit(hoist=hoist)
        if alias:
            name = alias
        if name in self.roles:
            if isinstance(self.roles[name], set):
                self.roles[name].add(new_role)
            else:
                self.roles[name] = {self.roles[name], new_role}
        else:
            self.roles[name] = new_role
        if perms:
            await new_role.edit(permissions=perms)
        return new_role

    async def create_rules(slef) -> None:
        pass

    async def initialize(self) -> None:
        await self.create_all_roles()
        await self.create_all_channels()
        return None

    async def send_file_embed(self, channel : TextChannel, color: Role,
            desc: str, filepath: str, title: str, *args: Tuple) -> None:
        filename = filepath.split('/')[-1]
        embed = Embed(title=title, description=desc, color=color.color)
        for name, value in args:
            embed.add_field(name=name, value=value)
        embed.set_image(url=f"attachment://{filename}")
        file = File(filepath, filename=filename)
        await channel.send(embed=embed, file=file)
        return None

    def _collect_roles(self) -> Dict:
        for role in self.guild.roles:
            if role.name.isdigit():
                name = 'Level'
            else:
                name = role.name
            if name in self.roles:
                self.roles[name].add(role)
            else:
                self.roles[name] = {role}
        return self.roles
