from random import random
from typing import List, Optional

from discord import ButtonStyle, Interaction, InteractionResponded, Message
from discord.errors import NotFound
from discord.ui import button, Button

from petto.stg.base import Chat, Stage, StageView
from petto.state import State
from petto.stats import Stats


class Track:

    prize = 0
    queue = 0

    async def reset(self, buttons: List[Button], interaction: Interaction,
            message: Message, view: StageView) -> None:
        if self.prize:
            self.prize = 0
            view.add_item(view.stage.get_item_button('🪙'))
        return None
 
    async def update(self, n: int, buttons: Optional[List[Button]] = None,
            interaction: Optional[Interaction] = None, view: Optional[StageView] = None) -> None:
        if self.prize or (self.queue + n < 10):
            self.queue += n
            return None
        self.prize = 1
        self.queue = 1
        for button in buttons:
            button.disabled = True
        try:
            await interaction.response.edit_message(view=view)
        except NotFound:
            pass
        return None


# Track is global to "track" API calls.
track = Track()


class Egg(Stage):

    alias = 'Geppetto🐣Egg'
    avatar_img = 'egg_avatar.png'
    chat = Chat(neutral=['Crack', 'Tap', 'Peep', 'Squeak', 'Chirp'])
    death_img = 'egg_death.png'
    info_img = 'egg_info.png'


    class Interface(StageView):

        @button(label='⚔️', style=ButtonStyle.danger)
        async def attack(self, interaction: Interaction, button: Button) -> None:
            await interaction.message.delete()
            self.stage.stats.update_health(self.stage.state.id, -1)
            await self.stage.specter_send(
                interaction, f"Do not attack {interaction.guild.me.mention}!")
            return None

        @button(label='🫳', style=ButtonStyle.blurple)
        async def peekaboo(self, interaction: Interaction, button: Button) -> None:
            global track
            await track.update(+1, self.children, interaction, self)
            message = interaction.message
            while track.queue:
                if random() < 0.95:
                    i, prob = 0, [1.0, 0.5, 0.1, 0.1]
                    while random() < prob[i % len(prob)]:
                        try:
                            await message.delete()
                        except NotFound:
                            await track.update(+1, self.children, interaction, self)
                            return None
                        await self.stage.pause(5)
                        message = await self.stage.send_random_chat(interaction.channel)
                        await self.stage.pause(3)
                        i += 1
                else:
                    try:
                        await interaction.response.defer()
                    except InteractionResponded:
                        return None
                    except NotFound:
                        await track.update(+1, self.children, interaction, self)
                        return None
                await track.update(-1)
            await track.reset(self.children, interaction, message, self)
            return None
