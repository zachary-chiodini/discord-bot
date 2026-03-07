from discord import ButtonStyle, Color, Embed, File, Interaction, Message, Webhook
from discord.errors import NotFound
from discord.ui import button, Button

from emoji import replace_emoji
from petto.stg.base import BaseStage, BaseView, Chat
from petto.stg.egg import Egg
from petto.stats import Stats


class Specter(BaseStage):

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
        self.add_item((self.attack_button.__name__, self.attack_button()),
            (self.poof_button.__name__, self.poof_button()))

    def attack_button(self) -> Button:
        async def callback(interaction: Interaction) -> None:
            await interaction.message.delete()
            self.stats.update_health(self.webhook.id, -1)
            await self.pause(3)
            message = await self.send_random_emote('angry')
            await self.pause(5)
            try:
                await message.delete()
            except NotFound:
                pass
            return None
        button = Button(label='⚔️', style=ButtonStyle.danger)
        button.callback = callback
        return button

    def poof_button(self) -> Button:
        async def callback(interaction: Interaction) -> None:
            await interaction.message.delete()
            return None
        button = Button(label='🫳', style=ButtonStyle.blurple)
        button.callback = callback
        return button

    def water_button(self, stage: Egg) -> Button:
        async def callback(interaction: Interaction) -> None:
            await interaction.message.delete()
            self.remove_item(self.water_button)
            self.add_item((self.poof_button.__name__, self.poof_button()))
            await stage.delete()
            stage.remove_item(stage.peekaboo_button)
            stage.add_item((stage.water_button.__name__, stage.water_button()))
            await self.pause(5)
            await stage.send_random_chat(interaction.channel)
            return None
        button = Button(label='🪙➡️💧', style=ButtonStyle.green)
        button.callback = callback
        return button

    async def send(self, text: str) -> Message:
        if self.last_chat:
            try:
                await self.last_chat.delete()
            except NotFound:
                pass
        self.last_chat = await self.webhook.send(text, view=self.interface(self), wait=True)
        return self.last_chat

    async def send_random_chat(self) -> Message:
        message = await self.send(self.random_chat())
        return message

    async def send_random_emote(self, key: str) -> Message:
        message = await self.send(self.random_emote(key))
        return message

    class Interface(BaseView):

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
                embed = Embed(title=f"Level {self.stage.player.level} {replace_emoji(self.stage.alias, '')}",
                    description='A disembodied voice appears out of thin air from all directions without an apparent source.',
                    color=Color.from_str('#89CFF0'))
                embed.add_field(name='Health', value=display_value(self.stage.player.health, '❤️', '🖤'))
                embed.add_field(name='Mood', value=self.stage.player.mood)
                embed.add_field(name='Posts', value=self.stage.player.posts)
                embed.add_field(name='Score', value=self.stage.player.score)
                embed.set_image(url=f"attachment://{self.stage.info_img}")
                file = File(f"petto/stg/img/{self.stage.info_img}",
                    filename=f"{self.stage.info_img}")
                attach = {'attachments': [file], 'embeds': [embed]}
            await interaction.edit_original_response(**attach, view=self)
            return None
