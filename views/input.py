from typing import Optional

import skia

from core.base import View, Rect
from core.color import Color
from core.data import ContextProperty, Binding, DataBinding
from core.key_input import KeyInput, Keys, KeyListener


class Input(View, KeyListener):
    __slots__ = ('__color', '__size', )

    __key_input: KeyInput = ContextProperty()

    text = Binding()

    def __init__(self, text: DataBinding):
        super(Input, self).__init__(text=text)
        self.__color: Color = Color.black()
        self.__size: int = 16
        self.__key_input.add_listener(self)
        self.__background: Optional[Color] = None
        self.__caret_pos: int = 3

    def paint(self, canvas: skia.Canvas, x: float, y: float, width: float, height: float):
        paint = skia.Paint(Color=self.__color.as_skia_color())
        font = skia.Font(None, self.__size)
        font.setSubpixel(True)
        metrics = font.getMetrics()
        text_width = font.measureText(self.text, skia.TextEncoding.kUTF8)
        line_height = abs(metrics.fTop) + abs(metrics.fBottom)

        if self.__background:
            canvas.drawRect(
                skia.Rect.MakeXYWH(x, y, text_width, line_height),
                skia.Paint(Color=self.__background.as_skia_color()),
            )

        canvas.drawString(self.text, x, y + line_height - metrics.fBottom, font, paint)

        caret_offset = font.measureText(
            self.text[:self.__caret_pos],
            skia.TextEncoding.kUTF8,
            paint=paint,
        )
        canvas.drawLine(x + caret_offset, y, x + caret_offset, y + line_height, paint)

    def get_bounding_rect(self) -> Rect:
        font = skia.Font(None, self.__size)
        metrics = font.getMetrics()
        text_width = font.measureText(self.text, skia.TextEncoding.kUTF8)
        line_height = abs(metrics.fTop) + abs(metrics.fBottom)
        return Rect(0, 0, text_width, line_height)

    def handle_char(self, char: str):
        self.text = self.text[:self.__caret_pos] + char + self.text[self.__caret_pos:]
        self.__caret_pos += 1

    def handle_key(self, key: int, action: int):
        if key == Keys.ARROW_RIGHT and action == 1:
            self.__caret_pos = min(self.__caret_pos + 1, len(self.text))
        elif key == Keys.ARROW_LEFT and action == 1:
            self.__caret_pos = max(self.__caret_pos - 1, 0)
        elif key == Keys.BACKSPACE and action == 1:
            self.text = (
                    self.text[:max(0, self.__caret_pos - 1)]
                    + self.text[self.__caret_pos:]
            )
            self.__caret_pos = max(0, self.__caret_pos - 1)

    # Properties

    def color(self, color: Color) -> 'Input':
        self.__color = color
        return self

    def background(self, color: Color) -> 'Input':
        self.__background = color
        return self
