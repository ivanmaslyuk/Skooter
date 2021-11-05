import skia

from webcolors import hex_to_rgb
from core.base import View, Rect


class Text(View):
    def __init__(self, text):
        super().__init__()
        self._text = text
        self._color = '#000000'
        self._size = 14

    def draw(self, canvas: skia.Canvas, x: float, y: float, width: float, height: float):
        x += self._x
        y += self._y
        r, g, b = hex_to_rgb(self._color)
        paint = skia.Paint(Color=skia.Color(r, g, b))
        font = skia.Font(None, self._size)
        bounds = skia.Rect()
        font.measureText(self._text, skia.TextEncoding.kUTF8, paint=paint, bounds=bounds)
        canvas.drawString(self._text, x, y + bounds.height(), font, paint)

        self.draw_children(canvas, x, y, width, height)

    def get_bounding_rect(self) -> Rect:
        r, g, b = hex_to_rgb(self._color)
        paint = skia.Paint(Color=skia.Color(r, g, b))
        font = skia.Font(None, self._size)
        bounds = skia.Rect()
        font.measureText(self._text, skia.TextEncoding.kUTF8, paint=paint, bounds=bounds)
        return Rect(0, 0, bounds.width(), bounds.height() + 3)

    def color(self, color: str):
        self._color = color
        return self

    def size(self, size: int):
        self._size = size
        return self
