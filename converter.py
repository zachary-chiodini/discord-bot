from discord import Member, Role, TextChannel
from discord.ext.commands import Context, Converter

from typing import Callable, Union


class Overload(Converter):

    def _cast_channel(self, context: Context, arg: str) -> Union[TextChannel, None]:
        return self._cast_mentionable(arg, '<#', '>', context.guild.get_channel)

    def _cast_member(self, context: Context, arg: str) -> Union[Member, None]:
        return self._cast_mentionable(arg, '<@', '>', context.guild.get_member, '!')

    def _cast_role(self, context: Context, arg: str) -> Union[Role, None]:
        return self._cast_mentionable(arg, '<@&', '>', context.guild.get_role)

    @staticmethod
    def _cast_mentionable(arg: str, prefix: str, suffix: str, get: Callable, legacy=''):
        if arg.startswith(prefix) and arg.endswith(suffix):
            entity_id = arg[len(prefix):-len(suffix)]
            if legacy:
                if entity_id.startswith(legacy):
                    entity_id = entity_id[1:]
            if entity_id.isdigit():
                entity = get(int(entity_id))
                if entity:
                    return entity
        return None


class Mention(Overload):

    async def convert(self, context: Context, arg: str) -> Union[Member, Role, str]:
        role = self._cast_role(context, arg)
        if role:
            return role
        member = self._cast_member(context, arg)
        if member:
            return member
        return arg


class MemberOrStr(Overload):
    
    async def convert(self, context: Context, arg: str) -> Union[Member, str]:
        member = self._cast_member(context, arg)
        if member:
            return member
        return arg


class RoleOrStr(Overload):

    async def convert(self, context: Context, arg: str) -> Union[Role, str]:
        role = self._cast_role(context, arg)
        if role:
            return role
        return arg


class Text(Overload):

    async def convert(self, context: Context, arg: str) -> Union[TextChannel, int, str]:
        if arg.isdigit():
            return int(arg)
        channel = self._cast_channel(context, arg)
        if channel:
            return channel
        return arg
