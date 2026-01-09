from discord import (app_commands, Guild, Intents, Interaction, Member, Message, Object,
    Permissions, RawReactionActionEvent, Role)
from discord.ext import commands
from emoji import distinct_emoji_list

from game import Game
from paint import Paint


class Base(commands.Cog):

    GUILD_ID = 1455730008273195032

    def __init__(self, bot: commands.Bot, guild: Guild):
        self.bot = bot
        self.gamer = Game(guild)
        self.guild = guild
        self.color = Paint()

    @commands.Cog.listener()
    async def on_member_join(self, member: Member) -> None:
        await member.add_roles(*[self.gamer.roles['Level'][0], self.gamer.roles['💀'],
            self.gamer.roles['💎🪨🕹️'], self.gamer.roles['Outsider']])
        await self.gamer.setup.send_img(
            self.gamer.roles['Outsider'], member.guild.system_channel, 'meilanliu',
            f"Name: {member.name}\nAlias: {member.mention}", 'Outsider Identifed', member)
        await member.guild.system_channel.send(f"{member.mention}, why are you here?")
        return None

    @commands.Cog.listener()
    async def on_member_remove(self, member: Member) -> None:
        await self.gamer.delete(member)
        return None

    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.author.bot:
            return None
        await self.gamer.increase_posts(message.author)
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

    gift = app_commands.Group(name='gift', description='Gift an item')

    sell = app_commands.Group(name='sell', description='Sell a purchasable item')

    trade = app_commands.Group(name='trade', description='Trade an item')

    paint = app_commands.Group(name='paint', description='Commands for managing colors')

    @app_commands.describe(
        color_name='Name of color to create', color_hex='Hex code in the form #RRGGBB')
    @paint.command(name= 'make', description='Create a new color.')
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
        if distinct_emoji_list(color_name):
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
        await interaction.response.defer()
        role = await self.gamer.setup.role(
            color_name.title(), color_hex, ref_role=self.guild.me.top_role)
        self.color.update(role.id, color_hex)
        await self.gamer.setup.send_img(role, interaction.channel, color_hex.lstrip('#').upper(),
            f"**Created**: {role.mention}", '')
        await interaction.followup.send('**New Color Created**')
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
        await self.gamer.setup.send_img(role, interaction.channel, new_hex.lstrip('#').upper(),
            f"**Created**: {role.mention}", '')
        await interaction.followup.send('**New Color Created**')
        return None

    @app_commands.describe(player='Player to color', color_role='Selected color')
    @paint.command(name='player', description='Color yourself or another player')
    async def player(self, interaction: Interaction, player: Member, color_role: Role) -> None:
        if not self.color.id_exists(color_role.id):
            await interaction.response.send_message(f"Color not found: {color_role.mention}.")
            return None
        await player.remove_roles(
            *[role for role in player.roles if self.color.id_exists(role.id)])
        await player.add_roles(color_role)
        await interaction.response.send_message(
            f"{interaction.user.mention} colored {player.mention} {color_role.mention}.")
        return None

    @app_commands.describe(color_role='Selected color')
    @paint.command(name='show', description='Look up a color')
    async def show(self, interaction: Interaction, color_role: Role) -> None:
        if not self.color.id_exists(color_role.id):
            await interaction.response.send_message(f"Color not found: {color_role.mention}.")
            return None
        filename = self.color.get(color_role.id).lstrip('#')
        await self.gamer.setup.send_img(color_role, interaction.channel, filename, '', '')
        resp = f"**Showing Color**: {color_role.mention}"
        if interaction.response.is_done():
            await interaction.followup.send(resp)
            return None
        await interaction.response.send_message(resp)
        return None

    delete = app_commands.Group(name='delete', description='Administrator commands',
        default_permissions=Permissions(administrator=True))

    @delete.command()
    async def channels(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        for i, channel in enumerate(interaction.guild.channels):
            if channel.id != interaction.channel.id:
                await channel.delete()
        await interaction.followup.send(f"Deleted {i} channels.")
        return None

    @delete.command()
    async def role(self, interaction: Interaction, role: Role) -> None:
        await role.delete()
        await interaction.followup.send(f"{role.mention} deleted.")
        return None

    master = app_commands.Group(name='master', description='Administrator commands',
        default_permissions=Permissions(administrator=True))

    @master.command()
    async def create(self, interaction: Interaction, member: Member, item_role: Role) -> None:
        if member.bot:
            await interaction.response.send_message(f"Cannot create {member.mention} an item.")
            return None
        new_item_list = distinct_emoji_list(item_role.name)
        if new_item_list:
            item_key = new_item_list[0]
            extra_items, owned_items = set(), set()
            if item_key in self.gamer.setup.perm_items:
                # Handles permission item roles
                # Note: Permission roles are overly complicated.
                # Creating stacked items that act as combined permissions is more complicated,
                # but it looks cool
                for cur_role in member.roles:
                    if cur_role.name in self.gamer.setup.perm_items:
                        for owned_item in distinct_emoji_list(cur_role.name):
                            owned_items.add(owned_item.mention)
                            if owned_item in new_item_list:
                                extra_items.add(owned_item.mention)
                        if len(extra_items) == len(new_item_list):
                            await interaction.response.send_message(
                                f"{member.mention} already has item {', '.join(extra_items)}")
                            return None
                        new_stack = owned_items
                        new_stack.update(set(new_item_list))
                        new_stack = ''.join(sorted(new_stack, key=lambda s: '📜🔮💎🪨🕹️'.find(s)))
                        break
                else:
                    cur_role = None
                    new_stack = item_role.name
            else:
                # Handles all other item roles (Stacks up to 3)
                for cur_role in member.roles:
                    if item_key in cur_role.name:
                        owned_items.update(set(distinct_emoji_list(cur_role.name)))
                        if len(owned_items) == 3:
                            await interaction.response.send_message(
                                f"{member.mention} already has the max stack {cur_role.mention}.")
                            return None
                        n_items = len(new_item_list) + len(owned_items)
                        if n_items > 3:
                            for _ in range(n_items - 3):
                                extra_items.add(item_key)
                            n_items = 3
                        new_stack = item_key * n_items
                        break
                else:
                    cur_role = None
                    new_stack = item_role.name
            if extra_items:
                await interaction.channel.send(
                    f"{member.mention} already had item {', '.join(extra_items)}.")
            points = 0
            created_items = new_item_list - extra_items
            for new_item in created_items:
                points += self.gamer.setup.all_items[new_item].points
            await self.gamer.increase_score(member, points)
            created_items_str = ', '.join(self.role[item].mention for item in created_items)
            await interaction.followup.send(
                f"{interaction.user} created {member.member} {created_items_str}")
        return None

    @master.command()
    async def initialize(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        resp = await self.gamer.setup.all()
        await interaction.followup.send(resp)
        return None


if __name__ == "__main__":
    bot = commands.Bot(command_prefix='!', intents=Intents.all())

    @bot.event
    async def on_ready():
        guild = bot.get_guild(GameBot.GUILD_ID)
        await bot.add_cog(GameBot(bot, guild))
        guild = Object(id=GameBot.GUILD_ID)
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)

    with open('database/files/token.txt') as token_file:
        token_raw = token_file.read()

    bot.run(token_raw)
