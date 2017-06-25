from typing import List, Tuple, Iterable
from pathlib import Path

PUT_FRAME = 'matrix_custom_frame'
DISPLAY = 'matrix_effect_custom'

# row_index, start, end
SZ_INIT = 3


class Frame:
    def __init__(self, rows: Iterable = None):
        self.frame = [[]] * 6
        if rows:
            for i, row in enumerate(rows):
                self.set_row(i, row)

    def set_row(self, index: int, row: List[Tuple[int, int, int]]):
        if len(row) > 22:
            raise ValueError("No more than 22 keys per row allowed.")
        self.frame[index] = row

    def draw(self, device: Path):
        for i, row in enumerate(self.frame):
            with (device / PUT_FRAME).open('wb') as put_frame:
                self._write_frame(put_frame, i, row)
        with (device / DISPLAY).open('wb') as display:
            display.write(b'1')

    @staticmethod
    def _write_frame(fp, i, row):
        result = bytearray(SZ_INIT + 0x10 * 3)
        result[0] = i
        result[1] = 0
        result[2] = 0x0F
        for ci, color in enumerate(row):
            ri = 3 + (ci * 3)
            result[ri:ri + 3] = color

        fp.write(result)


__all__ = ['Frame']
