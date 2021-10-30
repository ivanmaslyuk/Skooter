import skia

from webcolors import hex_to_rgb

from core import app
from core.base import View, Rect


class Justify:
    BEGIN = 'begin'
    END = 'end'
    SPACE_BETWEEN = 'space-between'
    SPACE_AROUND = 'space-around'


class Alignment:
    BEGIN = 'begin'
    CENTER = 'center'
    END = 'end'


class Rectangle(View):
    def __init__(self, width=0, height=0):
        super().__init__()
        self._background = '#ffffff'
        self._width = width
        self._height = height
        self._opacity = 1
        self._radius = 0

    def draw(self, canvas: skia.Canvas, x: float, y: float, width: float, height: float, env: app.Environment):
        x += self._x + self._left_margin + self._left_padding
        y += self._y + self._top_margin + self._top_padding
        rect = skia.Rect(x, y, x + self._width, y + self._height)
        r, g, b = hex_to_rgb(self._background)
        paint = skia.Paint(Color=skia.Color(r, g, b, round(255 * self._opacity)))
        if self._radius > 0:
            canvas.drawRoundRect(rect, self._radius, self._radius, paint)
        else:
            canvas.drawRect(rect, paint)

        self.draw_children(canvas, x, y, width, height, env)

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


class Text(View):
    def __init__(self, text):
        super().__init__()
        self._text = text
        self._color = '#000000'
        self._size = 14

    def draw(self, canvas: skia.Canvas, x: float, y: float, width: float, height: float, env: app.Environment):
        x += self._x
        y += self._y
        r, g, b = hex_to_rgb(self._color)
        paint = skia.Paint(Color=skia.Color(r, g, b))
        font = skia.Font(None, self._size)
        bounds = skia.Rect()
        font.measureText(self._text, skia.TextEncoding.kUTF8, paint=paint, bounds=bounds)
        canvas.drawString(self._text, x, y + bounds.height(), font, paint)

        self.draw_children(canvas, x, y, width, height, env)

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


class HBox(View):
    def __init__(self):
        super().__init__()
        self._alignment = Alignment.BEGIN
        self._justify = Justify.BEGIN
        self._spacing = 0
        self._height = None
        self._width = None
        self._wrap = False

        self._view_width = 0
        self._view_height = 0

    def _lay_out_items(
            self,
            canvas: skia.Canvas,
            x: float,
            y: float,
            width: float,
            height: float,
            env: app.Environment,
            draw: bool = False,
    ):
        content_x = self._spacing
        max_height = 0
        rows = []
        row = []
        view_width = self._width or width
        if view_width:
            view_width -= self._left_padding + self._right_padding
        for item in self._children:
            bounding_rect = item.get_bounding_rect()
            max_height = max(max_height, bounding_rect.height)

            if self._wrap and view_width and content_x + self._spacing + bounding_rect.width > view_width:
                rows.append({
                    'row': row,
                    'row_items_width': content_x,
                })
                row = []
                content_x = self._spacing

            row.append({
                'width': bounding_rect.width,
                'height': bounding_rect.height,
                'item': item,
            })
            content_x += bounding_rect.width + self._spacing

        if row:
            rows.append({
                'row': row,
                'row_items_width': content_x,
            })

        content_x = self._spacing
        content_y = self._spacing
        for row_info in rows:
            row = row_info['row']
            leftover_width = view_width - row_info['row_items_width']
            for idx, item_info in enumerate(row):
                item: View = item_info['item']
                item_width = item_info['width']
                item_height = item_info['height']

                if self._justify == Justify.END and idx == 0:
                    content_x += leftover_width

                if self._justify == Justify.SPACE_AROUND:
                    content_x += leftover_width / (len(row) + 1)

                if self._justify == Justify.SPACE_BETWEEN and idx != 0:
                    content_x += leftover_width / (len(row) - 1)

                if draw:
                    if self._alignment == Alignment.BEGIN:
                        item.draw(canvas, x + content_x, y + content_y, width, height, env)
                    elif self._alignment == Alignment.END:
                        item.draw(canvas, x + content_x, y + content_y + (max_height - item_height), width, height, env)
                    elif self._alignment == Alignment.CENTER:
                        item.draw(
                            canvas,
                            x + content_x,
                            y + content_y + (max_height - item_height) / 2,
                            width, height,
                            env,
                        )

                if self._justify == Justify.SPACE_AROUND and idx == len(row) - 1:
                    content_x += leftover_width / (len(row) + 1)

                content_x += item_width + self._spacing

            self._view_width = max(self._view_width, content_x)
            content_y += max_height + self._spacing
            self._view_height = content_y
            content_x = self._spacing

    def draw(self, canvas: skia.Canvas, x: float, y: float, width: float, height: float, env: app.Environment):
        x += self._x + (self._left_padding or 0) + (self._left_margin or 0)
        y += self._y + (self._top_padding or 0) + (self._top_margin or 0)

        self._lay_out_items(
            canvas,
            x,
            y,
            width - (self._left_padding or 0) - (self._right_padding or 0),
            height - (self._top_padding or 0) - (self._bottom_padding or 0),
            env,
            draw=True,
        )

    def get_bounding_rect(self) -> Rect:
        width = self._width
        height = self._height
        if height is None or width is None:
            self._lay_out_items(None, 0, 0, 640, 480)
            height = height or self._view_height
            width = width or self._view_width

        return Rect(
            x=0,
            y=0,
            width=self._left_margin + width + self._right_margin,
            height=self._top_margin + height + self._bottom_margin,
        )

    def alignment(self, alignment):
        self._alignment = alignment
        return self

    def justify(self, justify):
        self._justify = justify
        return self

    def spacing(self, spacing: float):
        self._spacing = spacing
        return self

    def width(self, width: float):
        self._width = width
        return self

    def height(self, height: float):
        self._height = height
        return self

    def wrap(self, wrap: bool = False):
        self._wrap = wrap
        return self


