from datetime import datetime
from io import BytesIO
from random import randint
from zoneinfo import ZoneInfo

from discord import (app_commands, Color, Embed, File, Guild, Intents, Interaction, Member,
    Message, MessageType, Object, Permissions, RawBulkMessageDeleteEvent, RawMessageDeleteEvent,
    RawReactionActionEvent, Role, TextChannel)
from discord.errors import NotFound
from emoji import replace_emoji
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw, ImageFont
from discord.ext import commands, tasks

from game import BabySlime, Game, GoldNeko, Skyevolutrex, MommySlime
from paint import Paint
from utils import get_emoji_list


class Base(commands.Cog):

    GUILD_ID = 1455730008273195032

    def __init__(self, bot: commands.Bot, guild: Guild):
        self.bot = bot
        self.color = Paint()
        self.gamer = Game(guild)
        self.guild = guild

    async def cog_load(self) -> None:
        await self.gamer.load_npcs()
        self.game_loop.start()
        return None

    def cog_unload(self) -> None:
        self.game_loop.cancel()
        return None

    @tasks.loop(hours=8)
    async def game_loop(self) -> None:
        _, npc = list(self.gamer.npcs.items())[randint(0, len(self.gamer.npcs) - 1)]
        await npc.send_passive_dialogue()
        return None

    @game_loop.before_loop
    async def before_game_loop(self) -> None:
        await self.bot.wait_until_ready()
        return None

    @commands.Cog.listener()
    async def on_member_join(self, member: Member) -> None:
        await member.add_roles(self.gamer.roles['Level'][0], self.gamer.roles['💀'],
            self.gamer.roles['💎🪨🕹️'], self.gamer.roles['Outsider'])
        await self.gamer.setup.send_img(self.gamer.roles['Outsider'], 'meilanliu',
            f"Name: {member.name}\nAlias: {member.mention}", 'Outsider Identified', member)
        skyevolutrex = self.gamer.npcs.get(Skyevolutrex.alias)
        await skyevolutrex.webhook.send(f"{member.mention}, why are you here?")
        await skyevolutrex.send_passive_dialogue()
        goldneko = self.gamer.npcs.get(GoldNeko.alias)
        await goldneko.webhook.send(f"An outsider has arrived: {member.mention}.")
        await goldneko.send_passive_dialogue()
        return None

    @commands.Cog.listener()
    async def on_member_remove(self, member: Member) -> None:
        await self.gamer.delete(member)
        return None

    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.type == MessageType.new_member:
            return None
        await self.gamer.increase_posts(message.author)
        return None

    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, payload: RawBulkMessageDeleteEvent):
        for message in payload.cached_messages:
            await self.gamer.decrease_posts(message.author)
        return None

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload: RawMessageDeleteEvent) -> None:
        if payload.cached_message:
            await self.gamer.decrease_posts(payload.cached_message.author)
        return None

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent) -> None:
        if payload.guild_id != self.GUILD_ID:
            return None
        await self.gamer.increase_reacts(payload.member)
        return None

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent) -> None:
        if payload.guild_id != self.GUILD_ID:
            return None
        await self.gamer.decrease_reacts(self.guild.get_member(payload.user_id))
        return None


