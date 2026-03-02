from random import random
from typing import Union

from discord import ButtonStyle, Interaction, Message, NotFound
from discord.ui import button, Button

from petto.stg.base import Chat, Stage, StageView


queue = 0
curr_message = None


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
            global curr_message, queue
            queue += 1
            message = interaction.message
            while queue > 0:
                print(queue)
                if random() < 0.95:
                    i, prob = 0, [1, 0.5, 0.1, 0.1]
                    while random() < prob[i % len(prob)]:
                        try:
                            await message.delete()
                        except NotFound:
                            queue += 1
                            return None
                        await self.stage.pause(5)
                        message = await self.stage.send_random_chat(interaction.channel)
                        await self.stage.pause(3)
                        i += 1
                else:
                    try:
                        await interaction.response.defer()
                    except NotFound:
                        queue += 1
                        return None
                queue -= 1
            return None
