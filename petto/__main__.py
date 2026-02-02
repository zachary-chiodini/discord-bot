from discord import Object
from discord.ext import commands, Intents

from petto.petto import Petto


with open('guild_id.txt') as f:
    guild_id = int(f.read())

bot = commands.Bot(command_prefix='/', intents=Intents.all())

@bot.event
async def on_ready():
    await bot.add_cog(Petto(bot, guild_id))
    guild_obj = Object(id=guild_id)
    bot.tree.copy_global_to(guild=guild_obj)
    #bot.tree.clear_commands(guild=guild_obj)
    await bot.tree.sync(guild=guild_obj)

with open('token.txt') as token_file:
    token_raw = token_file.read()

bot.run(token_raw)
