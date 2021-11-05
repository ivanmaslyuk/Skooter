import skia

from webcolors import hex_to_rgb
from core.base import View, Rect


class Rectangle(View):
    def __init__(self, width=0, height=0):
        super().__init__()
        self._background = '#ffffff'
        self._width = width
        self._height = height
        self._opacity = 1
        self._radius = 0

    def draw(self, canvas: skia.Canvas, x: float, y: float, width: float, height: float):
        x += self._x + self._left_margin + self._left_padding
        y += self._y + self._top_margin + self._top_padding
        rect = skia.Rect(x, y, x + self._width, y + self._height)
        r, g, b = hex_to_rgb(self._background)
        paint = skia.Paint(Color=skia.Color(r, g, b, round(255 * self._opacity)))
        if self._radius > 0:
            canvas.drawRoundRect(rect, self._radius, self._radius, paint)
        else:
            canvas.drawRect(rect, paint)

        self.draw_children(canvas, x, y, width, height)

    def get_bounding_rect(self):
        return Rect(
            x=0,
            y=0,
            width=self._left_margin + self._left_padding + self._width + self._right_padding + self._right_margin,
            height=self._top_margin + self._top_padding + self._height + self._bottom_padding + self._bottom_margin,
        )

    def background(self, color: str):
        self._background = color
        return self

    def opacity(self, opacity: float):
        self._opacity = opacity
        return self

    def radius(self, radius: float):
        self._radius = radius
        return self
