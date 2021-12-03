import skia

from core.base import View, Rect
from core.color import Color
from core.data import ContextProperty
from core.key_input import KeyInput, Keys, KeyListener


class Input(View, KeyListener):
    __slots__ = ('__color', '__size', )

    __value: str = '123456789'
    __caret_pos: int = 3
    __key_input: KeyInput = ContextProperty()

    def __init__(self):
        super(Input, self).__init__()
        self.__color: Color = Color.black()
        self.__size: int = 16
        self.__key_input.add_listener(self)

    def paint(self, canvas: skia.Canvas, x: float, y: float, width: float, height: float):
        paint = skia.Paint(Color=self.__color.as_skia_color())
        font = skia.Font(None, self.__size)
        font.setSubpixel(True)
        bounds = skia.Rect()

        metrics = font.getMetrics()
        canvas.drawString(Input.__value, x, y + metrics.fCapHeight, font, paint)

        caret_offset = font.measureText(
            Input.__value[:Input.__caret_pos],
            skia.TextEncoding.kUTF8,
            paint=paint,
            bounds=bounds,
        )
        caret_height = abs(metrics.fTop) + metrics.fBottom
        canvas.drawLine(x + caret_offset, y, x + caret_offset, y + caret_height, paint)

    def get_bounding_rect(self) -> Rect:
        return Rect(0, 0, 300, 20)

    def handle_char(self, char: str):
        Input.__value = Input.__value[:Input.__caret_pos] + char + Input.__value[Input.__caret_pos:]
        Input.__caret_pos += 1

    def handle_key(self, key: int, action: int):
        if key == Keys.ARROW_RIGHT and action == 1:
            Input.__caret_pos = min(Input.__caret_pos + 1, len(self.__value))
        elif key == Keys.ARROW_LEFT and action == 1:
            Input.__caret_pos = max(Input.__caret_pos - 1, 0)
        elif key == Keys.BACKSPACE and action == 1:
            Input.__value = (
                    Input.__value[:max(0, Input.__caret_pos - 1)]
                    + Input.__value[Input.__caret_pos:]
            )
            Input.__caret_pos = max(0, Input.__caret_pos - 1)

    # Properties

    def color(self, color: Color) -> 'Input':
        self.__color = color
        return self
