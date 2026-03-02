from asyncio import sleep
from random import choice, random
from typing import List, Type, TypedDict, Union
from typing_extensions import NotRequired

from discord import (ButtonStyle, Color, Embed, File, Interaction, Message, NotFound, TextChannel, Webhook)
from discord.ui import button, Button, View
from emoji import replace_emoji

from petto.state import State
from petto.stats import Stats


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
    angry: NotRequired[List[str]]
    neutral: NotRequired[List[str]]


class Base:

    alias: str
    avatar_img: str
    chat: Chat
    death_img: str
    info_img: str

    def __init__(self):
        self.interface = self.Interface
        self.last_chat: Union[Message, None] = None

    @staticmethod
    async def pause(n: int) -> None:
        await sleep(n * random())
        return None

    def random_chat(self) -> str:
        return self.random_emote(choice(list(self.chat.keys())))

    def random_emote(self, key: str) -> str:
        return choice(self.chat[key])


class Specter(Base):

    alias = '😈Specter'
    avatar_img = 'specter_avatar.png'
    chat = Chat(
        angry=['You fool!', "I'll turn you into an egg!", 'Fuck you!', 'The darkness has taken you!', 'Stop this!'],
        neutral=['Abracadabra!', 'Boo!', 'Sim Sala Bim!', 'Poof!', 'Alakazam!', 'Ta-da!'])
    death_img: str
    info_img = 'specter_avatar.png'

    def __init__(self, stats: Stats, webhook: Webhook):
        super().__init__()
        self.player = stats.get_player(webhook.id)
        self.stats = stats
        self.webhook = webhook

    async def send(self, text: str) -> Message:
        if self.last_chat:
            try:
                await self.last_chat.delete()
            except NotFound:
                pass
        self.last_chat = await self.webhook.send(text, view=self.interface(self))
        return self.last_chat

    async def send_random_chat(self) -> Message:
        message = await self.send(self.random_chat())
        return message

    async def send_random_emote(self, key: str) -> Message:
        message = await self.send(self.random_emote(key))
        return message

    class Interface(View):

        def __init__(self, specter: Specter):
            super().__init__(timeout=None)
            self.specter = specter
            self.toggle = False

        @button(label='🔍', style=ButtonStyle.grey)
        async def info(self, interaction: Interaction, button: Button) -> None:
            def display_value(stat: int, full_bar: str, empty_bar: str) -> str:
                return (stat * full_bar) + ((5 - stat) * empty_bar)
            await interaction.response.defer()
            if self.toggle:
                attach = {'attachments': [], 'embeds': []}
                button.label = '🔍'
                self.toggle = False
            else:
                button.label = '🔺'
                self.toggle = True
                embed = Embed(title=f"Level {self.specter.player.level} {replace_emoji(self.specter.alias, '')}",
                    description='A disembodied voice that appears out of thin air from all directions without an apparent source.',
                    color=Color.from_str('#89CFF0'))
                embed.add_field(name='Health', value=display_value(self.specter.player.health, '❤️', '🖤'))
                embed.add_field(name='Mood', value=self.specter.player.mood)
                embed.add_field(name='Posts', value=self.specter.player.posts)
                embed.add_field(name='Score', value=self.specter.player.score)
                embed.set_image(url=f"attachment://{self.specter.info_img}")
                file = File(f"petto/stg/img/{self.specter.info_img}",
                    filename=f"{self.specter.info_img}")
                attach = {'attachments': [file], 'embeds': [embed]}
            await interaction.edit_original_response(**attach, view=self)
            return None

        @button(label='⚔️', style=ButtonStyle.danger)
        async def attack(self, interaction: Interaction, button: Button) -> None:
            await interaction.message.delete()
            self.specter.stats.update_health(self.specter.webhook.id, -1)
            await self.specter.pause(5)
            message = await self.specter.send_random_emote('angry')
            await self.specter.pause(5)
            await message.delete()
            return None

        @button(label='🫳', style=ButtonStyle.blurple)
        async def peekaboo(self, interaction: Interaction, button: Button) -> None:
            await interaction.message.delete()
            return None


