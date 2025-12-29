from re import fullmatch


def is_hexcode(str_: str) -> bool:
    return fullmatch(r'#([0-9a-fA-F]{6})', str_)
