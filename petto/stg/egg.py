from random import random

from discord import ButtonStyle, Interaction, Message
from discord.errors import NotFound, InteractionResponded
from discord.ui import Button

from petto.npc.specter import Specter
from petto.stg.base import Chat, Stage
from petto.state import State
from petto.stats import Stats


class Track:

    prize = 0
    queue = 0

    async def reset(self) -> None:
        if self.prize:
            self.prize = 0
            #view.add_item(view.stage.get_item_button('🪙'))
        return None
 
    async def update(self, n: int) -> None:
        if self.prize or (self.queue + n < 10):
            self.queue += n
            return None
        self.prize = 1
        self.queue = 1
        return None


# Track is global to "track" API calls.
track = Track()


class Egg(Stage):

    alias = 'Geppetto🐣Egg'
    avatar_img = 'egg_avatar.png'
    chat = Chat(neutral=['Crack', 'Tap', 'Peep', 'Squeak', 'Chirp'])
    color = '#FFD700'
    death_img = 'egg_death.png'
    description = 'An otherwordly Fabergé egg with a monstrous face, scales made of jewels inlaid into gold, a large center gem that looks like an eye and a crown with horns.'
    info_img = 'egg_info.png'
    specter_class = Specter

    def __init__(self, state: State, stats: Stats):
        super().__init__(state, stats)
        self._specter = None
        self.add_item((self.attack_button.__name__, self.attack_button()),
            (self.peekaboo_button.__name__, self.peekaboo_button()))

    def attack_button(self) -> Button:
        async def callback(interaction: Interaction) -> None:
            await interaction.message.delete()
            self.stats.update_health(self.state.id, -1)
            await self.specter_send(
                interaction, f"Do not attack {interaction.guild.me.mention}!")
            return None
        button = Button(label='⚔️', style=ButtonStyle.danger)
        button.callback = callback
        return button

    def coin_button(self) -> Button:
        async def callback(interaction: Interaction) -> None:
            await interaction.message.delete()
            self.remove_item(self.coin_button)
            button = self.peekaboo_button()
            button.disabled = True
            self.add_item((self.peekaboo_button.__name__, button))
            specter = await self.get_specter(interaction)
            specter.remove_item(specter.poof_button)
            specter.add_item((specter.water_button.__name__, specter.water_button(self)))
            self.pause(5)
            await specter.send_random_emote('neutral')
            return None
        button = Button(label='🪙', style=ButtonStyle.green)
        button.callback = callback
        return button

    async def get_specter(self, interaction: Interaction) -> Specter:
        if self._specter:
            return self._specter
        webhooks = await interaction.guild.webhooks()
        for webhook in webhooks:
            if webhook.name == Specter.alias:
                self._specter = Specter(self.stats, webhook)
                return self._specter
        raise Exception('Webhook not found.')

    def peekaboo_button(self) -> Button:
        async def callback(interaction: Interaction) -> None:
            global track
            await track.update(+1)
            message = interaction.message
            while track.queue:
                if random() < 0.95:
                    i, prob = 0, [1.0, 0.5, 0.1, 0.1]
                    while random() < prob[i % len(prob)]:
                        try:
                            await message.delete()
                        except NotFound:
                            await track.update(+1)
                            return None
                        await self.pause(5)
                        message = await self.send_random_chat(interaction.channel)
                        await self.pause(3)
                        i += 1
                else:
                    try:
                        await interaction.response.defer()
                    except InteractionResponded:
                        return None
                    except NotFound:
                        await track.update(+1)
                        return None
                await track.update(-1)
            await track.reset()
            return None
        button = Button(label='🫳', style=ButtonStyle.blurple)
        button.callback = callback
        return button

    async def specter_send(self, interaction: Interaction, text: str) -> Message:
        specter = await self.get_specter(interaction)
        message = await specter.send(text)
        return message

    def water_button(self) -> Button:
        async def callback(interaction: Interaction) -> None:
            await interaction.response.defer()
            return None
        button = Button(label='🫗', style=ButtonStyle.blurple)
        button.callback = callback
        return button