class Stage(Base):

    specter_class = Specter

    def __init__(self, state: State, stats: Stats):
        super().__init__()
        self.player = stats.get_player(state.id)
        self.state = state
        self.stats = stats
        self._specter = None

    def __init_subclass__(cls: Type['Stage']):
        super().__init_subclass__()
        if not hasattr(cls, 'Interface'):
            raise TypeError('Undefined nested class Interface.')

    async def get_specter(self, interaction: Interaction) -> Specter:
        if self._specter:
            return self._specter
        webhooks = await interaction.guild.webhooks()
        for webhook in webhooks:
            if webhook.name == Specter.alias:
                self._specter = Specter(self.stats, webhook)
                return self._specter
        raise Exception('Webhook not found.')

    async def reply(self, message: Message, text: str) -> Message:
        message = await message.reply(text, view=self.interface(self))
        return message

    async def reply_random(self, message: Message) -> Message:
        message = await self.reply(message, self.random_chat())
        return message

    async def send(self, channel: TextChannel, text: str) -> Message:
        if self.last_chat:
            try:
                await self.last_chat.delete()
            except NotFound:
                pass
        self.last_chat = await channel.send(text, view=self.interface(self))
        return self.last_chat

    async def send_random_chat(self, channel: TextChannel) -> Message:
        message = await self.send(channel, self.random_chat())
        return message

    async def send_random_emote(self, channel: TextChannel, key: str) -> Message:
        message = await self.send(channel, self.random_emote(key))
        return message

    async def send_random(self, interaction: Interaction) -> Message:
        member = interaction.guild.get_member(self.state.id)
        channels = set()
        for channel in interaction.guild.channels:
            perms = channel.permissions_for(member)
            if perms.view_channel and perms.send_messages:
                channels.add(channel)
        if channels:
            message = self.send_random_chat(choice(list(channels)))
        else:
            message = self.send_random_chat(interaction.guild.system_channel)
        return message

    async def specter_send(self, interaction: Interaction, text: str) -> Message:
        specter = await self.get_specter(interaction)
        message = await specter.send(text)
        return message


class StageView(View):

    def __init__(self, stage: Stage):
        super().__init__(timeout=None)
        self.stage = stage
        self.toggle = False

    @button(label='🔍', style=ButtonStyle.grey)
    async def info(self, interaction: Interaction, button: Button) -> None:
        def display_value(stat: int, full_bar: str, empty_bar: str) -> str:
            return (stat * full_bar) + ((5 - stat) * empty_bar)
        await interaction.response.defer()
        if self.toggle:
            button.label = '🔍'
            self.toggle = False
            attach = {'attachments': [], 'embeds': []}
        else:
            button.label = '🔺'
            self.toggle = True
            embed = Embed(title=f"Level {self.stage.player.level} {replace_emoji(self.stage.alias, ' ')}",
                description='An otherwordly Fabergé egg with a monstrous face, scales made of jewels inlaid into gold, a large center gem that looks like an eye and a crown with horns.',
                color=Color.from_str('#FFD700'))
            embed.add_field(name='Age', value=self.stage.state.age)
            embed.add_field(name='Health', value=display_value(self.stage.player.health, '❤️', '🖤'))
            embed.add_field(name='Hunger', value=display_value(self.stage.state.hunger, '🍖', '🦴'))
            embed.add_field(name='Thirst', value=display_value(self.stage.state.thirst, '💧', '🌵'))
            embed.add_field(name='Power', value=display_value(self.stage.state.power, '⚡', '🥀'))
            embed.add_field(name='Hygiene', value=display_value(self.stage.state.hygiene, '🧼', '🦠'))
            embed.add_field(name='Weight', value=f"{self.stage.state.weight} kg")
            embed.add_field(name='Mood', value=self.stage.player.mood)
            embed.add_field(name='Posts', value=self.stage.player.posts)
            embed.add_field(name='Score', value=self.stage.player.score)
            embed.set_image(url=f"attachment://{self.stage.info_img}")
            file = File(f"petto/stg/img/{self.stage.info_img}",
                filename=f"{self.stage.info_img}")
            attach = {'attachments': [file], 'embeds': [embed]}
        await interaction.edit_original_response(**attach, view=self)
        return None
