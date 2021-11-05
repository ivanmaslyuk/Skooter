import skia

from core.base import View, Rect


class Image(View):
    __cache = {}

    def __init__(self, filename: str, width: float, height: float):
        super(Image, self).__init__()
        self.__filename: str = filename
        self.__width: float = width
        self.__height: float = height

    def get_bounding_rect(self) -> Rect:
        return Rect(0, 0, self.__width, self.__height)

    def load_image(self):
        image = Image.__cache.get(self.__filename)
        if image is None:
            image = skia.Image.open(self.__filename).resize(self.__width, self.__height)
            Image.__cache[self.__filename] = image
        if image is None:
            raise RuntimeError(f'Image could not be loaded: {self.__filename}')
        return image

    def draw(self, canvas: skia.Canvas, x: float, y: float, width: float, height: float):
        x += self._x + self._left_margin + self._left_padding
        y += self._y + self._top_margin + self._top_padding
        image = self.load_image()

        canvas.drawImageRect(image, skia.Rect.MakeXYWH(x, y, self.__width, self.__height))

        self.draw_children(canvas, x,  y, width, height)
