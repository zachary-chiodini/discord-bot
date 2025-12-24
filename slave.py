from asyncio import TimeoutError
from collections import OrderedDict
from math import sqrt
from os import path
from random import randint
from re import fullmatch
from time import perf_counter

from discord import Color, Embed, File, Intents, Member, Message, PermissionOverwrite, Role, TextChannel
from discord.ext import commands
from discord.ext.commands import Context
from PIL import Image

from converter import Mention, MemberOrStr, RoleOrStr, Text


ADMIN_USER_ID = 1380323054479085648
ADMIN_ROLE_ID = 1440115659387310201

FILE_COLOR = 'database/text_file/color.txt'
FILE_ITEMS = 'database/text_file/items.txt'
FILE_LEVEL = 'database/text_file/level.txt'
FILE_SCORE = 'database/text_file/score.txt'

MAIN_ROLE_ID = 1430634515193139220
OUTSIDER_ROLE_ID = 1435574700863393825
PRISONER_ROLE_ID = 1430999416180965418

GOLD_COIN_ROLE_ID = 1448979150948794378
SEPARATOR_ROLE_ID = 1448156888066949277

PERM_EMBED_ROLE_ID = 1449342831629172826
PERM_MOG_ROLE_ID = 1439713022489923730
PERM_POST_ROLE_ID = 1437459436829409440
PERM_REACT_ROLE_ID = 1436878137647562754
PERM_ITEMS = [PERM_EMBED_ROLE_ID, PERM_MOG_ROLE_ID, PERM_POST_ROLE_ID, PERM_REACT_ROLE_ID]

PRISON_VISITATION_ID = 1397259367224442962
PURSE_CHANNEL_ID = 1449214693091840131

CRIME_MAP = {1396611518153625703: 'SEX OFFENDER', 1396672806867046461: 'MURDERER', 1396672632539189339: 'PROSTITUTE',
    1396672163196698674: 'STRAIGHT', 1396673043903938711: 'BULLY'}


