from asyncio import TimeoutError
from collections import OrderedDict
from math import sqrt
from os import path
from random import randint
from re import fullmatch
from time import perf_counter
from typing import Set, Tuple

from discord import (Color, Embed, File, Intents, Member, Message,
                     PermissionOverwrite, Role, TextChannel)
from discord.ext import commands
from discord.ext.commands import Context
from PIL import Image

from converter import Mention, MemberOrStr, RoleOrInt, RoleOrStr, Text


class Slave(commands.Cog):

    ADMIN_USER_ID = 1380323054479085648
    ADMIN_ROLE_ID = 1440115659387310201
    SERVER_ID = 1386754069640646787

    FILE_COLOR = 'database/text_file/color.txt'
    FILE_ITEMS = 'database/text_file/items.txt'
    FILE_LEVEL = 'database/text_file/level.txt'
    FILE_SCORE = 'database/text_file/score.txt'

    MAIN_ID = 1430634515193139220
    OUTSIDER_ID = 1435574700863393825
    PRISONER_ID = 1430999416180965418

    GOLD_COIN_ID = 1448979150948794378
    SEPARATOR_ID = 1448156888066949277

    PERM_EMBED_ID = 1449342831629172826
    PERM_MOG_ID = 1439713022489923730
    PERM_POST_ID = 1437459436829409440
    PERM_REACT_ID = 1436878137647562754

    PERM_ITEMS = {PERM_EMBED_ID, PERM_MOG_ID, PERM_POST_ID, PERM_REACT_ID}
    PRIME_ROLES = {MAIN_ID, OUTSIDER_ID, PRISONER_ID}

    PRISON_VISITATION_ID = 1397259367224442962
    PURSE_ID = 1449214693091840131

    CRIME_MAP = {1396611518153625703: 'SEX OFFENDER', 1396672806867046461: 'MURDERER', 1396672632539189339: 'PROSTITUTE',
        1396672163196698674: 'STRAIGHT', 1396673043903938711: 'BULLY'}

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._colors = {}
        # Load colors database: Used to dynamically create color roles.
        with open(self.FILE_COLOR) as f:
            for line in f.readlines():
                role_id, hex_code = line.split(',')
                self._colors[int(role_id)] = hex_code.strip()
        self._score = {}
        # Load score database: Used to keep track of user levels and scores.
        with open(self.FILE_SCORE) as f:
            for i, line in enumerate(f.readlines()):
                user_id, level_role_id, posts, score = line.split(',')
                self._score[int(user_id)] = [i, int(level_role_id), int(posts), int(score)]
        # Load level role database: Used to dynamically create level roles.
        self._level = []
        with open(self.FILE_LEVEL) as f:
            for role_id in f.readlines():
                self._level.append(int(role_id))
        # Load item database: Used to dynamically create item roles.
        self._items = {}
        with open(self.FILE_ITEMS) as f:
            for line in f.readlines():
                role_id, points = line.split(',')
                self._items[int(role_id)] = int(points)

    @commands.Cog.listener()
    async def on_member_join(self, member: Member) -> None:
        # Assign new member roles
        for role_id in [self.OUTSIDER_ID, self._level[0], self.PERM_POST_ID, self.PERM_REACT_ID]:
            await member.add_roles(member.guild.get_role(role_id))
        # Initialize score
        self._score[member.id] = [len(self._score), self._level[0], 0, 0]
        # Update database
        with open(self.FILE_SCORE, 'a') as f:
            f.write(f"{member.id:<20},{self._level[0]:<20},0000000000000,0000000000000\n")
        # Welcome new member
        embed = Embed(title='Outsider Identified',
            description=f"Name: {member.name}\nAlias: {member.mention}",
            color=member.guild.get_role(self._level[0]).color)
        embed.set_image(url=member.display_avatar.url)
        await member.guild.system_channel.send(embed=embed)
        return None

    @commands.Cog.listener()
    async def on_member_remove(self, member: Member) -> None:
        await self._collect_items(member.guild.get_member(self.ADMIN_USER_ID), member)
        await self._show_stats(member.guild.system_channel, member, f"{member.name.title()} Left")
        # Delete member from database (rewrite)
        del self._score[member.id]
        with open(self.FILE_SCORE, 'w') as f:
            for i, member_id, stats in enumerate(self._score.items()):
                self._score[member_id][0] = i
                f.write(f"{member_id:<20},{stats[1]:<20},{stats[2]:0>13},{stats[3]:0>13}\n")
        return None

    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.author.bot or message.content.startswith('!slave'):
            return None
        await self._increase_posts(message.author)
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
        main = context.guild.get_role(self.MAIN_ID)
        outsider = context.guild.get_role(self.OUTSIDER_ID)
        if isinstance(member, Member):
            if not member.get_role(self.MAIN_ID):
                await context.send(f"{member.mention} must be a member of {main.mention}.")
                return None
            vote = {context.author.id}
            await context.send(f"Two additional members must respond with 'yes' to exile {member.mention}.")
            try:
                await bot.wait_for('message', timeout=10, check=lambda m: yes_from_respondent(context, m))
                await context.send(f"One additional member must respond with 'yes' to exile {member.mention}")
                await bot.wait_for('message', timeout=10, check=lambda m: yes_from_respondent(context, m))
            except TimeoutError:
                await context.send('Timeout: Aborted.')
                return None
            await member.remove_roles(main)
            await member.add_roles(outsider)
            title = f"Citizen {member.display_name} Was Exhiled"
            await self._send_report(outsider.color, context, False, crime, member, title, text)
            return None
        await context.send(
            f"Exile {main.mention} Citizen to {outsider.mention}:\n"
            f"{self._color_code_message('slave', 'exile', '@Member', '')}\n"
            'Attach the Commandment Channel:\n'
            f"{self._color_code_message('slave', 'exile', '@Member ', '#Channel', '')}\n"
            'Attach an optional message:\n'
            f"{self._color_code_message('slave', 'exile', '@Member ', '<message-id>')}\n"
            'Include an optional message:\n'
            f"""{self._color_code_message('slave', 'exile', '@Member ', '"Offensive speech!"')}\n"""
            'Combinations:\n'
            f"{self._color_code_message('slave', 'exile', '@Member ', '#Channel ', '<message-id>')}\n"
            f"""{self._color_code_message('slave', 'exile', '@Member ', '#Channel ', '"Offensive speech!"')}\n"""
            f"""{self._color_code_message('slave', 'exile', '@Member ', '<message-id> ', '"Offensive speech!"')}""")
        return None

    @slave.command()
    async def gift(self, context: Context, member: MemberOrStr, item: RoleOrStr) -> None:
        if isinstance(member, Member) and isinstance(item, Role):
            # Make sure item is giftable
            if item.id in self._items:
                container = self._items
                points = self._items[item.id]
            elif item.id in self.PERM_ITEMS:
                if member.get_role(item.id):
                    await context.send(f"{member.mention} already has a {item.mention}.")
                    return None
                container = [item.id]
                points = 0
            else:
                await context.send(f"{item.mention} is not a giftable item.")
                return None
            # Make sure author has item
            author_items = set()
            for role in context.author.roles:
                if role.id in container:
                    author_items.add(role)
                    break
            if not author_items:
                await context.send(f"{context.author.mention} does not have a {item.mention} to gift.")
            elif context.author.id == member.id:
                await context.send(f"You cannot gift yourself {item.mention}.")
            else:
                # Gift member item
                gift = author_items.pop()
                await context.author.remove_roles(gift)
                await member.add_roles(gift)
                await context.send(f"{member.mention} recieved {gift.mention} from {context.author.mention}.")
                if points:
                    self._decrease_score(context.author, points)
                    self._increase_score(member, points)
                return None
        await context.send(
            f"Gift an item to another member:\n"
            f"{self._color_code_message('slave', 'gift', '@Member', '@Item')}")
        return None

    @slave.command()
    async def paint(self, context: Context, member: Mention = '', role: RoleOrStr = '', *args: Role) -> None:
        async def create_new_color(name: str, hexcode: str) -> None:
            # Create new color role
            color = Color.from_str(hexcode)
            new_color = await self._create_role(name.title(), context.guild.me.top_role.position, color)
            # Update database
            self._colors[new_color.id] = hexcode
            with open(self.FILE_COLOR, 'a') as f:
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
            n = len(hexes)
            r, g, b = round(r / n), round(g / n), round(b / n)
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
            # Search database for color role
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
                    for color_role in [role] + args:
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
            await context.send(f"Interpreted input {offender} as a @Color role.\nColor not found.")
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
                'Paint yourself a Color:\n'
                f"{self._color_code_message('slave', 'paint', '', '@Color')}\n"
                'Paint a Member a Color:\n'
                f"{self._color_code_message('slave', 'paint', '@Member ', '@Color')}\n"
                'Look up a Color:\n'
                f"{self._color_code_message('slave', 'paint show', '', '#RRGGBB')}\n"
                f"{self._color_code_message('slave', 'paint show', '', '@Color')}\n"
                'Mix Colors:\n'
                f"{self._color_code_message('slave', 'paint', '@Color ', '@Color ', '...')}\n"
                'Create a new Color:\n'
                f"""{self._color_code_message('slave', 'paint', '"Color Name" ', '#RRGGBB')}\n""")
        return None

    @slave.command()
    async def roll(self, context: Context, bet: RoleOrInt = 0, bet_type: str = 'pass line') -> None:
        def roll_from_respondent(context: Context, message: Message) -> bool:
            if ((message.author.id == context.author.id) and (message.channel == context.channel) 
                    and (message.content.lower().strip() == 'roll')):
                return True
            return False

        async def winner() -> None:
            await context.send(f"{context.author.mention} Won!")
            if bet_role:
                await house.remove_roles(house_role)
                await context.author.add_roles(house_role)
            if bet:
                self._increase_score(context.author, bet)

        async def loser() -> None:
            await context.send(f"{context.author.mention} Lost!")
            if bet_role:
                await house.add_roles(author_role)
                await context.author.remove_roles(author_role)
            if bet:
                self._decrease_score(context.author, bet)
    
        # Input massage
        if bet and isinstance(bet, int):
            if bet > self._get_score(context.author):
                await context.send(f"{context.author.mention} does not have {bet} points to bet.")
                return None
            bet_role = None
        elif isinstance(bet, Role):
            gold_coin = context.guild.get_role(self.GOLD_COIN_ID)
            if bet not in self._items:
                await context.send(f"Bet points or {gold_coin.mention}, not {bet.mention}.")
                return None
            for author_role in context.author.roles:
                if author_role.id in self._items:
                    break
            else:
                await context.send(f"{context.author.mention} does not have a {gold_coin.mention} to bet.")
                return None
            house = context.guild.get_member(self.ADMIN_USER_ID)
            for house_role in house.roles:
                if house_role.id in self._items:
                    break
            else:
                await context.send(f"House currently cannot payout a {gold_coin.mention}. More must be minted.")
                return None
            bet_role = bet
            bet = self._items[bet_role.id]
        else:
            bet_role = None
        dice_map = {}
        # Come-out Roll
        dice_1, dice_2 = randint(1, 6), randint(1, 6)
        point = dice_1 + dice_2
        if (point == 7) or (point == 11):
            winner()
        elif (point == 2) or (point == 3) or (point == 12):
            loser()
        # The Point Phase
        await context.send(f"You rolled a {point}")
        score = point
        while True:
            await context.send('Roll again by typing "roll."')
            try:
                await bot.wait_for('message', timeout=30, check=lambda m: roll_from_respondent(context, m))
            except TimeoutError:
                await context.send(f"Timeout: {context.author.mention} Lost!")
                return None
            dice_1, dice_2 = randint(1, 6), randint(1, 6)
            score = dice_1 + dice_2
            await context.send(f"You rolled a {score}")
            if score == point:
                winner()
                break
            elif score == 7:
                loser()
                break
        return None

    @slave.command()
    async def stats(self, context: Context, member: Member) -> None:
        self._show_stats(context.channel, member, 'Member Stats')
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
            copy_item = await self._create_role(item.name, item.position, item.color)
            # Update database
            self._items[copy_item.id] = self._items[item.id]
            with open(self.FILE_ITEMS, 'a') as f:
                f.write(f"\n{copy_item.id:<20},{self._items[copy_item.id]:0>13}")
            # Give to member
            await member.add_roles(copy_item)
            await context.send(f"{member.mention} recieved {copy_item.mention}")
            # Create item channel under purse channel
            channel = context.guild.get_channel(self.PURSE_ID)
            permissions = PermissionOverwrite(
                view_channel=True, send_messages=False, create_public_threads=False, create_polls=False)
            new_channel = await context.guild.create_text_channel(
                name='🪙gold-coin', category=channel.category, overwrites={copy_item: permissions},
                position=channel.position + 1)
            await new_channel.send(
                content=f"{copy_item.mention}\n⭐ Worth 250 Points", file=File('database/items/coin.png'))
            # Send item creation message
            embed = Embed(title='New Item Created',
                description=f"{copy_item.mention}\n⭐ Worth 250 Points", color=copy_item.color)
            file = File('database/items/coin.png', filename='coin.png')
            embed.set_image(url=f"attachment://coin.png")
            embed.set_author(name=context.author.display_name, icon_url=context.author.display_avatar.url)
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(name='', value=f"{member.mention} was gifted a {copy_item.mention}")
            await context.guild.system_channel.send(embed=embed, file=file)
            # Update score
            await self._increase_score(member, self._items[copy_item.id])
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
                with open(self.FILE_COLOR, 'w') as f:
                    for role_id, color_hex in self._colors.items():
                        f.write(f"{role_id},{color_hex}\n")
        return None

    @master.command()
    async def erase(self, context: Context, target_id: MemberOrStr = '') -> None:
        def yes_from_master(context: Context, message: Message) -> bool:
            return (self._is_master_user(context) and (message.channel == context.channel)
                and (message.content.lower().strip() == 'yes'))

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
            self._collect_items(context.author, member)
            await self._clear_score(member)
            # Strip and change member roles
            await member.remove_roles(*[role for role in member.roles if role != member.guild.default_role])
            level_zero_role = await context.guild.get_role(self._level[0])
            await member.add_roles(*[self.PRISONER_ID, self.PERM_POST_ID, level_zero_role])
            color = await context.guild.get_role(self.PRISONER_ID).color
            await self._send_report(color, context, True, crime, member, 'Criminal Identified', text)
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
        outsider = context.guild.get_role(self.OUTSIDER_ID)
        prisoner = context.guild.get_role(self.PRISONER_ID)
        if isinstance(member, Member):
            role = member.get_role(self.OUTSIDER_ID)
            if not role:
                role = member.get_role(self.PRISON_VISITATION_ID)
                if not role:
                    await context.send(f"{member.mention} must be a {outsider.mention} or {prisoner.mention}.")
                    return None
            await self._send_report(
                context.guild.get_role(self.MAIN_ID).color, context, False, text,
                f"{role.name.title()} Has Been Liberated", '')
            return None
        await context.send(
            f"Liberate an {outsider.mention} or a {prisoner.mention}:\n"
            F"{self._color_code_message('slave', 'master liberate', '@Member', '')}\n"
            f"Attach an optional message:\n{self._color_code_message('slave', 'master liberate', '@Member ', '<message-id>')}\n"
            f"""Include an optional message:\n{self._color_code_message('slave', 'master liberate', '@Member ', '"Confessed to their sin."')}""")
        return None

    @master.command()
    async def mute(self, context: Context, member: Member) -> None:
        await self._is_master(context)
        post_perm_role = context.guild.get_role(self.PERM_POST_ID)
        if member.get_role(self.PERM_POST_ID):
            await member.remove_roles(post_perm_role)
            text1 = f"🤐 Muted!"
            text2 = 'Removed'
        else:
            await member.add_roles(post_perm_role)
            text1 = f"🔊 Unmuted!"
            text2 = 'Recieved'
        color = None
        for role in member.roles:
            if role.id in self._colors:
                color = role
                break
        if not color:
            color = context.guild.get_role(self._score[member.id][1])
        embed = Embed(title=text1, description=f"{member.mention} {text2} {post_perm_role.mention}.", color=color.color)
        embed.set_author(name=context.author.display_name, icon_url=context.author.display_avatar.url)
        embed.set_thumbnail(url=member.display_avatar.url)
        await context.guild.system_channel.send(embed=embed)
        return None

    def _calc_level(self, member: Member) -> int:
        score = self._score[member.id][3]
        A = 9910.10197
        a, b, c  = A / 9801, 0.89797, score - 1
        x = 1 + (sqrt(abs(b*b - 4*a*c)) - b) / (2*a)
        return int(x)

    async def _clear_score(self, member: Member) -> None:
        member_ref = self._score[member.id]
        self._score[member.id] = [member_ref[0], member_ref[1], 0, 0]
        await self._level_up(member)
        return None

    async def _collect_items(self, author: Member, member: Member) -> None:
        items = set()
        points = 0
        for role in member.roles:
            if role.id in self._items:
                items.add(role)
                points += self._items[role.id]
        if items:
            await author.add_roles(*items)
            await self._increase_score(author, points)
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

    async def _create_role(self, name: str, position: int, color: Color) -> Role:
        guild = self.bot.get_guild(self.SERVER_ID)
        if len(guild.roles) == 250:
            # Delete random color role
            role_ids = list(self._colors.keys())
            random_role = guild.get_role(role_ids[randint(0, len(role_ids) - 1)])
            await guild.system_channel.send(f"Maximum roles encountered. Deleted role {random_role.mention}.")
            await random_role.delete()
            # Update database (rewrite)
            del self._colors[random_role.id]
            with open(self.FILE_COLOR, 'w') as f:
                for role_id, color_hex in self._colors.items():
                    f.write(f"{role_id},{color_hex}\n")
        new_role = await guild.create_role(name=name, color=color)
        await guild.edit_role_positions(positions={new_role: position})
        return new_role

    async def _decrease_score(self, member: Member, points: int) -> None:
        self._score[member.id][3] -= points
        await self._level_up(member, member.guild.system_channel)
        return None

    async def _is_master(self, context: Context) -> None:
        if self._is_master_user(context):
            return None
        await context.send(f"You are not my master: {context.author.display_name}.")
        raise commands.CheckFailure(f"User {context.author.display_name} is not master.")

    async def _get_message_embed(self, context: Context, message_id: int) -> Embed:
        message = await context.channel.fetch_message(message_id)
        embed = Embed(description=message.content, timestamp=message.created_at)
        embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
        embed.add_field(name="Criminal Message", value=f"[{message.id}]({message.jump_url})", inline=False)
        if message.attachments:
            embed.set_image(url=message.attachments[0].url)
        return embed

    def _get_posts(self, member: Member) -> int:
        return self._score[member.id][2]

    def _get_score(self, member: Member) -> int:
        return self._score[member.id][3]

    async def _show_stats(self, channel: TextChannel, member: Member, title: str) -> None:
        # Collect member items, color, and primary role
        suffix_map = {'0': 'th', '1': 'th', '2': 'nd', '3': 'rd', '4': 'th', '5': 'th',
                      '6': 'th', '7': 'th', '8': 'th', '9': 'th', 'first': 'st'}
        color, prime = None, None
        coins, items = set(), set()
        for role in member.roles:
            if role.id in self.PERM_ITEMS:
                items.add(role)
            elif role.id in self._items:
                coins.add(role)
            elif role.id in self._colors:
                color = role
            elif role.id in self.PRIME_ROLES:
                prime = role
        # Get level and place
        level = member.guild.get_role(self._score[member.id][1])
        if not color:
            color = level
        place = 1
        for member_i in member.guild.members:
            if self._get_score(member_i) > self._get_score(member):
                place += 1
        suffix_key = str(place)
        if (place == 1) or ((suffix_key[-1] == '1') and (len(suffix_key) > 2)):
            suffix_key = 'first'
        else:
            suffix_key = suffix_key[-1]
        # Show stats
        embed = Embed(title=title,
            description=(f"**Place**: {place}{suffix_map[suffix_key]}\n"
                         f"**Alias**: {member.mention}\n"
                         f"**Level**: {level.mention}\n"
                         f"**State**: {prime.mention}\n"
                         f"**Color**: {color.mention}\n"
                         f"**Score**: {self._get_score(member):0>13}\n"
                         f"**Posts**: {self._score[member.id][2]:0>13}"),
            color=color.color)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name='Items:', value=', '.join([role.mention for role in items]), inline=False)
        embed.add_field(name='Purse:', value=', '.join([role.mention for role in coins]), inline=False)
        await channel.send(embed=embed)
        return None

    def _is_master_user(self, context: Context) -> bool:
        return (context.author.id == self.ADMIN_USER_ID) or any(role.id == self.ADMIN_ROLE_ID for role in context.author.roles)

    async def _send_report(self, color: Color, context: Context, convict: bool, crime: Text, member: Member, title: str, text: str) -> None:
        # Massage input
        msg_embed = []
        note = ''
        if convict:
            report_id = self.PRISON_VISITATION_ID
        else:
            report_id = context.guild.system_channel.id
        if isinstance(crime, TextChannel) and (crime.id in self.CRIME_MAP):
            report_id = crime.id
            note = f"\nOffense: {crime.mention}"
            if convict:
                note = f"{note}\nConvicted: {self.CRIME_MAP[report_id]}\nSentence: TBD"
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
        await context.send(embed=embed)
        return None

    async def _increase_posts(self, member: Member, posts: int = 1) -> None:
        self._score[member.id][2] += posts
        await self._increase_score(member, posts)
        return None

    async def _increase_score(self, member: Member, points: int) -> None:
        self._score[member.id][3] += points
        await self._level_up(member)
        return None

    async def _level_up(self, member: Member) -> None:
        level_role = member.get_role(self._score[member.id][1])
        curr_lvl_n = int(level_role.name.removeprefix('LVL '))
        next_lvl_n = self._calc_level(member)
        if next_lvl_n != curr_lvl_n:
            if next_lvl_n > curr_lvl_n:
                title = 'New Level Unlocked'
                prefix = 'up'
                # Create level roles if new level not found in level list.
                if (len(self._level) - 1) < next_lvl_n:
                    level_len_freeze = len(self._level)
                    for i in range(next_lvl_n - level_len_freeze + 1):
                        level = level_len_freeze + i
                        index = member.guild.get_role(SEPARATOR_ID).position
                        new_level_role = await self._create_role(f"LVL {level}", index, Color.random())
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
            if not member.get_role(self.PRISONER_ID):
                # Level up message
                filename = f"{(next_lvl_n % 2) + 1}.png"
                embed = Embed(title=title,
                    description=f"{member.mention} {prefix}graded from {level_role.mention} to {new_level_role.mention}",
                    color=new_level_role.color)
                file = File(f"database/images/{filename}", filename=filename)
                embed.set_image(url=f"attachment://{filename}")
                embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
                guild = self.bot.get_guild(self.SERVER_ID)
                await guild.system_channel.send(embed=embed, file=file)
        # Update database
        member_ref = self._score[member.id]
        with open(self.FILE_SCORE, 'r+') as f:
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
