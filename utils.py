from re import fullmatch

from discord import Member


async def add_ids_to(member: Member, *args: int) -> None:
    await member.add_roles(member.guild.get_role(role_id) for role_id in args)
    return None

def is_hexcode(str_: str) -> bool:
    return fullmatch(r'#([0-9a-fA-F]{6})', str_)