class Slave(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._colors = {}
        # Load colors database
        with open(FILE_COLOR) as f:
            for line in f.readlines():
                role_id, hex_code = line.split(',')
                self._colors[int(role_id)] = hex_code.strip()
        self._score = {}
        # Load score database
        with open(FILE_SCORE) as f:
            for i, line in enumerate(f.readlines()):
                user_id, level_role_id, posts, score = line.split(',')
                self._score[int(user_id)] = [i, int(level_role_id), int(posts), int(score)]
        # Load level role database
        self._level = []
        with open(FILE_LEVEL) as f:
            for role_id in f.readlines():
                self._level.append(int(role_id))
        # Load item database
        self._items = {}
        with open(FILE_ITEMS) as f:
            for line in f.readlines():
                role_id, points = line.split(',')
                self._items[int(role_id)] = int(points)

    @commands.Cog.listener()
    async def on_member_join(self, member: Member) -> None:
        # Assign new member roles
        for role_id in [OUTSIDER_ROLE_ID, self._level[0], PERM_POST_ROLE_ID, PERM_REACT_ROLE_ID]:
            await member.add_roles(member.guild.get_role(role_id))
        # Update score
        self._score[member.id] = [len(self._score), self._level[0], 0, 0]
        # Update database
        with open(FILE_SCORE, 'a') as f:
            f.write(f"{member.id:<20},{self._level[0]:<20},0000000000000,0000000000000\n")
        # Welcome new member
        embed = Embed(title=f"Outsider Identified",
            description=f"{member.mention}\nName: {member.name}\nAlias: {member.display_name}",
            color=member.guild.get_role(self._level[0]).color)
        embed.set_image(url=member.display_avatar.url)
        await member.guild.system_channel.send(embed=embed)
        return None

    @commands.Cog.listener()
    async def on_member_remove(self, member: Member) -> None:
        items_removed = set()
        for role in member.roles:
            if role.id in self._items:
                items_removed.add(role)
        if items_removed:
            admin = member.guild.get_member(ADMIN_USER_ID)
            for item in items_removed:
                await admin.add_roles(item)
                self._score[admin.id][3] += self._items[item.id]
            await self._level_up(admin, member.guild.system_channel)
        # Delete member from database
        del self._score[member.id]
        with open(FILE_SCORE, 'w') as f:
            for i, member_id, member_ref in enumerate(self._score.items()):
                self._score[member_id][0] = i
                f.write(f"{member_id:<20},{member_ref[1]:<20},{member_ref[2]:0>13},{member_ref[3]:0>13}\n")
        # Notify guild
        embed = Embed(title=f"Someone Left",
            description=f"{member.mention}\nName: {member.name}\nAlias: {member.display_name}",
            color=Color.red())
        embed.set_image(url=member.display_avatar.url)
        await member.guild.system_channel.send(embed=embed)
        return None


    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.author.bot:
            return None
        if message.content.startswith('!slave'):
            return None
        # Update post count
        self._score[message.author.id][2] += 1
        # Update score
        self._score[message.author.id][3] += 1
        await self._level_up(message.author, message.channel)
        return None

    @commands.group(invoke_without_command=True)
    async def slave(self, context: Context) -> None:
        if self._is_master_user(context):
            await context.send(f"You're amazing, {context.author.display_name}.")
        else:
            await context.send(f"Hi, {context.author.display_name}.")
        return None

    @slave.command()
    async def exile(self, context: Context, member: MemberOrStr = '', crime: Text = '', text: str = '') -> None:
        def yes_from_respondent(context: Context, message: Message) -> bool:
            if ((message.author.id not in vote) and (message.channel == context.channel) 
                    and (message.content.lower().strip() == 'yes')):
                vote.add(message.author.id)
                return True
            return False
        if isinstance(member, Member):
            if not member.get_role(MAIN_ROLE_ID):
                await context.send(f"{member.mention} must be a member of {context.guild.get_role(MAIN_ROLE_ID).mention}.")
                return None
            vote = {context.author.id}
            await context.send(f"Two additional members must respond with 'yes' to exile {member.mention}")
            try:
                await bot.wait_for('message', timeout=10, check=lambda m: yes_from_respondent(context, m))
                await context.send(f"One additional member must respond with 'yes' to exile {member.mention}")
                await bot.wait_for('message', timeout=10, check=lambda m: yes_from_respondent(context, m))
            except TimeoutError:
                await context.send('Timeout: Aborted.')
                return None
            await member.remove_roles(context.guild.get_role(MAIN_ROLE_ID))
            await member.add_roles(context.guild.get_role(OUTSIDER_ROLE_ID))
            await self._send_report(
                context.guild.get_role(OUTSIDER_ROLE_ID).color, context, False, crime, member,
                f"Citizen {member.display_name} Exhiled", text)
            return None
        await context.send(
            f"Exile {context.guild.get_role(MAIN_ROLE_ID).mention} member:\n{self._color_code_message('slave', 'exile', '@Member', '')}\n"
            f"Attach the Commandment Channel:\n{self._color_code_message('slave', 'exile', '@Member ', '#Channel', '')}\n"
            f"Attach an optional message:\n{self._color_code_message('slave', 'exile', '@Member ', '<message-id>')}\n"
            f"""Include an optional message:\n{self._color_code_message('slave', 'exile', '@Member ', '"Offensive speech!"')}\n"""
            f"Combinations:\n{self._color_code_message('slave', 'exile', '@Member ', '#Channel ', '<message-id>')}\n"
            f"""{self._color_code_message('slave', 'exile', '@Member ', '#Channel ', '"Offensive speech!"')}\n"""
            f"""{self._color_code_message('slave', 'exile', '@Member ', '<message-id> ', '"Offensive speech!"')}""")
        return None

    @slave.command()
    async def gift(self, context: Context, member: MemberOrStr, item: RoleOrStr) -> None:
        if isinstance(member, Member) and isinstance(item, Role):
            if item.id in self._items:
                container = self._items
                points = self._items[item.id]
            elif item.id in PERM_ITEMS:
                if member.get_role(item.id):
                    await context.send(f"{member.mention} already has a {item.mention}.")
                    return None
                container = [item.id]
                points = 0
            else:
                await context.send(f"{item.mention} is not a giftable item.")
                return None
            author_items = set()
            for role in context.author.roles:
                if role.id in container:
                    author_items.add(role)
            if not author_items:
                await context.send(f"{context.author.mention} does not have a {item.mention} to gift.")
            elif context.author.id == member.id:
                await context.send(f"You cannot gift yourself a {item.mention}.")
            else:   
                gift = author_items.pop()
                await context.author.remove_roles(gift)
                await member.add_roles(gift)
                await context.send(f"{member.mention} recieved {gift.mention} from {context.author.mention}.")
                if points:
                    self._score[context.author.id][3] -= points
                    await self._level_up(context.author, context.channel)
                    self._score[member.id][3] += points
                    await self._level_up(member, context.channel)
                return None
        else:
            await context.send(
                f"Gift an item to another member:\n"
                f"{self._color_code_message('slave', 'gift', '@Member', '@Item')}")
        return None

    @slave.command()
    async def paint(self, context: Context, member: Mention = '', role: RoleOrStr = '', *args: Role) -> None:
        async def create_new_color(name: str, hexcode: str) -> None:
            # Create new color role
            color = Color.from_str(hexcode)
            new_color = await self._create_role(context.channel, name.title(), context.guild.me.top_role.position, color)
            # Update database
            self._colors[new_color.id] = hexcode
            with open(FILE_COLOR, 'a') as f:
                f.write(f"{new_color.id},{hexcode}\n")
            # Make colored square image
            img = Image.new("RGB", (256, 256), ((color.value >> 16) & 0xFF, (color.value >> 8) & 0xFF, color.value & 0xFF))
            img.save(f"database/colors/{hexcode[1:].lower()}.png", format='PNG')
            await show_color(new_color, 'New Color Created')
            return None

        def mix_colors(*hexes: int) -> int:
            r, g, b = 0, 0, 0
            # Extract red, green and blue channels
            for hex_ in hexes:     
                r += (hex_ >> 16) & 0xFF
                g += (hex_ >> 8) & 0xFF
                b += hex_ & 0xFF
            # Mix (average) each channel
            r, g, b = r // len(hexes), g // len(hexes), b // len(hexes)
            # Recombine 0xRRGGBB integer
            return (r << 16) + (g << 8) + b

        async def show_color(color: Role, text: str) -> None:
            filename = f"{color.color.value:06x}.png".lower()
            embed = Embed(title=text, description=color.mention, color=color.color)
            file = File(f"database/colors/{filename}", filename=filename)
            embed.set_image(url=f"attachment://{filename}")
            embed.set_author(name=context.author.display_name, icon_url=context.author.display_avatar.url)
            await context.send(embed=embed, file=file)
            return None

        if (member == 'show'):
            # Search for color role in database
            offender = role
            if isinstance(role, Role):
                offender = role.mention
                if role.id in self._colors:
                    await show_color(role, 'Showing Color')
                    return None
            elif fullmatch(r'#([0-9a-fA-F]{6})', role):
                for role_id, hex_code in self._colors.items():
                    if role.lower() == hex_code.lower():
                        await show_color(context.guild.get_role(role_id), 'Color Found')
                        return None
            await context.send(f"Color {offender} not found.")
        elif isinstance(member, Member):
            # Paint member a color role
            offender = role
            if isinstance(role, Role):
                offender = role.mention
                if role.id in self._colors:
                    await member.remove_roles(*[role for role in member.roles if role.id in self._colors])
                    await member.add_roles(role)
                    return None
            else:
                await context.send(f"Make {offender} a @Color role to paint {member.mention}.")
        elif isinstance(member, Role):
            offender = member.mention
            if member.id in self._colors:
                offender = role
                if isinstance(role, Role):
                    # Mix color roles
                    mixed_color_map = OrderedDict([(member.name, member.color.value)])
                    for color_role in [role] + [arg for arg in args]:
                        offender = color_role.mention
                        if color_role.id in self._colors:
                            mixed_color_map[color_role.name] = color_role.color.value
                        else:
                            break
                    else:
                        mixed_color_int = mix_colors(*mixed_color_map.values())
                        mixed_color_hex = f"#{mixed_color_int:06X}"
                        mixed_color_name = ' '.join(mixed_color_map)
                        for role_id, color_hex in self._colors.items():
                            color_role = context.guild.get_role(role_id)
                            if (mixed_color_hex.lower() == color_hex.lower()) or (color_role.name == mixed_color_name):
                                await show_color(color_role, 'Mixed Color Found')
                                return None
                        await create_new_color(mixed_color_name, mixed_color_hex)
                        return None
                else:
                    # Paint author color role
                    await context.author.remove_roles(*[role for role in context.author.roles if role.id in self._colors])
                    await context.author.add_roles(member)
                    return None
            await context.send(f"Interpreted input {offender} as a @color role.\nColor not found.")
        elif isinstance(member, str) and role and isinstance(role, str):
            # Create a new color role
            if fullmatch(r'#([0-9a-fA-F]{6})', role):
                for role_id, color_hex in self._colors.items():
                    color_role = context.guild.get_role(role_id)
                    if (color_role.name == member.title()) or (role.lower() == color_hex.lower()):
                        await show_color(color_role, 'Color already exists.')
                        return None
                await create_new_color(member.title(), role)
            else:
                await context.send(f"Color code {role} is invalid. Use format #RRGGBB.")
        else:
            await context.send(
                f"Paint yourself a Color:\n{self._color_code_message('slave', 'paint', '', '@Color')}\n"
                f"Paint a Member a Color:\n{self._color_code_message('slave', 'paint', '@Member ', '@Color')}\n"
                f"Look up a Color:\n{self._color_code_message('slave', 'paint show', '', '#RRGGBB')}\n"
                f"{self._color_code_message('slave', 'paint show', '', '@Color')}\n"
                f"Mix Colors:\n{self._color_code_message('slave', 'paint', '@Color ', '@Color ', '...')}\n"
                f"""Create a new Color:\n{self._color_code_message('slave', 'paint', '"Color Name" ', '#RRGGBB')}\n""")
        return None

    @slave.group(invoke_without_command=True)
    async def master(self, context: Context) -> None:
        await self._is_master(context)
        return None

    @master.command()
    async def create(self, context: Context, member: Member, item: Role) -> None:
        await self._is_master(context)
        if item.id in self._items:
            # Mint new item
            copy_item = await self._create_role(context.channel, item.name, item.position, item.color)
            # Update database
            self._items[copy_item.id] = self._items[item.id]
            with open(FILE_ITEMS, 'a') as f:
                f.write(f"\n{copy_item.id:<20},{self._items[copy_item.id]:0>13}")
            # Give to member
            await member.add_roles(copy_item)
            await context.send(f"{member.mention} recieved {copy_item.mention}")
            # Update score  
            self._score[member.id][3] += self._items[copy_item.id]
            # Create item channel under purse channel
            channel = context.guild.get_channel(PURSE_CHANNEL_ID)
            permissions = PermissionOverwrite(view_channel=True, send_messages=False, create_public_threads=False, create_polls=False)
            new_channel = await context.guild.create_text_channel(
                name='🪙gold-coin', category=channel.category, overwrites={copy_item: permissions}, position=channel.position + 1)
            await new_channel.send(content=f"{copy_item.mention}\n⭐ Worth 250 Points", file=File('database/items/coin.png'))
            # Send item creation message
            embed = Embed(title='New Item Created', description=f"{copy_item.mention}\n⭐ Worth 250 Points", color=copy_item.color)
            file = File('database/items/coin.png', filename='coin.png')
            embed.set_image(url=f"attachment://coin.png")
            embed.set_author(name=context.author.display_name, icon_url=context.author.display_avatar.url)
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(name='', value=f"{member.mention} was gifted a {copy_item.mention}")
            await context.guild.system_channel.send(embed=embed, file=file)
            # Update level
            await self._level_up(member, context.channel)
        else:
            await context.send(f"{item.mention} is not a mintable item.")
        return None

    @master.command()
    async def delete(self, context: Context, entity: str, color_role: Role) -> None:
        await self._is_master(context)
        if entity == 'color':
            if color_role.id in self._colors:
                await color_role.delete()
                # Update database (rewrite)
                del self._colors[color_role.id]
                with open(FILE_COLOR, 'w') as f:
                    for role_id, color_hex in self._colors.items():
                        f.write(f"{role_id},{color_hex}\n")
        return None

    @master.command()
    async def erase(self, context: Context, target_id: MemberOrStr = '') -> None:
        def yes_from_master(context: Context, message: Message) -> bool:
            return self._is_master_user(context) and (message.channel == context.channel) and (message.content.lower().strip() == 'yes')

        await self._is_master(context)
        if target_id:
            if isinstance(target_id, Member):
                target_id = target_id.id

            elif target_id.isdigit():
                target_id = int(target_id)

            if isinstance(target_id, int):
                async for target_message in context.channel.history(limit=None, oldest_first=False):
                    if target_message.author.id == target_id:
                        targets = [target_message.author.name, target_message.author.display_name, str(target_id)]
                        embed = Embed(title=f"Target Acquired {target_id}:",
                            description=f"Name: {target_message.author.name}\nNickname: {target_message.author.display_name}",
                            color=Color.red())
                        embed.set_image(url=target_message.author.display_avatar.url)
                        await context.send(embed=embed)
                        break
                else:
                    await context.send(f"Target ID {target_id} not found.")
                    return None

                await context.send(f"Are you sure you want to erase {target_message.author.name}? "
                    'This will delete all messages sent by and that referenced this user.')
            else:
                targets = [target_id]
                await context.send(f"Are you sure you want to erase all messages containing '{target_id}' in {context.channel.name}?")
        else:
            targets = ['']
            await context.send(f"Are you sure you want to erase all messages in {context.channel.name}?")

        try:
            await bot.wait_for('message', timeout=10, check=lambda m: yes_from_master(context, m))
        except TimeoutError:
            await context.send('Timeout: Aborted.')
            return None

        await context.send(f"Erasing them ...")
        init_time = perf_counter()
        messages_deleted, total_messages = 0, 0
        async for message in context.channel.history(limit=None, oldest_first=False):
            total_messages += 1
            if ((message.author.id == target_id)
                    or any(e.lower() in message.content.casefold() for e in targets)
                    or any(embed.title and ((str(target_id).lower() in embed.title.casefold()) or (str(target_id).lower() in embed.description.casefold())) for embed in message.embeds)):
                try:
                    await message.delete()
                    messages_deleted += 1
                except Exception as e:
                    await context.send(e)
                    break

        tot_secs = int(perf_counter() - init_time)
        h, m, s = tot_secs // 3600, (tot_secs % 3600) // 60, int(tot_secs % 60)
        embed = Embed(title=f"Target Summary {target_id}:",
            description=f"Erased: {messages_deleted}\nParsed: {total_messages}\nChannel: {context.channel}\nTime: {h:02}:{m:02}:{s:02}",
            color=Color.red())
        await context.send(embed=embed)
        return None

    @master.command()
    async def imprison(self, context: Context, member: MemberOrStr = '', crime: Text = '', text: str = '') -> None:
        await self._is_master(context)
        if isinstance(member, Member):
            # Collect valuable items from member
            items = set()
            points = 0
            for role in member.roles:
                if role.id in self._items:
                    await member.remove_roles(role)
                    items.add(role)
                    points += self._items[role.id]
            if items:
                # Update author score
                await context.author.add_roles(*items)
                self._score[context.author.id][3] += points
                await self._level_up(context.author, context.channel)
            # Clear member score
            member_ref = self._score[member.id]
            self._score[member.id] = [member_ref[0], member_ref[1], 0, 0]
            await self._level_up(member, context.channel)
            # Strip and change member roles
            await member.remove_roles(*[role for role in member.roles if role != member.guild.default_role])
            level_role = await context.guild.get_role(self._level[0])
            await member.add_roles([PRISONER_ROLE_ID, PERM_POST_ROLE_ID, level_role])
            await self._send_report(
                context.guild.get_role(PRISONER_ROLE_ID).color, context, True, crime, member,
                f"Criminal {member.id} Identified", text)
            return None
        await context.send(
            f"Imprison a member:\n{self._color_code_message('slave', 'master imprison', '@Member', '')}\n"
            f"Attach the Commandment Channel:\n{self._color_code_message('slave', 'master imprison', '@Member ', '#Channel', '')}\n"
            f"Attach an optional message:\n{self._color_code_message('slave', 'master imprison', '@Member ', '<message-id>')}\n"
            f"""Include an optional message:\n{self._color_code_message('slave', 'master imprison', '@Member ', '"Offensive speech!"')}\n"""
            f"Combinations:\n{self._color_code_message('slave', 'master imprison', '@Member ', '#Channel ', '<message-id>')}\n"
            f"""{self._color_code_message('slave', 'master imprison', '@Member ', '#Channel ', '"Offensive speech!"')}\n"""
            f"""{self._color_code_message('slave', 'master imprison', '@Member ', '<message-id> ', '"Offensive speech!"')}""")
        return None

    @master.command()
    async def liberate(self, context: Context, member: MemberOrStr = str, text: str = '') -> None:
        await self._is_master(context)
        outsider = context.guild.get_role(OUTSIDER_ROLE_ID)
        prisoner = context.guild.get_role(PRISONER_ROLE_ID)
        if isinstance(member, Member):
            role = member.get_role(OUTSIDER_ROLE_ID)
            if not role:
                role = member.get_role(PRISON_VISITATION_ID)
                if not role:
                    await context.send(f"{member.mention} must be a {outsider.mention} or {prisoner.mention}.")
                    return None
            await self._send_report(
                context.guild.get_role(MAIN_ROLE_ID).color, context, False, text,
                f"{role.name.title()} Has Been Liberated", '')
            return None
        await context.send(
            f"Liberate an {outsider.mention} or a {prisoner.mention}:\n"
            F"{self._color_code_message('slave', 'master liberate', '@Member', '')}\n"
            f"Attach an optional message:\n{self._color_code_message('slave', 'master liberate', '@Member ', '<message-id>')}\n"
            f"""Include an optional message:\n{self._color_code_message('slave', 'master liberate', '@Member ', '"Confessed to their sin."')}""")
        return None

    @staticmethod
    def _color_code_message(red_text: str, white_text: str, blue_text: str = '', green_text: str = '', orange_text: str = '') -> str:
        red_text = f"\u001b[31m!{red_text}\u001b[0m"
        if blue_text:
            blue_text = f"\u001b[34m{blue_text}\u001b[0m"
        if green_text:
            green_text = f"\u001b[32m{green_text}\u001b[0m"
        if orange_text:
            orange_text = f"\u001b[33m{orange_text}\u001b[0m"
        return f"```ansi\n{red_text} {white_text} {blue_text}{green_text}{orange_text}\n```"

    async def _create_role(self, channel: TextChannel, name: str, position: int, color: Color) -> Role:
        if len(channel.guild.roles) == 250:
            # Delete random color role
            role_ids = list(self._colors.keys())
            random_role = channel.guild.get_role(role_ids[randint(0, len(role_ids) - 1)])
            await channel.send(f"Maximum roles encountered. Deleted role {random_role.mention}.")
            await random_role.delete()
            # Update database (rewrite)
            del self._colors[random_role.id]
            with open(FILE_COLOR, 'w') as f:
                for role_id, color_hex in self._colors.items():
                    f.write(f"{role_id},{color_hex}\n")
        new_role = await channel.guild.create_role(name=name, color=color)
        await channel.guild.edit_role_positions(positions={new_role: position})
        return new_role

    def _calc_level(self, member: Member) -> int:
        score = self._score[member.id][3]
        max_value = 10000.0
        A = 9910.10197
        a, b, c  = A / 9801, 0.89797, score - 1
        x = 1 + (sqrt(abs(b*b - 4*a*c)) - b) / (2*a)
        if x >= max_value:
            return 0
        return int(x)

    async def _is_master(self, context: Context) -> None:
        if self._is_master_user(context):
            return None
        await context.send(f"You are not my master: {context.author.display_name}.")
        raise commands.CheckFailure(f"User {context.author.display_name} is not master.")

    @staticmethod
    def _is_master_user(context: Context) -> bool:
        return (context.author.id == ADMIN_USER_ID) or any(role.id == ADMIN_ROLE_ID for role in context.author.roles)

    async def _send_report(self, color: Color, context: Context, convict: bool, crime: Text, member: Member, title: str, text: str) -> None:
        # Massage input
        msg_embed = []
        note = ''
        if convict:
            report_id = PRISON_VISITATION_ID
        else:
            report_id = context.guild.system_channel.id
        if isinstance(crime, TextChannel) and (crime.id in CRIME_MAP):
            report_id = crime.id
            note = f"\nOffense: {crime.mention}"
            if convict:
                note = f"{note}\nConvicted: {CRIME_MAP[report_id]}\nSentence: TBD"
            if text.isdigit():
                text = 'Attached'
                msg_embed = [await self._get_message_embed(context, int(text))]
            elif not text:
                text = 'Attached'
        elif isinstance(crime, int):
            msg_embed = [await self._get_message_embed(context, crime)]
            if not text:
                text = 'Attached'
        elif crime:
            text = crime
        else:
            text = 'Undefined'
        note = f"{note}\nMessage: {text}"
        # Main report sent to report channel
        embed = Embed(title=title, description=f"{member.mention}\nName: {member.name}\nNickname: {member.display_name}{note}", color=color)
        embed.set_image(url=member.display_avatar.url)
        sent_message = await member.guild.get_channel(report_id).send(embeds=[embed] + msg_embed)
        # Link to report sent to context channel
        embed = Embed(title=title, url=sent_message.jump_url, color=color)
        embed.set_thumbnail(url=member.display_avatar.url)
        await member.guild.get_channel(context.channel.id).send(embed=embed)
        return None

    async def _get_message_embed(self, context: Context, message_id: int) -> Embed:
        message = await context.channel.fetch_message(message_id)
        embed = Embed(description=message.content, timestamp=message.created_at)
        embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
        embed.add_field(name="Criminal Message", value=f"[{message.id}]({message.jump_url})", inline=False)
        if message.attachments:
            embed.set_image(url=message.attachments[0].url)
        embed.set_footer(text=f"Forwarded by {context.author.mention}", icon_url=context.author.display_avatar.url)
        return embed

    async def _level_up(self, member: Member, channel: TextChannel) -> None:
        level_role = member.get_role(self._score[member.id][1])
        curr_lvl_n = int(level_role.name.removeprefix('LVL '))
        next_lvl_n = self._calc_level(member)
        if next_lvl_n != curr_lvl_n:
            if next_lvl_n > curr_lvl_n:
                title = 'New Level Unlocked'
                prefix = 'up'
                # Create level roles if new level not found in level list.
                if (len(self._level) - 1) < next_lvl_n:
                    for i in range(next_lvl_n - curr_lvl_n):
                        level = curr_lvl_n + i + 1
                        index = member.guild.get_role(SEPARATOR_ROLE_ID).position
                        new_level_role = await self._create_role(channel, f"LVL {level}", index, Color.random())
                        self._level.append(new_level_role.id)
                        with open(FILE_LEVEL, 'a') as f:
                            f.write(f"\n{new_level_role.id}")
                else:
                    new_level_role = member.guild.get_role(self._level[next_lvl_n])
            else:
                title = 'Level Lost'
                prefix = 'down'
                new_level_role = member.guild.get_role(self._level[next_lvl_n])
            # Update level
            self._score[member.id][1] = new_level_role.id
            await member.remove_roles(level_role)
            await member.add_roles(new_level_role)
            if not member.get_role(PRISONER_ROLE_ID):
                # Level up message
                filename = f"{(next_lvl_n % 2) + 1}.png"
                embed = Embed(title=title,
                    description=f"{member.mention} {prefix}graded from {level_role.mention} to {new_level_role.mention}",
                    color=new_level_role.color)
                file = File(f"database/images/{filename}", filename=filename)
                embed.set_image(url=f"attachment://{filename}")
                embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
                await channel.guild.system_channel.send(embed=embed, file=file)
        # Update database
        member_ref = self._score[member.id]
        with open(FILE_SCORE, 'r+') as f:
            f.seek((member_ref[0] * 70))
            f.write(f"{member.id:<20},{member_ref[1]:<20},{member_ref[2]:0>13},{member_ref[3]:0>13}\n")
        return None


if __name__ == "__main__":
    bot = commands.Bot(command_prefix='!', intents=Intents.all())

    @bot.event
    async def on_ready():
        await bot.add_cog(Slave(bot))

    with open('database/text_file/token.txt') as token_file:
        token_raw = token_file.read()
    bot.run(token_raw)
