from __future__ import annotations
from random import choice
from typing import List, Type, TypedDict
from typing_extensions import NotRequired

from discord import ButtonStyle, Color, Embed, File, Interaction, Message, TextChannel
from discord.ext.commands import Bot
from discord.ui import button, Button, View

from petto.state import State
from petto.stats import Player
from petto import utils


class StageView(View):
    def __init__(self, stage: Stage):
        super().__init__(timeout=None)
        self.stage = stage
        self.toggled = False


class Chat(TypedDict):

    clean: NotRequired[List[str]]
    dirty: NotRequired[List[str]]
    hungry: NotRequired[List[str]]
    full: NotRequired[List[str]]
    powerful: NotRequired[List[str]]
    weak: NotRequired[List[str]]
    parched: NotRequired[List[str]]
    quenched: NotRequired[List[str]]
    healthy: NotRequired[List[str]]
    sick: NotRequired[List[str]]
    happy: NotRequired[List[str]]
    sad: NotRequired[List[str]]
    scared: NotRequired[List[str]]
    mad: NotRequired[List[str]]
    neutral: NotRequired[List[str]]


class Stage:

    chat: Chat
    alias: str
    avatar: str
    death_img: str
    info_img: str
 
    def __init__(self, state: State, player: Player):
        self.interface: StageView = self.Interface(self)
        self.player = player
        self.state = state

    def __init_subclass__(cls: Type['Stage']):
        super().__init_subclass__()
        if not hasattr(cls, 'Interface'):
            raise TypeError('Undefined nested class Interface.')

    def random_chat(self) -> str:
        return choice(self.chat[choice(list(self.chat.keys()))])

    async def reply(self, message: Message, text: str) -> None:
        await message.reply(text, view=self.interface)
        return None

    async def reply_random(self, message: Message) -> None:
        await self.reply(message, self.random_chat())
        return None

    async def send(self, channel: TextChannel, text: str) -> None:
        await channel.send(text, view=self.interface)
        return None

    async def send_random(self, bot: Bot, guild_id: int) -> None:
        await self.send_random(utils.get_random_channel_with_perm(bot, guild_id))
        return None

    async def send_random_text(self, channel: TextChannel) -> None:
        await self.send(channel, self.random_chat())
        return None


class Egg(Stage):

    chat = Chat(neutral=['Crack', 'Tap', 'Peep', 'Squeak', 'Chirp'])
    alias = 'Geppetto🐣Egg'
    avatar = 'Egg1'
    death_img = 'Egg2'
    info_img = 'Egg3'

    class Interface(StageView):

        @button(label='⚔️', style=ButtonStyle.danger)
        async def attack(self, interaction: Interaction, button: Button) -> None:
            await interaction.response.defer()
            await interaction.message.delete()
            await self.stage.send_random_text(interaction.channel)
            return None

        @button(label='🫳', style=ButtonStyle.blurple)
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
                embed = Embed(title=f"Level {self.stage.player.level} {self.stage.alias}",
                    description='An otherwordly Fabergé egg with scales made of jewels inlaid into gold, a large center gem that looks like an eye and a crown with horns.',
                    color=Color.from_str('#89CFF0'))
                embed.add_field(name='Age', value=self.stage.state.age)
                embed.add_field(name='Health', value=self.stage.state.health)
                embed.add_field(name='Hunger', value=self.stage.state.hunger)
                embed.add_field(name='Thirst', value=self.stage.state.thirst)
                embed.add_field(name='Power', value=self.stage.state.power)
                embed.add_field(name='Weight', value=self.stage.state.weight)
                embed.add_field(name='Hygiene', value=self.stage.state.hygiene)
                embed.add_field(name='Mood', value=self.stage.state.mood)
                embed.add_field(name='Posts', value=self.stage.player.posts)
                embed.add_field(name='Score', value=self.stage.player.score)
                embed.set_image(url=f"attachment://{self.stage.info_img}.png")
                file = File(f"petto/imgs/{self.stage.info_img}.png",
                    filename=f"{self.stage.info_img}.png")
                attach = {'attachments': [file], 'embeds': [embed]}
            await interaction.edit_original_response(**attach, view=self)
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
