from asyncio import sleep
from random import choice, random
from typing import Callable, Dict, List, Tuple, TypedDict, Union
from typing_extensions import NotRequired

from discord import ButtonStyle, Color, Embed, File, Guild, Interaction, Message, TextChannel, Webhook
from discord.errors import NotFound
from discord.ui import button, Button, Item, View
from emoji import replace_emoji

from petto.sts.state import State
from petto.sts.stats import Stats


DynamicItem = Union[Callable, Tuple[str, Item]]


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


class BaseView(View):

    def __init__(self, stage: BaseStage):
        super().__init__(timeout=None)
        self.stage = stage
        for item in self.stage.items.values():
            self.add_item(item)


class BaseStage:

    alias: str
    avatar_img: str
    chat: Chat
    color: str
    description: str
    death_img: str
    info_img: str

    def __init__(self):
        self.items: Dict[str, Item] = {}
        self.last_chat: Union[Message, None] = None
        self.last_reply: Union[Message, None] = None
        self.toggle = False
        button = Button(label='🔍', style=ButtonStyle.grey)
        button.callback = lambda interaction: self.info_callback(interaction, button)
        self.add_item((self.info_callback.__name__, button))

    def add_item(self, *dynamic_items: DynamicItem) -> None:
        for item in dynamic_items:
            if isinstance(item, Callable):
                self.items[item.__name__] = item()
            elif isinstance(item, Tuple):
                self.items[item[0]] = item[1]
        return None

    async def info_callback(self, interaction: Interaction, button: Button) -> None:
        NotImplementedError(f"{self.__class__} must implement info_callback[[self, Interaction, Button], None] method.")

    @staticmethod
    async def pause(n: int) -> None:
        await sleep(n * random())
        return None

    def random_chat(self) -> str:
        return self.random_emote(choice(list(self.chat.keys())))

    def random_emote(self, key: str) -> str:
        return choice(self.chat[key])

    def remove_item(self, *callable_item: Callable) -> None:
        for callable in callable_item:
            del self.items[callable.__name__]
        return None

    class Interface(BaseView):
        pass


class Stage(BaseStage):

    def __init__(self, state: State, stats: Stats):
        super().__init__()
        self.player = stats.get_player(state.id)
        self.state = state
        self.stats = stats

    async def del_last_chat(self) -> None:
        if self.last_chat:
            try:
                await self.last_chat.delete()
            except NotFound:
                pass
        return None

    async def info_callback(self, interaction: Interaction, button: Button) -> None:
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
            embed = Embed(title=f"Level {self.player.level} {replace_emoji(self.alias, ' ')}",
                description=self.description, color=Color.from_str(self.color))
            embed.add_field(name='Age', value=self.state.age)
            embed.add_field(name='Health', value=display_value(self.player.health, '❤️', '🖤'))
            embed.add_field(name='Hunger', value=display_value(self.state.hunger, '🍖', '🦴'))
            embed.add_field(name='Thirst', value=display_value(self.state.thirst, '💧', '🌵'))
            embed.add_field(name='Power', value=display_value(self.state.power, '⚡', '🥀'))
            embed.add_field(name='Hygiene', value=display_value(self.state.hygiene, '🧼', '🦠'))
            embed.add_field(name='Weight', value=f"{self.state.weight} kg")
            embed.add_field(name='Mood', value=self.player.mood)
            embed.add_field(name='Posts', value=self.player.posts)
            embed.add_field(name='Score', value=self.player.score)
            embed.set_image(url=f"attachment://{self.info_img}")
            file = File(f"petto/stg/img/{self.info_img}",
                filename=f"{self.info_img}")
            attach = {'attachments': [file], 'embeds': [embed]}
        try:
            await interaction.edit_original_response(**attach, view=self.Interface(self))
        except NotFound:
            pass
        return None

    async def reply(self, message: Message, text: str) -> Message:
        await self.del_last_chat()
        if self.last_reply:
            try:
                await self.last_reply.delete()
            except NotFound:
                pass
        self.last_chat = await message.reply(text, view=self.Interface(self))
        self.last_reply = message
        return self.last_chat

    async def reply_random(self, message: Message) -> Message:
        message = await self.reply(message, self.random_chat())
        return message

    async def send(self, channel: TextChannel, text: str) -> Message:
        await self.del_last_chat()
        self.last_chat = await channel.send(text, view=self.Interface(self))
        return self.last_chat

    async def send_random_chat(self, channel: TextChannel) -> Message:
        message = await self.send(channel, self.random_chat())
        return message

    async def send_random_emote(self, channel: TextChannel, key: str) -> Message:
        message = await self.send(channel, self.random_emote(key))
        return message

    async def send_random(self, guild: Guild) -> Message:
        member = guild.get_member(self.state.id)
        channels = set()
        for channel in guild.channels:
            perms = channel.permissions_for(member)
            if perms.view_channel and perms.send_messages:
                channels.add(channel)
        if channels:
            message = self.send_random_chat(choice(list(channels)))
        else:
            message = self.send_random_chat(guild.system_channel)
        return message

    async def update(self, interaction: Interaction) -> None:
        if interaction.response.is_done():
            await interaction.followup.edit_message(
                interaction.message.id, view=self.Interface(self))
            return None
        await interaction.response.edit_message(view=self.Interface(self))
        return None


class WebhookStage(BaseStage):

    def __init__(self, stats: Stats, webhook: Webhook):
        super().__init__()
        self.player = stats.get_player(webhook.id)
        self.stats = stats
        self.webhook = webhook

    async def info_callback(self, interaction: Interaction, button: Button) -> None:
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
            embed = Embed(title=f"Level {self.player.level} {replace_emoji(self.alias, '')}",
                description=self.description, color=Color.from_str(self.color))
            embed.add_field(name='Health', value=display_value(self.player.health, '❤️', '🖤'))
            embed.add_field(name='Mood', value=self.player.mood)
            embed.add_field(name='Posts', value=self.player.posts)
            embed.add_field(name='Score', value=self.player.score)
            embed.set_image(url=f"attachment://{self.info_img}")
            file = File(f"petto/stg/img/{self.info_img}",
                filename=f"{self.info_img}")
            attach = {'attachments': [file], 'embeds': [embed]}
        await interaction.edit_original_response(**attach, view=self.Interface(self))
        return None

    async def send(self, text: str) -> Message:
        if self.last_chat:
            try:
                await self.last_chat.delete()
            except NotFound:
                pass
        self.last_chat = await self.webhook.send(text, view=self.Interface(self), wait=True)
        return self.last_chat

    async def send_random_chat(self) -> Message:
        message = await self.send(self.random_chat())
        return message

    async def send_random_emote(self, key: str) -> Message:
        message = await self.send(self.random_emote(key))
        return message
