from random import randint, random
from typing import Dict, List

from discord import AllowedMentions, ButtonStyle, Embed, File, Interaction, Role, Webhook
from discord.ui import button, Button, View
from emoji import replace_emoji

from stats import Player


class Interface(View):

    def __init__(self, alias: str, description: str, filename: str, player: Player,
            roles: Dict[str, Role]):
        super().__init__()
        self.alias = alias
        self.description = description
        self.filename = filename
        self.player = player
        self.roles = roles
        self.toggled = False

    @button(label="Fight!", style=ButtonStyle.grey)
    async def fight_button(self, interaction: Interaction, button: Button) -> None:
        return None

    @button(label='▼ Index', style=ButtonStyle.blurple)
    async def bio_button(self, interaction: Interaction, button: Button) -> None:
        if self.toggled:
            button.label = '▼ Index'
            attach = {'embeds': [], 'attachments': []}
            self.toggled = False
        else:
            button.label = '▲ Index'
            level = self.roles['Level'][self.player.level]
            if self.player.level == 99:
                power = self.roles['🎖️🎖️🎖️']
            else:
                power = self.roles['🎖️' * ((self.player.level // 33) + 1)]
            vigor = self.roles[self.player.get_health_str()]
            embed = Embed(
                title=f"Level {self.player.level} {replace_emoji(self.alias, '')}",
                description=(f"{level.mention}{vigor.mention}{power.mention}\n"
                    f"**Kills**: 0 **Posts**: {self.player.posts} **Score**: {self.player.score}\n"
                    f"{self.description}"),
                color=level.color)
            file = File(f"database/images/{self.filename}.png", filename=f"{self.filename}.png")
            embed.set_image(url=f"attachment://{self.filename}.png")
            attach = {'embeds': [embed], 'attachments': [file]}
            self.toggled = True
        await interaction.response.edit_message(**attach, view=self)
        return None


class NPC:

    alias: str
    avatar: str
    bias: int
    coins: int
    index: str
    items: List[str]
    passive: List[str]
    points: int
    thumbnail: str

    def __init__(self, player: Player, roles: Dict[str, Role], webhook: Webhook):
        self.interface = Interface(self.alias, self.index, self.thumbnail, player, roles)
        self.player = player
        self.roles = roles
        self.webhook = webhook

    async def send_passive_dialogue(self) -> None:
        async for message in self.webhook.channel.history(limit=1):
            if message.webhook_id == self.webhook.id:
                await self.webhook.edit_message(message.id, view=None)
        await self.webhook.send(self.passive[randint(0, len(self.passive) - 1)],
            view=self.interface, allowed_mentions=AllowedMentions(roles=True))
        return None


class Skyevolutrex(NPC):

    alias = '🐾Wild Skyevolutrex'
    avatar = 'wildskyevolutrex'
    bias = 0.5
    coins = 5
    index = "A creature that resembles a dog with wings, an orange hooked beak with teeth-like serrations and blue fur-like protofeathers. It's a nocturnal, small-pack hexapod with hollow bones that inhabits the caves of high-altitude forest cliffs in The Other World."
    items = ['🪬']
    passive = ['EEK!', 'RAW!', 'BWARK!', 'SQAWK!', 'CAW!']
    points = 3000
    thumbnail = 'wildskyevolutrex'

    def __init__(self, player: Player, roles: Dict, webhook: Webhook):
        super().__init__(player, roles, webhook)
