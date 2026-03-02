from pathlib import Path

from discord import Intents, Object
from discord.ext import commands

from petto.petto import Petto


def raw_val_from(path: Path) -> str:
    if path.exists():
        with open(str(path)) as f:
            raw = f.read().strip()
    else:
        raise FileNotFoundError(f"File {str(path)} must exist.")
    return raw


path = Path('petto/txt/guild.txt')
guild_id = raw_val_from(path)
try:
    guild_id = int(guild_id)
except ValueError:
    raise ValueError(f"File {str(path)} must contain a server id.")

path = Path('petto/txt/token.txt')
token_raw = raw_val_from(path)
if not token_raw:
    raise ValueError(f"File {str(path)} must contain a Discord bot token.")

bot = commands.Bot(command_prefix='/', intents=Intents.all())

@bot.event
async def on_ready():
    await bot.add_cog(Petto(bot, guild_id))
    guild_obj = Object(id=guild_id)
    bot.tree.copy_global_to(guild=guild_obj)
    #bot.tree.clear_commands(guild=guild_obj)
    await bot.tree.sync(guild=guild_obj)

bot.run(token_raw)
