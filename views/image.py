import skia

from core.base import View, Rect


class Image(View):
    __slots__ = ('__filename', )

    __cache = {}

    def __init__(self, filename: str, width: float, height: float):
        super(Image, self).__init__()
        self.__filename: str = filename
        self._width: float = width
        self._height: float = height

    def get_bounding_rect(self) -> Rect:
        return Rect(0, 0, self._width, self._height)

    def load_image(self):
        image = Image.__cache.get(self.__filename)
        if image is None:
            image = skia.Image.open(self.__filename).resize(self._width, self._height)  # noqa
            Image.__cache[self.__filename] = image
        if image is None:
            raise RuntimeError(f'Image could not be loaded: {self.__filename}')
        return image

    def draw(self, canvas: skia.Canvas, x: float, y: float, width: float, height: float):
        x += self._x + self._left_margin + self._left_padding
        y += self._y + self._top_margin + self._top_padding
        image = self.load_image()

        canvas.drawImageRect(image, skia.Rect.MakeXYWH(x, y, self._width, self._height))  # noqa

        self.draw_children(canvas, x,  y, width, height)
