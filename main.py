from typing import Union

from discord import (app_commands, Guild, Intents,
    Member, Message, Object, RawReactionActionEvent, Role)
from discord.ext import commands
from discord.ext.commands import Context

from game import Game


class Base(commands.Cog):

    GUILD_ID = 1455730008273195032

    def __init__(self, bot: commands.Bot, guild: Guild):
        self.bot = bot
        self.gamer = Game(guild)
        self.guild = guild

    async def cog_before_invoke(self, context: Context) -> None:
        if context.interaction and not context.interaction.response.is_done():
            await context.interaction.response.defer()
        return None

    @staticmethod
    def get_author(context: Context) -> Member:
        if context.interaction:
            return context.interaction.user
        return context.author

    @commands.Cog.listener()
    async def on_member_join(self, member: Member) -> None:
        await member.add_roles(*[self.gamer.roles['Level'][0], self.gamer.roles['💀'],
            self.gamer.roles['💎'], self.gamer.roles['🪨'], self.gamer.roles['🕹️'],
            self.gamer.roles['Outsider']])
        await self.gamer.send_img(
            self.gamer.roles['Outsider'], member.guild.system_channel, 'meilanliu',
            f"Name: {member.name}\nAlias: {member.mention}", 'Outsider Identifed', member)
        await member.guild.system_channel.send(
            f"{member.mention}, why are you here?")
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

    @staticmethod
    async def hybrid_fail(context: Context, message: str) -> None:
        if context.interaction:
            if context.interaction.response.is_done():
                await context.interaction.followup.send(message)
            await context.interaction.response.send_message(message)
            raise app_commands.CheckFailure()
        await context.send(message)
        raise commands.CheckFailure()

    @staticmethod
    async def hybrid_reply(context: Context, content: str) -> Union[Message, None]:
        if context.interaction:
            if context.interaction.response.is_done():
                return await context.interaction.followup.send(content)
            return await context.interaction.response.send_message(content)
        return await context.send(content)


class GameBot(Base):

    ADMIN_USER_ID = 1380323054479085648
    ADMIN_ROLE_ID = 0

    @commands.hybrid_group()
    async def paint(self, context: Context) -> None:
        pass

    @paint.command()
    async def make(self, context: Context, color_name: str, color_hex: str) -> None:
        paint_id = self.gamer.paint.get(color_hex)
        if paint_id:
            role = context.guild.get_role(paint_id)
            resp = f"Color already exists: {role.mention}."
            await self.show(context, role)
        elif not self.gamer.paint.is_hexcode(color_hex):
            resp = f"Color must be hex code in the form #RRGGBB."
        else:
            resp = await self.gamer.create_color(context, color_name.title(), color_hex)
        await self.hybrid_reply(context, resp)
        return None

    @paint.command()
    async def mix(self, context: Context, color1: Role, color2: Role) -> None:
        for role in [color1, color2]:
            if not self.gamer.paint.id_exists(role.id):
                resp = f"{role.mention} is not a color."
                break
        else:
            new_code = self.gamer.paint.mix(
                self.gamer.paint.get(color1.id), self.gamer.paint.get(color2.id))
            paint_id = self.gamer.paint.get(new_code)
            if paint_id:
                role = context.guild.get_role(paint_id)
                resp = f"Color already exists: {role.mention}."
                await self.show(context, role)
            else:
                new_name = f"{color1.name} {color2.name}"
                resp = await self.gamer.create_color(context, new_name, new_code)
        await self.hybrid_reply(context, resp)
        return None

    @paint.command()
    async def player(self, context: Context, player: Member, color_role: Role) -> None:
        if not self.gamer.paint.id_exists(color_role.id):
            resp = f"Color not found: {color_role.mention}."
        else:
            await self.gamer.paint.remove_from(player)
            await player.add_roles(color_role)
            author = self.get_author(context)
            resp = f"{author.mention} colored {player.mention} {color_role.mention}."
        await self.hybrid_reply(context, resp)
        return None

    @paint.command()
    async def show(self, context: Context, color_role: Role) -> None:
        if not self.gamer.paint.id_exists(color_role.id):
            resp = f"Color not found: {color_role.mention}."
        else:
            filename = self.gamer.paint.get(color_role.id).lstrip('#')
            await self.gamer.send_img(color_role, context.channel, filename, '', '')
            resp = f"**Showing Color**: {color_role.mention}"
        await self.hybrid_reply(context, resp)
        return None

    def is_master(self, context: Context) -> bool:
        author = self.get_author(context)
        return (author.id == self.ADMIN_USER_ID) or (author.get_role(self.ADMIN_ROLE_ID))

    @app_commands.check(is_master)
    @commands.check(is_master)
    @commands.hybrid_group()
    async def master(self, context: Context) -> None:
        await self.hybrid_reply(context, f"Hi, {self.get_author(context).display_name}.")
        return None

    @master.command()
    async def initialize(self, context: Context) -> None:
        resp = await self.gamer.initialize()
        for member in context.guild.members:
            await member.add_roles(*[self.gamer.roles['Level'][0], self.gamer.roles['💀'],
                self.gamer.roles['💎'], self.gamer.roles['🪨'], self.gamer.roles['🕹️'],
                self.gamer.roles['Outsider']])
        await self.hybrid_reply(context, resp)
        return None

    @master.command()
    async def reset(self, context: Context) -> None:
        resp = await self.gamer.reset()
        await self.hybrid_reply(context, resp)
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
