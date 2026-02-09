from __future__ import annotations
from asyncio import Lock, sleep
from random import choice, randint, random
from typing import Callable, List, Optional, Type, TypedDict, Union
from typing_extensions import NotRequired

from discord import ButtonStyle, Color, Embed, File, Interaction, Message, NotFound, TextChannel, Webhook
from discord.ext.commands import Bot
from discord.ui import button, Button, View
from emoji import replace_emoji

from petto.state import State
from petto.stats import Stats, Player
from petto import utils


class SpecterView(View):

    def __init__(self, player: Player, button: Optional[Button] = None):
        super().__init__(timeout=None)
        self.player = player
        if button:
            self.add_item(button)

    @button(label='🔍', style=ButtonStyle.grey)
    async def info(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.defer()
        return None

    @button(label='⚔️', style=ButtonStyle.danger)
    async def attack(self, interaction: Interaction, button: Button) -> None:
        await interaction.message.delete()
        return None

    @button(label='🫳', style=ButtonStyle.blurple)
    async def peekaboo(self, interaction: Interaction, button: Button) -> None:
        await interaction.message.delete()
        return None


class StageView(View):

    def __init__(self, stage: Stage):
        super().__init__(timeout=None)
        self.lookback = None
        self.points = 0
        self.queue = 0
        self.front = []
        self.stage = stage
        self.toggle1 = False
        self.toggle2 = False
        self.lock = Lock()

    @button(label='🔍', style=ButtonStyle.grey)
    async def info(self, interaction: Interaction, button: Button) -> None:
        def display_field(field: str, stat: int) -> str:
            if stat == 0:
                return f"{field} (empty)"
            elif stat == 5:
                return f"{field} (full)"
            return field
        def display_value(stat: int, full_bar: str, empty_bar: str) -> str:
            return (stat * full_bar) + ((5 - stat) * empty_bar)
        await interaction.response.defer()
        if self.toggle1:
            attach = {'attachments': [], 'embeds': []}
            button.label = '🔍'
            self.toggle1 = False
        else:
            button.label = '🔺'
            self.toggle1 = True
            embed = Embed(title=f"Level {self.stage.player.level} {replace_emoji(self.stage.alias, ' ')}",
                description='An otherwordly Fabergé egg with scales made of jewels inlaid into gold, a large center gem that looks like an eye and a crown with horns.',
                color=Color.from_str('#89CFF0'))
            embed.add_field(name='Age', value=self.stage.state.age)
            embed.add_field(name=display_field('Health', self.stage.player.health),
                value=display_value(self.stage.player.health, '❤️', '🖤'))
            embed.add_field(name=display_field('Hunger', self.stage.state.hunger),
                value=display_value(self.stage.state.hunger, '🍖', '🦴'))
            embed.add_field(name=display_field('Thirst', self.stage.state.thirst),
                value=display_value(self.stage.state.thirst, '💧', '🌵'))
            embed.add_field(name=display_field('Power', self.stage.state.power),
                value=display_value(self.stage.state.power, '⚡', '🥀'))
            embed.add_field(name=display_field('Hygiene', self.stage.state.hygiene),
                value=display_value(self.stage.state.hygiene, '🧼', '🦠'))
            embed.add_field(name='Weight', value=f"{self.stage.state.weight} kg")
            embed.add_field(name='Mood', value=self.stage.player.mood)
            embed.add_field(name='Posts', value=self.stage.player.posts)
            embed.add_field(name='Score', value=self.stage.player.score)
            embed.set_image(url=f"attachment://{self.stage.info_img}.png")
            file = File(f"petto/imgs/{self.stage.info_img}.png",
                filename=f"{self.stage.info_img}.png")
            attach = {'attachments': [file], 'embeds': [embed]}
        await interaction.edit_original_response(**attach, view=self)
        return None

    @button(label='⚔️', style=ButtonStyle.danger)
    async def attack(self, interaction: Interaction, button: Button) -> None:
        await interaction.message.delete()
        if self.stage.player.health:
            self.stage.player.health -= 1
        await self.stage.specter_send(
            interaction, f"Do not attack {interaction.guild.me.mention}!")
        return None

    @button(label='🫳', style=ButtonStyle.blurple)
    async def peekaboo(self, interaction: Interaction, button: Button) -> None:
        async def callback(interaction: Interaction) -> None:
            await interaction.response.defer()
            return None
        async def pause(n: int) -> None:
            await sleep(n * random())
            return None
        points = 0
        i, prob = 0, [0.5, 0.1, 0.1]
        self.queue += 1
        message = interaction.message
        if random() < 0.95:
            while self.queue:
                try:
                    await message.delete()
                except NotFound:
                    if self.queue > points:
                        points = self.queue
                    else:
                        points += 1
                    break
                if self.queue > 0:
                    await pause(5)
                    message = await self.stage.send_random_text(interaction.channel)
                    await pause(5)
                    if random() > prob[i % len(prob)]:
                        self.queue -= 1
                    i += 1
                if self.queue > 5:
                    self.queue = 5
        else:
            try:
                button.disabled = True
                await interaction.response.edit_message(view=self)
                await pause(5)
                button.disabled = False
                await interaction.followup.edit_message(message.id, view=self)
                if self.queue > 0:
                    self.queue -= 1
            except NotFound:
                if self.queue > points:
                    points = self.queue
                else:
                    points += 1
        if points > 3:
            pass  # You win a Geppetto Point
        return None


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
    specter = '😈Specter'
 
    def __init__(self, state: State, player: Player, stats: Stats):
        self.interface: StageView = self.Interface(self)
        self.player = player
        self.stats = stats
        self.state = state

    def __init_subclass__(cls: Type['Stage']):
        super().__init_subclass__()
        if not hasattr(cls, 'Interface'):
            raise TypeError('Undefined nested class Interface.')

    async def get_specter(self, interaction: Interaction) -> Webhook:
        webhooks = await interaction.guild.webhooks()
        for webhook in webhooks:
            if webhook.name == self.specter:
                return webhook
        raise Exception('Webhook not found.')

    def random_chat(self) -> str:
        return choice(self.chat[choice(list(self.chat.keys()))])

    async def reply(self, message: Message, text: str) -> Message:
        message = await message.reply(text, view=self.interface)
        return message

    async def reply_random(self, message: Message) -> Message:
        message = await self.reply(message, self.random_chat())
        return message

    async def send(self, channel: TextChannel, text: str) -> Message:
        async for message in channel.history(limit=1):
            if (not message.webhook_id) and message.author.bot:
                try:
                    await message.delete()
                except NotFound:
                    pass
        message = await channel.send(text, view=self.interface)
        return message

    async def send_random(self, bot: Bot, guild_id: int) -> Message:
        message = await self.send_random_text(
            utils.get_random_channel_with_perm(bot, guild_id))
        return message

    async def send_random_text(self, channel: TextChannel) -> Message:
        message = await self.send(channel, self.random_chat())
        return message

    async def specter_send(self, interaction: Interaction, text: str, button: Optional[Button] = None) -> Message:
        webhook = await self.get_specter(interaction)
        async for message in webhook.channel.history(limit=1):
            if message.webhook_id == webhook.id:
                try:
                    await message.delete()
                except NotFound:
                    pass
        message = await webhook.send(
            text, view=SpecterView(self.stats.get_player(webhook.id), button))
        return message


class Egg(Stage):

    chat = Chat(neutral=['Crack', 'Tap', 'Peep', 'Squeak', 'Chirp'])
    alias = 'Geppetto🐣Egg'
    avatar = 'egg_avatar'
    death_img = 'Egg2'
    info_img = 'Egg3'

    class Interface(StageView):

        @button(label='🫗', style=ButtonStyle.blurple)
        async def water(self, interaction: Interaction, button: Button) -> None:
            async def callback(interaction: Interaction, button: Button) -> None:
                await interaction.response.defer()
                player = self.stage.stats.get_player(interaction.user.id)
                if '🪙' in player.items:
                    pass
                else:
                    content = interaction.message.content
                    specter = await self.stage.get_specter(interaction)
                    button.disabled = True
                    await interaction.followup.edit_message(interaction.message.id,
                        content='Find me a Geppetto Point!',
                        view=SpecterView(self.stage.stats.get_player(specter.id), button))
                    await sleep(5)
                    await interaction.message.delete()
                return None
            await interaction.response.defer()
            if self.toggle2:
                button.label = '🫗'
                self.toggle2 = False
            else:
                player = self.stage.stats.get_player(interaction.user.id)
                if '💧' in player.items:
                    button.label = '🧼'
                    self.toggle2= True
                else:
                    button = Button(label='🪙➡️💧', style=ButtonStyle.danger)
                    button.callback = lambda x: callback(x, button)
                    await self.stage.specter_send(
                        interaction, f"You need water to clean {interaction.guild.me.mention}!", button)
            await interaction.edit_original_response(view=self)
            return None


class Baby(Stage):

    ['Waah!', 'Boohoo!', 'Sniffle', 'Barf!', 'Bleah!', 'Hiccup!', 'Argh!', 'Mommy!', 'Help!', 'Meow']

    class Interface(StageView):

        @button(label='🍼', style=ButtonStyle.primary)
        async def feed(self, interaction: Interaction, button: Button) -> None:
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


class Kid:

    @button(label='🥪', style=ButtonStyle.primary)
    async def feed(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.defer()
        return None

    @button(label='🧃', style=ButtonStyle.primary)
    async def water(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.defer()
        return None

    @button(label='🎮', style=ButtonStyle.primary)
    async def game(self, interaction: Interaction, button: Button) -> None:
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

    @button(label='🍻', style=ButtonStyle.primary)
    async def party(self, interaction: Interaction, button: Button) -> None:
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

    @button(label='💊', style=ButtonStyle.primary)
    async def medicate(self, interaction: Interaction, button: Button) -> None:
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

    @button(label='🙏🏻', style=ButtonStyle.primary)
    async def pray(self, interaction: Interaction, button: Button) -> None:
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
