from datetime import time, timezone
from random import choice, random

from discord import (Embed, File, Guild, Interaction, Member, Message,  MessageType,
    RawBulkMessageDeleteEvent, RawMessageDeleteEvent, RawReactionActionEvent)
from discord.ext import commands, tasks

from petto.stage import *
from petto.state import State
from petto.stats import Stats


class Petto(commands.Cog):

    stages = [Egg, Baby, Kid, Adult, Senior, Dead, Ghost, Ascended, Damned]

    def __init__(self, bot: commands.Bot, guild_id: int):
        self.bot = bot
        self.guild_id = guild_id
        self.items = []
        self.state = State()
        self.stats = Stats()
        self.stage: Stage = self.stages[self.state.stage](self.state)

    @tasks.loop(time=time(hour=0, minute=0, tzinfo=timezone.utc))
    async def at_midnight(self) -> None:
        self.state.age += 1
        await self.stage.send_random(self.bot, self.guild_id)
        return None

    @tasks.loop(time=time(hour=12, minute=0, tzinfo=timezone.utc))
    async def at_noon(self) -> None:
        await self.stage.send_random(self.bot, self.guild_id)
        return None

    @tasks.loop(hours=1)
    async def every_hour(self) -> None:
        return None

    @at_midnight.before_loop
    async def before_loop(self) -> None:
        await self.bot.wait_until_ready()
        return None

    async def cog_load(self) -> None:
        self.at_midnight()
        return None

    def cog_unload(self) -> None:
        self.at_midnight.cancel()
        return None

    @commands.Cog.listener()
    async def on_guild_join(self, guild: Guild) -> None:
        for member in guild.members:
            self.stats.create_player(member.id)
        await self.stage.send_random_text(guild.system_channel)
        return None

    @commands.Cog.listener()
    async def on_member_join(self, member: Member) -> None:
        self.stats.create_player(member.id)
        return None

    @commands.Cog.listener()
    async def on_member_remove(self, member: Member) -> None:
        self.stats.delete(member.id)
        return None

    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        if ((message.type == MessageType.new_member) or (self.bot.user in message.mentions)
                or ((message.reference and isinstance(message.reference.resolved, Message)
                    and (message.reference.resolved.author == self.bot.user)))):
            await self.stage.reply_random(message)
        elif random() < 0.01:
            await self.stage.send_random_text(message.channel)
        return None

    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, payload: RawBulkMessageDeleteEvent):
        for message in payload.cached_messages:
            if not message.author.bot:
                self.stats.update_posts(message.author.id, 1)
        return None

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload: RawMessageDeleteEvent) -> None:
        if payload.cached_message and (not payload.cached_message.author.bot):
            self.stats.update_posts(payload.cached_message.author.id, -1)
        return None

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent) -> None:
        self.stats.update_reacts(payload.member.id, 1)
        return None

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent) -> None:
        self.stats.update_reacts(payload.member.id, -1)
        return None