class GameBot(Base):

    ADMIN_USER_ID = 1380323054479085648
    ADMIN_ROLE_ID = 0

    buy = app_commands.Group(name='buy', description='Buy a purchasable item')

    gift = app_commands.Group(name='gift', description='Gift an item or points')

    sell = app_commands.Group(name='sell', description='Sell a purchasable item')

    show = app_commands.Group(name='show', description='Display player attributes')

    @show.command()
    async def character(self, interaction: Interaction, channel: TextChannel) -> None:
        await interaction.response.defer(ephemeral=True)
        for webhook in await channel.webhooks():
            if webhook.name in self.gamer.npcs:
                await self.gamer.npcs[webhook.name].send_passive_dialogue()
        await interaction.followup.send('Done.', ephemeral=True)
        return None

    @app_commands.describe(color_role='Selected color')
    @show.command(name='color', description='Look up a color')
    async def show_color(self, interaction: Interaction, color_role: Role) -> None:
        if not self.color.id_exists(color_role.id):
            await interaction.response.send_message(f"Color not found: {color_role.mention}.")
            return None
        filename = self.color.get(color_role.id).lstrip('#')
        await self.gamer.setup.send_img(color_role, filename, '', '', channel=interaction.channel)
        resp = f"**Showing Color**: {color_role.mention}"
        if interaction.response.is_done():
            await interaction.followup.send(resp)
            return None
        await interaction.response.send_message(resp)
        return None

    @app_commands.describe(member='Player to show stats of')
    @show.command(name='stats', description='Show player stats')
    async def stats(self, interaction: Interaction, member: Member) -> None:
        coins, items = set(), set()
        color_role = None
        level, perms, state, vigor = '♾️', '♾️', '♾️', '♾️'
        max_stacked = False
        for role in member.roles:
            item_list = get_emoji_list(role.name)
            if item_list:
                item_key = item_list[0]
                if item_key in self.gamer.setup.lives:
                    vigor = role.mention
                elif item_key in self.gamer.setup.extra:
                    coins.add(role.mention)
                elif item_key in self.gamer.setup.perm_single_items:
                    perms = role.mention
                else:
                    items.add(role.mention)
                    if not max_stacked:
                        max_stacked = len(item_list) == 3
            elif self.color.id_exists(role.id):
                color_role = role
            elif role.name.isdigit():
                level = role.mention
            elif role.name in self.gamer.setup.primary_roles:
                state = role.mention
        if not color_role:
            color_role = member.top_role
        player = self.gamer.stats.get_player(member.id)
        embed = Embed(
            description=(
                f"**Place**: {self.gamer.stats.place(member.id)}\n"
                f"**Alias**: {member.mention}\n"
                f"**Vigor**: {vigor}\n"
                f"**Level**: {level}\n"
                f"**State**: {state}\n"
                f"**Perm**: {perms}\n"
                f"**Posts**: {player.posts}\n"
                f"**React**: {player.reacts}\n"
                f"**Score**: {player.score}\n"
                f"**Color**: {color_role.mention}"),
            color=color_role.color)
        embed.set_thumbnail(url=member.display_avatar.url)
        if coins:
            embed.add_field(name='', value=f"**Coins**: {''.join(coins)}", inline=False)
        if items:
            embed.add_field(name='', value=f"**Items**: {''.join(items)}", inline=False)
        if max_stacked:
            embed.add_field(name='MAX STACKED', value='', inline=False)
        await interaction.response.send_message(embed=embed)
        return None

    paint = app_commands.Group(name='paint', description='Commands for managing colors')

    @app_commands.describe(
        color_name='Name of color to create', color_hex='Hex code in the form #RRGGBB')
    @paint.command(name= 'make', description='Create a new color')
    async def make(self, interaction: Interaction, color_name: str, color_hex: str) -> None:
        paint_id = self.color.get(color_hex)
        if paint_id:
            role = interaction.guild.get_role(paint_id)
            await interaction.response.send_message(f"Color already exists: {role.mention}.")
            await self.show(interaction, role)
            return None
        if not self.color.is_hexcode(color_hex):
            await interaction.response.send_message('Color must be hex code in the form #RRGGBB.')
            return None
        if get_emoji_list(color_name):
            await interaction.response.send_message('Colors cannot contain emojis.')
            return None
        if color_name.isdigit():
            await interaction.response.send_message('Colors cannot be numbers.')
            return None
        if color_name in self.gamer.setup.primary_roles:
            primary_roles = self.gamer.setup.primary_roles.keys()
            await interaction.response.send_message(
                f"Colors cannot be a primary role: {', '.join(primary_roles)}.")
            return None
        if color_name.title() == interaction.guild.me.top_role.name:
            await interaction.response.send_message(
                f"Colors cannot be {interaction.guild.me.top_role.mention}.")
        await interaction.response.defer()
        role = await self.gamer.setup.role(
            color_name.title(), color_hex, ref_role=self.guild.me.top_role)
        self.color.update(role.id, color_hex)
        await self.gamer.setup.send_img(role, color_hex.lstrip('#').upper(),
            f"**Created**: {role.mention}", '', channel=interaction.channel)
        await interaction.followup.send('**New Color Created**')
        return None

    @app_commands.describe(member='Member to color', color_role='Selected color')
    @paint.command(name='member', description='Color yourself or another member')
    async def member(self, interaction: Interaction, member: Member, color_role: Role) -> None:
        if not self.color.id_exists(color_role.id):
            await interaction.response.send_message(f"Color not found: {color_role.mention}.")
            return None
        await member.remove_roles(
            *[role for role in member.roles if self.color.id_exists(role.id)])
        await member.add_roles(color_role)
        await interaction.response.send_message(
            f"{interaction.user.mention} colored {member.mention} {color_role.mention}.")
        return None

    @app_commands.describe(color1='First color to mix', color2='Second color to mix')
    @paint.command(name='mix', description='Mix two colors and create a new one')
    async def mix(self, interaction: Interaction, color1: Role, color2: Role) -> None:
        for role in [color1, color2]:
            if not self.color.id_exists(role.id):
                await interaction.response.send_message(f"{role.mention} is not a color.")
                return None
        new_hex = self.color.mix(self.color.get(color1.id), self.color.get(color2.id))
        paint_id = self.color.get(new_hex)
        if paint_id:
            role = interaction.guild.get_role(paint_id)
            await interaction.response.send_message(f"Color already exists: {role.mention}.")
            await self.show(interaction, role)
            return None
        await interaction.response.defer()
        role = await self.gamer.setup.role(
            f"{color1.name} {color2.name}", new_hex, ref_role=self.guild.me.top_role)
        self.color.update(role.id, new_hex)
        await self.gamer.setup.send_img(role, new_hex.lstrip('#').upper(),
            f"**Created**: {role.mention}", '', channel=interaction.channel)
        await interaction.followup.send('**New Color Created**')
        return None

    player = app_commands.Group(name='player', description='Commands for interacting with other players')

    @app_commands.describe(member='Target member')
    @player.command(name='kiss', description='Kiss yourself or another player')
    async def kiss(self, interaction: Interaction, member: Member) -> None:
        await interaction.response.defer()
        await self.gamer.decrease_score(interaction.user, 100)
        await self.gamer.increase_score(member, 100)
        # Need image
        embed = Embed(
            title=f"{interaction.user.display_name.title()} Kissed {member.display_name.title()}!",
            color=Color.red())
        await interaction.guild.system_channel.send(embed=embed)
        if self.gamer.stats.get_player(interaction.user.id).score == 0:
            await self.gamer.remove_heart(
                interaction.user, interaction.channel, interaction.user.display_name)
        await interaction.followup.send(f"{interaction.user.mention} kissed {member.mention}!")
        return None

    @app_commands.describe(member='Target Member')
    @player.command(name='punch', description='Attack yourself or another player')
    async def punch(self, interaction: Interaction, member: Member) -> None:
        await interaction.response.defer()
        for def_role in member.roles:
            if def_role in self.gamer.setup.primary_roles:
                break
        for off_role in interaction.user.roles:
            if off_role.name in self.gamer.setup.primary_roles:
                break
        offen = self.gamer.stats.get_player(interaction.user.id)
        defen = self.gamer.stats.get_player(member.id)
        attack = offen.attack()
        damage = defen.defend(attack)
        await self.gamer.decrease_score(member, damage)
        await self.gamer.increase_score(interaction.user, damage)
        # Need image
        embed = Embed(
            title=f"Level {offen.level} {off_role.name} Punched Level {defen.level} {def_role.name}!",
            description=f"{interaction.user.mention} punched {member.mention}!",
            color=Color.red())
        embed.add_field(name='Attack', value=attack)
        embed.add_field(name='Damage', value=damage)
        await interaction.guild.system_channel.send(embed=embed)
        if self.gamer.stats.get_player(member.id).score == 0:
            await self.gamer.remove_heart(
                member, interaction.channel, interaction.user.display_name)
        await interaction.followup.send(f"{interaction.user.mention} punched {member.mention}!")
        return None

    delete = app_commands.Group(name='delete', description='Administrator commands',
        default_permissions=Permissions(administrator=True))

    @delete.command(name='channels')
    async def delete_channels(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        for i, channel in enumerate(interaction.guild.channels):
            if channel.id != interaction.channel.id:
                await channel.delete()
        await interaction.followup.send(f"Deleted {i} channels.")
        return None

    @delete.command(name='messages')
    async def delete_messages(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        interaction_message = await interaction.original_response()
        deleted = await interaction.channel.purge(
            before=interaction_message, check=lambda m: not m.pinned)
        n = 0
        async for message in interaction.channel.history(before=interaction_message):
            try:
                await message.delete()
                n += 1
            except NotFound as e:
                await interaction_message.edit(content=f"Error: {e}")
        await interaction.followup.send(f"Deleted {len(deleted) + n} messages.")
        return None

    @delete.command(name='role')
    async def delete_role(self, interaction: Interaction, role: Role) -> None:
        await role.delete()
        if self.color.id_exists(role.id):
            self.color.delete(role.id)
        await interaction.response.send_message(f"{role.mention} deleted.")
        return None

    master = app_commands.Group(name='master', description='Administrator commands',
        default_permissions=Permissions(administrator=True))

    @master.command()
    async def create(self, interaction: Interaction, member: Member, item_role: Role) -> None:
        # Items roles are emojis
        new_item_list = get_emoji_list(item_role.name)
        if not new_item_list:
            await interaction.response.send_message(f"{item_role.mention} is not an item.")
            return None
        await interaction.response.defer()
        item_key = new_item_list[0]
        extra_item_list, owned_item_list = [], []
        if item_key in self.gamer.setup.perm_items:
            # Handles permission item roles
            # Note: Permission roles are overly complicated
            # Creating stacked items that act as combined permissions is more complicated
            # but it looks cool
            for cur_role in member.roles:
                if cur_role.name in self.gamer.setup.perm_items:
                    for owned_item in get_emoji_list(cur_role.name):
                        owned_item_list.append(owned_item)
                        if owned_item in new_item_list:
                            extra_item_list.append(owned_item)
                    if len(extra_item_list) == len(new_item_list):
                        await interaction.followup.send(
                            f"{member.mention} already has item {item_role.mention}")
                        return None
                    new_stack = set(new_item_list) | set(owned_item_list)
                    new_stack = ''.join(sorted(new_stack, key=lambda s: '📜🔮💎🪨🕹️'.find(s)))
                    break
            else:
                cur_role = None
                new_stack = item_role.name
        else:
            # Handles all other item roles (Stacks up to 3)
            for cur_role in member.roles:
                if item_key in cur_role.name:
                    owned_item_list = get_emoji_list(cur_role.name)
                    if len(owned_item_list) == 3:
                        await interaction.followup.send(
                            f"{member.mention} already has the max stack {cur_role.mention}")
                        return None
                    n_items = len(new_item_list) + len(owned_item_list)
                    if n_items > 3:
                        extra_item_list.extend([item_key for _ in range(n_items - 3)])
                        n_items = 3
                    new_stack = item_key * n_items
                    break
            else:
                cur_role = None
                new_stack = item_role.name
        if extra_item_list:
            mention_str = ', '.join([self.gamer.roles[item].mention for item in extra_item_list])
            await interaction.channel.send(f"{member.mention} already had item {mention_str}")
        points = 0
        created_item_list = new_item_list.copy()
        for item in extra_item_list:
            created_item_list.remove(item)
        for new_item in created_item_list:
            points += self.gamer.setup.all_items[new_item].points
        await self.gamer.increase_score(member, points)
        if cur_role:
            await member.remove_roles(cur_role)
        await member.add_roles(self.gamer.roles[new_stack])
        mention_str = ', '.join([self.gamer.roles[item].mention for item in created_item_list])
        await interaction.followup.send(
            f"{interaction.user.mention} created {member.mention} {mention_str}")
        return None

    @master.command()
    async def imprison(self, interaction: Interaction, member: Member, charge: TextChannel) -> None:
        if replace_emoji(charge.name, '') not in self.gamer.setup.rules:
            await interaction.response.send_message(f"Channel {charge.name} is not a crime.")
            return None
        await interaction.response.defer()
        await self.gamer.clear_score(member)
        for life_role in member.roles:
            if life_role.name in self.gamer.setup.lives:
                break
        await member.remove_roles(
            *[role for role in member.roles if role != interaction.guild.default_role])
        await member.add_roles(
            self.gamer.roles['Level'][0], life_role, self.gamer.roles['🪨'], self.gamer.roles['Prisoner'])
        # Create avatar behind bars in visitation channel
        avatar_bytes = await member.display_avatar.replace(format='png', size=512).read()
        with Image.open(BytesIO(avatar_bytes)).convert('RGBA') as avatar_img:
            avatar_img = ImageEnhance.Brightness(avatar_img).enhance(0.50)
            avatar_img = avatar_img.filter(ImageFilter.GaussianBlur(2))
            with Image.open('database/images/jail.png').convert('RGBA') as overlay_img:
                overlay_img = overlay_img.resize(avatar_img.size, resample=Image.Resampling.LANCZOS)
                avatar_img.paste(overlay_img, (0, 0), overlay_img)
            out = BytesIO()
            avatar_img.save(out, format='PNG')
            out.seek(0)
        embed = Embed(title=f"Prisoner {member.id}",
            description=f"Alias: {member.mention}", color=self.gamer.roles['Prisoner'].color)
        embed.set_image(url="attachment://jail.png")
        await interaction.guild.get_channel(1458944209502474525).send(
            embed=embed, file=File(out, filename='jail.png'))
        # Create mugshot with booking card in crime channel
        with Image.open(BytesIO(avatar_bytes)).convert('RGBA') as avatar_img:
            avatar_img = ImageOps.grayscale(avatar_img.convert("RGB")).convert("RGB")
            avatar_img = ImageEnhance.Contrast(avatar_img).enhance(1.6)
            avatar_img = ImageEnhance.Brightness(avatar_img).enhance(0.95)
            w1, h1 = avatar_img.size
            with Image.open('database/images/bookingcard.png').convert('RGBA') as overlay_img:
                name = replace_emoji(member.display_name, ' ').strip()
                serial = str(member.id)
                date =  datetime.now(ZoneInfo('America/New_York')).strftime('%m/%d/%Y %I:%M %p')
                crime = replace_emoji(charge.name, ' ').split('-')[-1].capitalize()
                if len(serial) > len(name):
                    longest = serial
                else:
                    longest = name
                l, s = 0, 0
                while l < w1 / 2:
                    s += 1
                    font = ImageFont.truetype('/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf', s)
                    l = font.getlength(longest)
                w2, h2 = overlay_img.size
                w = int(l) + 20
                h = int(h2 * (w / w2))
                overlay_img = overlay_img.resize((w, h), Image.Resampling.LANCZOS)
                draw = ImageDraw.Draw(overlay_img)
                pady = 5
                line_h, text_h = (h - 2 * pady) / 5, sum(font.getmetrics())
                midd_h = (line_h - text_h) // 2
                for i, text in enumerate([name, str(member.id), date, 'GFP USA', crime]):
                    draw.text(((w - font.getlength(text)) // 2, pady + midd_h + (i * line_h)), text, font=font)
                avatar_img.paste(overlay_img, ((w1 - w) // 2, h1 - h), overlay_img)
            out = BytesIO()
            avatar_img.save(out, format='PNG')
            out.seek(0)
        embed = Embed(title='Criminal Identified!', color=self.gamer.roles['Prisoner'].color)
        embed.set_image(url='attachment://booking.png')
        msg = await charge.send(embed=embed, file=File(out, filename='booking.png'))
        link = f"https://discord.com/channels/{msg.guild.id}/{msg.channel.id}"
        await interaction.followup.send(f"{member.mention} is imprisoned: [{charge.name}]({link})")
        return None

    @master.command()
    async def initialize(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        resp = await self.gamer.setup.all()
        await self.gamer.load_npcs()
        await interaction.followup.send(resp)
        return None

    @master.command()
    async def liberate(self, interaction: Interaction, member: Member) -> None:
        await interaction.response.defer(ephemeral=True)
        if member.get_role(self.gamer.roles['TOWG'].id):
            await interaction.response.send_message(f"{member.mention} is already liberated.")
            return None
        outsider = member.get_role(self.gamer.roles['Outsider'].id)
        prisoner = member.get_role(self.gamer.roles['Prisoner'].id)
        if outsider:
            cur_role = outsider
        elif prisoner:
            cur_role = prisoner
        else:
            await interaction.response.send_message(
                f"Only {outsider.mention} or {prisoner.mention} can be liberated.")
            return None
        new_role = self.gamer.roles['TOWG']
        await member.remove_roles(cur_role)
        await member.add_roles(new_role)
        image = 'liberated'
        file = File(f"database/images/{image}.png", filename=f"{image}.png")
        embed = Embed(title='Liberation',
            description=f"{member.mention} is a liberated {new_role.mention} citizen!",
            color=member.top_role.color)
        embed.set_image(url=f"attachment://{image}.png")
        embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
        await member.guild.system_channel.send(embed=embed, file=file)
        goldneko: GoldNeko = self.gamer.npcs.get(GoldNeko.alias)
        await goldneko.webhook.send(f"{member.mention} has been liberated!")
        await goldneko.send_passive_dialogue()
        await interaction.followup.send(
            f"{member.mention} has been liberated.", ephemeral=True)
        return None

    @master.command()
    async def spawn(self, interaction: Interaction, name: str, channel: TextChannel) -> None:
        str_map = {'baby slime': BabySlime, 'gold neko': GoldNeko, 'skyevolutrex': Skyevolutrex,
            'mommy slime': MommySlime}
        if name in str_map:
            await interaction.response.defer()
            await self.gamer.spawn(channel, str_map[name])
            await interaction.followup.send(f"Created {str_map[name].alias}.")
            return None
        await interaction.response.send_message(f"{name} does not exist.")
        return None


if __name__ == "__main__":
    bot = commands.Bot(command_prefix='!', intents=Intents.all())

    @bot.event
    async def on_ready():
        guild = bot.get_guild(GameBot.GUILD_ID)
        await bot.add_cog(GameBot(bot, guild))
        guild_obj = Object(id=GameBot.GUILD_ID)
        bot.tree.copy_global_to(guild=guild_obj)
        #bot.tree.clear_commands(guild=guild_obj)
        await bot.tree.sync(guild=guild_obj)

    with open('database/files/token.txt') as token_file:
        token_raw = token_file.read()

    bot.run(token_raw)
