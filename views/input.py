import skia

from core.base import View, Rect
from core.color import Color


class Input(View):
    __slots__ = ('__color', '__size', '__caret_pos', )
    __value: str = 'sample text SAMPLE TEXT'

    def __init__(self):
        super(Input, self).__init__()
        self.__color: Color = Color.black()
        self.__size: int = 16
        self.__caret_pos: int = 5

    def paint(self, canvas: skia.Canvas, x: float, y: float, width: float, height: float):
        paint = skia.Paint(Color=self.__color.as_skia_color())
        font = skia.Font(None, self.__size)
        font.setSubpixel(True)
        bounds = skia.Rect()

        metrics = font.getMetrics()
        canvas.drawString(Input.__value, x, y + metrics.fCapHeight, font, paint)

        caret_offset = font.measureText(Input.__value[:self.__caret_pos], skia.TextEncoding.kUTF8, paint=paint, bounds=bounds)
        caret_height = abs(metrics.fTop) + metrics.fBottom
        canvas.drawLine(x + caret_offset, y, x + caret_offset, y + caret_height, paint)

    def get_bounding_rect(self) -> Rect:
        return Rect(0, 0, 300, 20)

    def handle_char(self, char: str):
        print('handle')
        Input.__value = Input.__value[self.__caret_pos:] + char + Input.__value[:self.__caret_pos]

    # Properties

    def color(self, color: Color) -> 'Input':
        self.__color = color
        return self
