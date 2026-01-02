from asyncio import sleep
from typing import Union

from discord import (app_commands, Embed, Guild, Intents,
    Member, Message, Object, RawReactionActionEvent, Role)
from discord.ext import commands
from discord.ext.commands import Context

from game import Game


class Master:

    GUILD_ID = 1455730008273195032

    def __init__(self, bot: commands.Bot, guild: Guild):
        self.bot = bot
        self.gamer = Game()
        self.guild = guild

    async def cog_before_invoke(self, context: Context) -> None:
        if context.interaction and not context.interaction.response.is_done():
            await context.interaction.response.defer()
        return None

    @commands.Cog.listener()
    async def on_member_join(self, member: Member) -> None:
        await member.add_roles(*[self.gamer.roles['0'], self.gamer.roles['Outsider'],
            self.gamer.roles['💎'], self.gamer.roles['🪨'], self.gamer.roles['🕹️']])
        embed = Embed(title='Outsider Identified',
            description=f"Name: {member.name}\nAlias: {member.mention}",
            color=self.roles['Outsider'].color)
        embed.set_image(url=member.display_avatar.url)
        await member.guild.system_channel.send(embed=embed)
        return None

    @commands.Cog.listener()
    async def on_member_remove(self, member: Member) -> None:
        self.gamer.stats.delete_player(member.id)
        return None

    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.author.bot:
            return None
        self.gamer.stats.increase_posts(message.author.id)
        return None

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent) -> None:
        if payload.guild_id != self.GUILD_ID:
            return None
        self.gamer.stats.increase_reacts(payload.member.id)
        return None

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent) -> None:
        if payload.guild_id != self.GUILD_ID:
            return None
        self.gamer.stats.decrease_reacts(self.guild.get_member(payload.user_id).id)
        return None

    @commands.hybrid_group()
    async def slave(self, context: Context) -> None:
        await self._hybrid_reply(context, f"Hi, {context.author.display_name}.")
        return None

    @slave.command()
    async def paint(self, context: Context, member: Member, role: Role) -> None:
        if ('Color' not in self.roles) or (role not in self.roles['Color']):
            resp = f"Color not found: {role.mention}."
        else:
            await self.gamer.color.remove_from(member)
            await member.add_roles(role)
            resp = f"{context.author.mention} colored {member.mention} {role.mention}."
        await self._hybrid_reply(context, resp)
        return None

    async def _from_master(self, context: Context) -> bool:
        author = context.author
        if (author.id == author.guild.owner_id) or (author.get_role(self.roles['🐈'])):
            self._hybrid_reply(f"Hi, Master {author.display_name}.")
            return True
        await self._hybrid_fail(context, f"You are not my master: {author.display_name}.")

    @commands.hybrid_group()
    @commands.check(_from_master)
    @app_commands.check(_from_master)
    async def master(self, context: Context) -> None:
        pass

    @master.command()
    async def initialize(self, context: Context) -> None:
        await self.gamer.initialize()
        await self._hybrid_reply(context, 'Done.')
        return None

    @master.command()
    async def clear(self, context: Context) -> None:
        n = 0
        for role in context.guild.roles:
            if (role.id != self.guild.default_role.id) and (role.id != self.guild.me.top_role.id):
                await role.delete()
                await sleep(2)
                n += 1
        for m, channel in enumerate(context.guild.channels):
            await channel.delete()
            await sleep(2)
        await self._hybrid_reply(context, f"Deleted {n} roles and {m} channels.")
        return None

    @staticmethod
    async def _hybrid_fail(context: Context, message: str) -> Union[Message, None]:
        if context.interaction:
            if context.interaction.response.is_done():
                await context.interaction.followup.send(message)
            await context.interaction.response.send_message(message)
            raise app_commands.CheckFailure()
        await context.send(message)
        raise commands.CheckFailure()

    @staticmethod
    async def _hybrid_reply(context: Context, content: str) -> Union[Message, None]:
        if context.interaction:
            if context.interaction.response.is_done():
                return await context.interaction.followup.send(content)
            return await context.interaction.response.send_message(content)
        return await context.send(content)


if __name__ == "__main__":
    bot = commands.Bot(command_prefix='!', intents=Intents.all())

    @bot.event
    async def on_ready():
        guild = bot.get_guild(Master.GUILD_ID)
        await bot.add_cog(Master(bot, guild))
        guild = Object(id=Master.GUILD_ID)
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)

    with open('database/files/token.txt') as token_file:
        token_raw = token_file.read()

    bot.run(token_raw)
