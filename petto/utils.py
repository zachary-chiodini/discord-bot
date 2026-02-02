from random import choice

from discord import TextChannel
from discord.ext.commands import Bot


def get_random_channel_with_perm(bot: Bot, guild_id: int) -> TextChannel:
    channels = set()
    for channel in bot.get_guild(guild_id).channels:
        perms = channel.permissions_for(bot.user)
        if perms.view_channel and perms.send_messages:
            channels.add(channel)
    if not channels:
        return bot.get_guild(guild_id).system_channel
    return choice(list(channels))
