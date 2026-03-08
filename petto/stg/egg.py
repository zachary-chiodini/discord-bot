from random import random

from discord import ButtonStyle, Interaction, Message, Webhook
from discord.errors import NotFound, InteractionResponded
from discord.ui import Button

from petto.stg.bases import Chat, Stage, WebhookStage
from petto.sts.state import State
from petto.sts.stats import Stats


class Specter(WebhookStage):

    alias = '😈Specter'
    avatar_img = 'specter_avatar.png'
    chat = Chat(
        angry=['You fool!', "I'll turn you into an egg!", 'Fuck you!', 'The darkness has taken you!', 'Stop this!'],
        neutral=['Abracadabra!', 'Boo!', 'Sim Sala Bim!', 'Poof!', 'Alakazam!', 'Ta-da!'])
    death_img: str
    info_img = 'specter_avatar.png'

    def __init__(self, stats: Stats, webhook: Webhook):
        super().__init__(stats, webhook)
        self.add_item(self.attack_button, self.poof_button)

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
            self.add_item(self.poof_button)
            stage.remove_item(stage.peekaboo_button)
            stage.add_item(stage.water_button)
            await self.pause(5)
            await stage.send_random_chat(interaction.channel)
            return None
        button = Button(label='🪙➡️💧', style=ButtonStyle.green)
        button.callback = callback
        return button


class Track:

    prize = 0
    queue = 0

    async def reset(self, egg: Egg, interaction: Interaction) -> None:
        if self.prize:
            self.prize = 0
            self.queue = 0
            egg.remove_item(egg.attack_button, egg.coin_button)
            egg.add_item(egg.attack_button, egg.coin_button)
            await egg.del_last_chat()
            await egg.pause(5)
            await egg.send_random_chat(interaction.channel)
        return None

    def update(self, n: int, egg: Egg) -> None:
        if (not self.prize) and (self.queue + n > 7):
            self.prize = 1
            self.queue = 1
            attack_button = egg.attack_button()
            attack_button.disabled = True
            coin_button = egg.coin_button()
            coin_button.disabled = True
            egg.remove_item(egg.peekaboo_button)
            egg.add_item((egg.attack_button.__name__, attack_button),
                (egg.coin_button.__name__, coin_button))
        elif self.queue + n >= 0:
            self.queue += n
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
        attack_button = self.attack_button()
        attack_button.disabled = True
        self.add_item((self.attack_button.__name__, attack_button), self.peekaboo_button)

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

    def clean_button(self) -> Button:
        async def callback(interaction: Interaction) -> None:
            await interaction.response.defer()
            self.state.update_hygiene(+1)
            self.remove_item(self.clean_button)
            self.add_item(self.peekaboo_button)
            await self.update(interaction)
            return None
        button = Button(label='🪥', style=ButtonStyle.blurple)
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
            await self.pause(5)
            await specter.send('You found a Geppetto Point!')
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
            track.update(+1, self)
            message = interaction.message
            while track.queue:
                if random() < 0.95:
                    i, prob = 0, [1.0, 0.5, 0.1, 0.1]
                    while random() < prob[i % len(prob)]:
                        try:
                            await message.delete()
                        except NotFound:
                            track.update(+1, self)
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
                        track.update(+1, self)
                        return None
                track.update(-1, self)
            await track.reset(self, interaction)
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
            self.state.update_thirst(+1)
            self.remove_item(self.water_button)
            self.add_item(self.clean_button)
            await self.update(interaction)
            return None
        button = Button(label='🫗', style=ButtonStyle.blurple)
        button.callback = callback
        return button
