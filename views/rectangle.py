import skia

from core.base import View, Rect
from core.color import Color


class Rectangle(View):
    def __init__(self, width=None, height=None):
        super().__init__()
        self._background: Color = Color.white()
        self._width = width
        self._height = height
        self._opacity = 1
        self._radius = 0

    def paint(self, canvas: skia.Canvas, x: float, y: float, width: float, height: float):
        x += self._x + self._left_margin + self._left_padding
        y += self._y + self._top_margin + self._top_padding
        rect_width = self._width or width - self._left_margin - self._right_margin
        rect_height = self._height or height - self._top_margin - self._bottom_margin
        rect = skia.Rect(x, y, x + rect_width, y + rect_height)
        paint = skia.Paint(Color=self._background.as_skia_color())
        if self._radius > 0:
            canvas.drawRoundRect(rect, self._radius, self._radius, paint)  # noqa
        else:
            canvas.drawRect(rect, paint)  # noqa

    def get_bounding_rect(self):
        return Rect(
            x=0,
            y=0,
            width=(
                    self._left_margin + self._left_padding
                    + (self._width or 0) + self._right_padding + self._right_margin
            ),
            height=(
                    self._top_margin + self._top_padding
                    + (self._height or 0) + self._bottom_padding + self._bottom_margin
            ),
        )

    def background(self, color: Color) -> 'Rectangle':
        self._background = color
        return self

    def opacity(self, opacity: float) -> 'Rectangle':
        self._opacity = opacity
        return self

    def radius(self, radius: float) -> 'Rectangle':
        self._radius = radius
        return self

    def width(self, width: float) -> 'Rectangle':
        self._width = width
        return self

    def height(self, height: float) -> 'Rectangle':
        self._height = height
        return self
