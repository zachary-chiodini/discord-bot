from asyncio import sleep
from typing import Union

from discord import Embed, Guild, Intents, Member, Message, Object, RawReactionActionEvent
from discord.ext import commands
from discord.ext.commands import Context

from create import Create
from game import Game


class MyCog(commands.Cog):

    GUILD_ID = 1455730008273195032

    def __init__(self, bot: commands.Bot, guild: Guild):
        self.bot = bot
        self.create = Create(guild)
        self.game = Game()
        self.guild = guild
        self.roles = self.create.roles

    @staticmethod
    async def hybrid_reply(context: Context, content: str, ephemeral: bool
            ) -> Union[Message, None]:
        if context.interaction:
            if context.interaction.response.is_done():
                return await context.interaction.followup.send(content, ephemeral=ephemeral)
            return await context.interaction.response.send_message(content, ephemeral=ephemeral)
        return await context.send(content)

    @commands.Cog.listener()
    async def on_member_join(self, member: Member) -> None:
        await member.add_roles(*[self.roles['0'], self.roles['Outsider'], self.roles['💎'],
            self.roles['🪨'], self.roles['🕹️']])
        embed = Embed(title='Outsider Identified',
            description=f"Name: {member.name}\nAlias: {member.mention}",
            color=self.roles['Outsider'].color)
        embed.set_image(url=member.display_avatar.url)
        await member.guild.system_channel.send(embed=embed)
        return None

    @commands.Cog.listener()
    async def on_member_remove(self, member: Member) -> None:
        self.game.delete_player(member.id)
        return None

    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.author.bot:
            return None
        self.game.increase_posts(message.author.id)
        return None

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent) -> None:
        if payload.guild_id != self.GUILD_ID:
            return None
        self.game.increase_reacts(payload.member.id)
        return None

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent) -> None:
        if payload.guild_id != self.GUILD_ID:
            return None
        self.game.decrease_reacts(self.guild.get_member(payload.user_id).id)
        return None

    @commands.hybrid_group(invoke_without_command=True)
    async def slave(self, context: Context) -> None:
        await self.hybrid_reply(context, f"Hi, {context.author.display_name}.", False)
        return None

    @slave.command()
    async def initialize(self, context: Context) -> None:
        await self.create.initialize()
        return None

    @slave.command()
    async def clear(self, context: Context) -> None:
        if context.interaction:
            await context.interaction.response.defer(ephemeral=False)
        for role in context.guild.roles:
            if (role.id != self.guild.default_role.id) and (role.id != self.guild.me.top_role.id):
                await role.delete()
                await sleep(2)
        await self.hybrid_reply(context, "Cleared.", False)
        return None


if __name__ == "__main__":
    bot = commands.Bot(command_prefix='!', intents=Intents.all())

    @bot.event
    async def on_ready():
        guild = bot.get_guild(MyCog.GUILD_ID)
        await bot.add_cog(MyCog(bot, guild))
        guild = Object(id=MyCog.GUILD_ID)
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)

    with open('database/files/token.txt') as token_file:
        token_raw = token_file.read()

    bot.run(token_raw)
