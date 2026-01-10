from emoji import emoji_list
from typing import List


def get_emoji_list(str_: str) -> List[str]:
    return [dict_['emoji'] for dict_ in emoji_list(str_)]
