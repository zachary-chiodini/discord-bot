from __future__ import annotations
from random import choice
from typing import List, Type

from discord import ButtonStyle, Embed, File, Interaction, Message, TextChannel
from discord.ext.commands import Bot
from discord.ui import button, Button, View

from state import State
import utils


class StageView(View):
    def __init__(self, stage: Stage):
        super().__init__(timeout=None)
        self.stage = stage
        self.toggled = False


class Chat:

    clean: List[str]
    dirty: List[str]
    hungry: List[str]
    full: List[str]
    powerful: List[str]
    weak: List[str]
    parched: List[str]
    quenched: List[str]
    healthy: List[str]
    sick: List[str]
    happy: List[str]
    sad: List[str]
    scared: List[str]
    mad: List[str]
    neutral: List[str]

    def refresh(self) -> str:
        pass

    def random(self) -> str:
        fields = vars(self)
        return choice(fields[choice(list(fields.keys()))])


class Stage:

    chat: Chat
    avatar_img: str
    death_img: str
    info_img: str
 
    def __init__(self, state: State):
        self.interface: StageView = self.Interface(self)
        self.state = state

    def __init_subclass__(cls: Type['Stage']):
        super().__init_subclass__()
        if not hasattr(cls, 'Interface'):
            raise TypeError('Undefined nested class Interface.')

    async def reply(self, message: Message, text: str) -> None:
        await message.reply(text, view=self.interface)
        return None

    async def reply_random(self, message: Message) -> None:
        await self.reply(message, self.chat.random())
        return None

    async def send(self, channel: TextChannel, text: str) -> None:
        await channel.send(text, view=self.interface)
        return None

    async def send_random(self, bot: Bot, guild_id: int) -> None:
        await self.send_random(utils.get_random_channel_with_perm(bot, guild_id))
        return None

    async def send_random_text(self, channel: TextChannel) -> None:
        await self.send(channel, self.chat.random())
        return None


class Egg(Stage):

    chat = Chat(neutral=['Crack', 'Tap', 'Peep', 'Squeak', 'Chirp'])

    class Interface(StageView):

        @button(label='⚔️', style=ButtonStyle.danger)
        async def attack(self, interaction: Interaction, button: Button) -> None:
            await interaction.response.defer()
            await interaction.message.delete()
            await self.stage.send_random_text(interaction.channel)
            return None

        @button(label='🫳', style=ButtonStyle.grey)
        async def pet(self, interaction: Interaction, button: Button) -> None:
            await interaction.response.defer()
            await interaction.message.delete()
            await self.stage.send_random_text(interaction.channel)
            return None

        @button(label='🔍', style=ButtonStyle.grey)
        async def info(self, interaction: Interaction, button: Button) -> None:
            await interaction.response.defer()
            if self.toggled:
                attach = {'attachments': [], 'embeds': []}
                button.label = '🔍'
                self.toggled = False
            else:
                button.label = '🔺'
                self.toggled = True
                embed = Embed()
            return None


class Baby(Stage):

    ['Waah!', 'Boohoo!', 'Sniffle', 'Barf!', 'Bleah!', 'Hiccup!', 'Argh!', 'Mommy!', 'Help!', 'Meow']

    class Interface(StageView):

        @button(label='🍼', style=ButtonStyle.primary)
        async def feed(self, interaction: Interaction, button: Button) -> None:
            await interaction.response.defer()
            return None

        @button(label='🫳', style=ButtonStyle.grey)
        async def pet(self, interaction: Interaction, button: Button) -> None:
            await interaction.response.defer()
            return None

        @button(label='🪶', style=ButtonStyle.primary)
        async def tickle(self, interaction: Interaction, button: Button) -> None:
            await interaction.response.defer()
            return None

        @button(label='💞', style=ButtonStyle.primary)
        async def console(self, interaction: Interaction, button: Button) -> None:
            await interaction.response.defer()
            return None

        @button(label='🔍', style=ButtonStyle.grey)
        async def info(self, interaction: Interaction, button: Button) -> None:
            await interaction.response.defer()
            return None


class Kid:

    @button(label='🥪', style=ButtonStyle.primary)
    async def feed(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.defer()
        return None

    @button(label='🧃', style=ButtonStyle.primary)
    async def water(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.defer()
        return None

    @button(label='🫳', style=ButtonStyle.grey)
    async def pet(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.defer()
        return None

    @button(label='🎮', style=ButtonStyle.primary)
    async def game(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.defer()
        return None

    @button(label='🔍', style=ButtonStyle.grey)
    async def info(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.defer()
        return None


class Adult:

    @button(label='🍔', style=ButtonStyle.primary)
    async def feed(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.defer()
        return None

    @button(label='🥤', style=ButtonStyle.primary)
    async def water(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.defer()
        return None

    @button(label='🫳', style=ButtonStyle.grey)
    async def pet(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.defer()
        return None

    @button(label='🍻', style=ButtonStyle.primary)
    async def party(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.defer()
        return None

    @button(label='🔍', style=ButtonStyle.grey)
    async def info(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.defer()
        return None


class Senior:

    @button(label='🍴', style=ButtonStyle.primary)
    async def feed(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.defer()
        return None

    @button(label='🥃', style=ButtonStyle.primary)
    async def water(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.defer()
        return None

    @button(label='🫳', style=ButtonStyle.grey)
    async def pet(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.defer()
        return None

    @button(label='💊', style=ButtonStyle.primary)
    async def medicate(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.defer()
        return None

    @button(label='🔍', style=ButtonStyle.grey)
    async def info(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.defer()
        return None


class Dead:

    @button(label='🫳', style=ButtonStyle.grey)
    async def pet(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.defer()
        return None

    @button(label='🔍', style=ButtonStyle.grey)
    async def info(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.defer()
        return None


class Ghost:

    @button(label='🕯️', style=ButtonStyle.primary)
    async def offering(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.defer()
        return None

    @button(label='🩸', style=ButtonStyle.red)
    async def sacrifice(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.defer()
        return None

    @button(label='🫳', style=ButtonStyle.grey)
    async def pet(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.defer()
        return None

    @button(label='🙏🏻', style=ButtonStyle.primary)
    async def pray(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.defer()
        return None

    @button(label='🔍', style=ButtonStyle.grey)
    async def info(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.defer()
        return None


class Ascended:

    @button(label='🔍', style=ButtonStyle.grey)
    async def info(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.defer()
        return None


class Damned:

    @button(label='🔍', style=ButtonStyle.grey)
    async def info(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.defer()
        return None
