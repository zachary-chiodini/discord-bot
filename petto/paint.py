from os import remove
from pathlib import Path
from re import fullmatch
from typing import Union

from PIL import Image


class Paint:

    file = Path('color.txt')

    def __init__(self):
        self._paint = {}
        if self.file.exists():
            with open(str(self.file)) as f:
                for line in f.readlines():
                    paint_id, hex_code = line.split(',')
                    self._paint[int(paint_id)] = hex_code.strip()
        else:
            self.file.touch()

    def delete(self, paint_id: int) -> None:
        remove(self.image_path(self._paint[paint_id]))
        del self._paint[paint_id]
        with open(str(self.file), 'w') as f:
            for paint_id_, hex_code in self._paint.items():
                f.write(f"{paint_id_},{hex_code}\n")
        return None

    def id_exists(self, paint_id: int) -> bool:
        return paint_id in self._paint

    def get(self, id_or_hex: Union[int, str]) -> Union[int, str]:
        if isinstance(id_or_hex, int):
            return f"#{self._paint[id_or_hex]}"
        hex_code = id_or_hex.lstrip('#')
        for paint_id, hex_code_i in self._paint.items():
            if hex_code_i == hex_code:
                return paint_id
        return 0

    def image_path(self, hex_code: str) -> str:
        return f"imgs/{hex_code}.png"

    @staticmethod
    def is_hexcode(str_: str) -> bool:
        return fullmatch(r'#([0-9a-fA-F]{6})', str_)

    @staticmethod
    def mix(*hex_codes: str) -> str:
        r, g, b = 0, 0, 0
        for hex_code in hex_codes:
            r += int(hex_code[1:3], 16)
            g += int(hex_code[3:5], 16)
            b += int(hex_code[5:7], 16)
        r = round(r / len(hex_codes))
        g = round(g / len(hex_codes))
        b = round(b / len(hex_codes))
        return f"#{r:02X}{g:02X}{b:02X}"

    def reset(self) -> None:
        if self.file.exists():
            self.file.write_text('')
        for _, hex_code in self._paint.items():
            remove(self.image_path(hex_code.lstrip('#')))
        self._paint = {}
        return None

    def update(self, paint_id: str, hex_code: str) -> None:
        hex_code = hex_code.lstrip('#').upper()
        self._paint[paint_id] = hex_code
        with open(str(self.file), 'a') as f:
            f.write(f"{paint_id},{hex_code}\n")
        img = Image.new("RGB", (256, 256), tuple(bytes.fromhex(hex_code)))
        img.save(self.image_path(hex_code), format='PNG')
        return None
