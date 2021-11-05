import skia

from core.base import View, Rect
from views.enums import Alignment, Justify


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

    def _lay_out_items(self, canvas: skia.Canvas, x: float, y: float, width: float, height: float, draw: bool = False):
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
                item = item_info['item']
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
                        item.draw(canvas, x + content_x, y + content_y, width, height)
                    elif self._alignment == Alignment.END:
                        item.draw(canvas, x + content_x + (max_width - item_width), y + content_y, width, height)
                    elif self._alignment == Alignment.CENTER:
                        item.draw(canvas, x + content_x + (max_width - item_width) / 2, y + content_y, width, height)

                if self._justify == Justify.SPACE_AROUND and idx == len(column) - 1:
                    content_y += leftover_height / (len(column) + 1)

                content_y += item_height + self._spacing

            self._view_height = max(self._view_height, content_y)
            content_x += max_width + self._spacing
            self._view_width = content_x
            content_y = self._spacing

    def draw(self, canvas: skia.Canvas, x: float, y: float, width: float, height: float):
        x += self._x + self._left_padding or 0 + self._left_margin or 0
        y += self._y + self._top_padding or 0 + self._top_margin or 0

        self._lay_out_items(
            canvas,
            x,
            y,
            width - (self._left_padding or 0) - (self._right_padding or 0),
            height - (self._top_padding or 0) - (self._bottom_padding or 0),
            draw=True
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
