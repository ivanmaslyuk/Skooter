from typing import Optional

import skia

from core.base import View, Rect
from core.color import Color


class Text(View):
    def __init__(self, text):
        super().__init__()
        assert type(text) is str, 'Text must be of type "str".'
        self.__text = text
        self.__color: Color = Color.black()
        self.__size = 14
        self.__background: Optional[Color] = None

    def paint(self, canvas: skia.Canvas, x: float, y: float, width: float, height: float):
        x += self._x
        y += self._y
        paint = skia.Paint(Color=self.__color.as_skia_color())
        font = skia.Font(None, self.__size)
        text_width = font.measureText(self.__text, skia.TextEncoding.kUTF8)
        metrics = font.getMetrics()
        line_height = abs(metrics.fTop) + abs(metrics.fBottom)

        if self.__background:
            canvas.drawRect(
                skia.Rect.MakeXYWH(x, y, text_width, line_height),
                skia.Paint(Color=self.__background.as_skia_color()),
            )
        canvas.drawString(self.__text, x, y + line_height - metrics.fBottom, font, paint)

        self.draw_children(canvas, x, y, width, height)

    def get_bounding_rect(self) -> Rect:
        font = skia.Font(None, self.__size)
        width = font.measureText(self.__text, skia.TextEncoding.kUTF8)
        metrics = font.getMetrics()
        line_height = abs(metrics.fTop) + abs(metrics.fBottom)
        return Rect(0, 0, width, line_height)

    def color(self, color: Color) -> 'Text':
        self.__color = color
        return self

    def size(self, size: int) -> 'Text':
        self.__size = size
        return self

    def background(self, color: Color) -> 'Text':
        self.__background = color
        return self