class VBox(View):
    def __init__(self):
        super().__init__()
        self._alignment = Alignment.BEGIN
        self._justify = Justify.BEGIN
        self._spacing = 0
        self._height = None
        self._width = None
        self._wrap = False

        self._view_height = 0
        self._view_width = 0

    def _lay_out_items(
            self,
            canvas: skia.Canvas,
            x: float,
            y: float,
            width: float,
            height: float,
            env: app.Environment,
            draw: bool = False,
    ):
        content_y = self._spacing
        max_width = 0
        columns = []
        column = []
        for item in self._children:
            bounding_rect = item.get_bounding_rect()
            max_width = max(max_width, bounding_rect.width)

            if self._wrap and self._height and content_y + self._spacing + bounding_rect.height > self._height:
                columns.append({
                    'column': column,
                    'column_items_height': content_y,
                })
                column = []
                content_y = self._spacing

            column.append({
                'width': bounding_rect.width,
                'height': bounding_rect.height,
                'item': item,
            })
            content_y += bounding_rect.height + self._spacing

        if column:
            columns.append({
                'column': column,
                'column_items_height': content_y,
            })

        content_x = self._spacing
        content_y = self._spacing
        self._view_height = 0
        self._view_width = 0
        for column_info in columns:
            column = column_info['column']
            for idx, item_info in enumerate(column):
                item: View = item_info['item']
                item_width = item_info['width']
                item_height = item_info['height']

                if self._height:
                    leftover_height = self._height - column_info['column_items_height']

                    if self._justify == Justify.END and idx == 0:
                        content_y += leftover_height

                    if self._justify == Justify.SPACE_AROUND:
                        content_y += leftover_height / (len(column) + 1)

                    if self._justify == Justify.SPACE_BETWEEN and idx != 0:
                        content_y += leftover_height / (len(column) - 1)

                if draw:
                    if self._alignment == Alignment.BEGIN:
                        item.draw(canvas, x + content_x, y + content_y, width, height, env)
                    elif self._alignment == Alignment.END:
                        item.draw(canvas, x + content_x + (max_width - item_width), y + content_y, width, height, env)
                    elif self._alignment == Alignment.CENTER:
                        item.draw(
                            canvas,
                            x + content_x + (max_width - item_width) / 2,
                            y + content_y,
                            width,
                            height,
                            env,
                        )

                if self._justify == Justify.SPACE_AROUND and idx == len(column) - 1:
                    content_y += leftover_height / (len(column) + 1)

                content_y += item_height + self._spacing

            self._view_height = max(self._view_height, content_y)
            content_x += max_width + self._spacing
            self._view_width = content_x
            content_y = self._spacing

    def draw(self, canvas: skia.Canvas, x: float, y: float, width: float, height: float, env: app.Environment):
        x += self._x + self._left_padding or 0 + self._left_margin or 0
        y += self._y + self._top_padding or 0 + self._top_margin or 0

        self._lay_out_items(
            canvas,
            x,
            y,
            width - (self._left_padding or 0) - (self._right_padding or 0),
            height - (self._top_padding or 0) - (self._bottom_padding or 0),
            env,
            draw=True,
        )

    def get_bounding_rect(self) -> Rect:
        self._lay_out_items(None, 0, 0, 640, 480)
        return Rect(0, 0, self._view_width, self._view_height)

    def alignment(self, alignment):
        self._alignment = alignment
        return self

    def justify(self, justify):
        self._justify = justify
        return self

    def spacing(self, spacing: float):
        self._spacing = spacing
        return self

    def width(self, width: float):
        self._width = width
        return self

    def height(self, height: float):
        self._height = height
        return self

    def wrap(self, wrap: bool = False):
        self._wrap = wrap
        return self


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

    def draw(self, canvas: skia.Canvas, x: float, y: float, width: float, height: float, env: app.Environment):
        x += self._x + self._left_margin + self._left_padding
        y += self._y + self._top_margin + self._top_padding
        image = self.load_image()

        canvas.drawImageRect(image, skia.Rect.MakeXYWH(x, y, self.__width, self.__height))

        self.draw_children(canvas, x,  y, width, height, env)
