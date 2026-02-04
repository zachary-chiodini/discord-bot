from datetime import time, timezone
from pathlib import Path
from random import random

from discord import (app_commands, Embed, File, Guild, Interaction, Member, Message,  MessageType,
    Permissions, RawBulkMessageDeleteEvent, RawMessageDeleteEvent, RawReactionActionEvent)
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
        self.stage: Stage = self.stages[self.state.stage](
            self.state, self.stats.get_player(self.bot.user.id))

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
        pass

    @at_midnight.before_loop
    @at_noon.before_loop
    async def before_loop(self) -> None:
        await self.bot.wait_until_ready()
        return None

    def cog_load(self) -> None:
        self.at_midnight.start()
        self.at_noon.start()
        return None

    def cog_unload(self) -> None:
        self.at_midnight.cancel()
        self.at_noon.cancel()
        return None

    @commands.Cog.listener()
    async def on_guild_join(self, guild: Guild) -> None:
        pass

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
        if message.type == MessageType.new_member:
            await self.stage.reply_random(message)
            return None
        elif ((self.bot.user in message.mentions)
                or (self.bot.get_guild(self.guild_id).me.top_role in message.role_mentions)
                or ((message.reference and isinstance(message.reference.resolved, Message)
                    and (message.reference.resolved.author == self.bot.user)))):
            await self.stage.reply_random(message)
        elif random() < 0.01:
            await self.stage.send_random_text(message.channel)
        self.stats.update_posts(message.author.id, 1)
        return None

    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, payload: RawBulkMessageDeleteEvent):
        for message in payload.cached_messages:
            if not message.author.bot:
                self.stats.update_posts(message.author.id, -1)
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

    master = app_commands.Group(name='master', description='Administrator commands',
        default_permissions=Permissions(administrator=True))

    @master.command()
    async def initialize(self, interaction: Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        for member in interaction.guild.members:
            self.stats.create_player(member.id)
        await interaction.guild.me.edit(nick=Egg.alias)
        await self.bot.user.edit(avatar=Path(f"petto/imgs/{Egg.avatar}.png").read_bytes())
        await self.stage.send_random_text(interaction.guild.system_channel)
        await interaction.followup.send('Initialized.', ephemeral=True)
        return None
