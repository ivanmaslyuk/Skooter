from typing import Tuple

import skia

from webcolors import hex_to_rgb
from core.base import View, BoundingRect


class Rectangle(View):
    def __init__(self, width=0, height=0):
        self._background = '#ffffff'
        self._width = width
        self._height = height

    def draw(self, canvas: skia.Surface, x: float, y: float):
        x += self._x
        y += self._y
        rect = skia.Rect(x, y, x + self._width, y + self._height)
        r, g, b = hex_to_rgb(self._background)
        paint = skia.Paint(Color=skia.Color(r, g, b))
        canvas.drawRect(rect, paint)

        self.draw_children(canvas, x, y)

    def get_bounding_rect(self):
        return BoundingRect(0, 0, self._width, self._height)

    def background(self, color: str):
        self._background = color
        return self


class Text(View):
    def __init__(self, text):
        self._text = text
        self._color = '#000000'
        self._size = 14

    def draw(self, canvas: skia.Surface, x: float, y: float):
        x += self._x
        y += self._y
        r, g, b = hex_to_rgb(self._color)
        paint = skia.Paint(Color=skia.Color(r, g, b))
        font = skia.Font(None, self._size)
        bounds = skia.Rect()
        font.measureText(self._text, skia.TextEncoding.kUTF8, paint=paint, bounds=bounds)
        canvas.drawString(self._text, x, y + bounds.height(), font, paint)

        self.draw_children(canvas, x, y)

    def get_bounding_rect(self) -> BoundingRect:
        r, g, b = hex_to_rgb(self._color)
        paint = skia.Paint(Color=skia.Color(r, g, b))
        font = skia.Font(None, self._size)
        bounds = skia.Rect()
        font.measureText(self._text, skia.TextEncoding.kUTF8, paint=paint, bounds=bounds)
        return BoundingRect(0, 0, bounds.width(), bounds.height())

    def color(self, color: str):
        self._color = color
        return self

    def size(self, size: int):
        self._size = size
        return self


class HBox(View):
    class Alignment:
        BEGIN = 'BEGIN'
        CENTER = 'CENTER'
        END = 'END'

    class JustifyRule:
        BEGIN = 'BEGIN'
        END = 'END'
        SPACE_BETWEEN = 'SPACE_BETWEEN'
        SPACE_AROUND = 'SPACE_AROUND'

    def __init__(self, *items: View):
        self._items: Tuple[View] = items
        self._alignment = HBox.Alignment.BEGIN
        self._justify = HBox.JustifyRule.BEGIN
        self._spacing = 0
        self._height = None
        self._width = None
        self._wrap = False

    def draw(self, canvas: skia.Surface, x: float, y: float):
        x += self._x
        y += self._y

        content_x = self._spacing
        max_height = 0
        rows = []
        row = []
        for item in self._items:
            bounding_rect = item.get_bounding_rect()
            max_height = max(max_height, bounding_rect.height)

            if self._wrap and self._width and content_x + self._spacing + bounding_rect.width > self._width:
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
            leftover_width = self._width - row_info['row_items_width']
            for idx, item_info in enumerate(row):
                item = item_info['item']
                item_width = item_info['width']
                item_height = item_info['height']

                if self._justify == HBox.JustifyRule.END and idx == 0:
                    content_x += leftover_width

                if self._justify == HBox.JustifyRule.SPACE_AROUND:
                    content_x += leftover_width / (len(row) + 1)

                if self._justify == HBox.JustifyRule.SPACE_BETWEEN and idx != 0:
                    content_x += leftover_width / (len(row) - 1)

                if self._alignment == HBox.Alignment.BEGIN:
                    item.draw(canvas, x + content_x, y + content_y)
                elif self._alignment == HBox.Alignment.END:
                    item.draw(canvas, x + content_x, y + content_y + (max_height - item_height))
                elif self._alignment == HBox.Alignment.CENTER:
                    item.draw(canvas, x + content_x, y + content_y + (max_height - item_height) / 2)

                if self._justify == HBox.JustifyRule.SPACE_AROUND and idx == len(row) - 1:
                    content_x += leftover_width / (len(row) + 1)

                content_x += item_width + self._spacing

            content_y += max_height + self._spacing
            content_x = self._spacing

        self.draw_children(canvas, x, y)

    def get_bounding_rect(self) -> BoundingRect:
        return BoundingRect(0, 0, 0, 0)  # todo implement

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
    class Alignment:
        BEGIN = 'BEGIN'
        CENTER = 'CENTER'
        END = 'END'

    class JustifyRule:
        BEGIN = 'BEGIN'
        END = 'END'
        SPACE_BETWEEN = 'SPACE_BETWEEN'
        SPACE_AROUND = 'SPACE_AROUND'

    def __init__(self, *items: View):
        self._items: Tuple[View] = items
        self._alignment = VBox.Alignment.BEGIN
        self._justify = VBox.JustifyRule.BEGIN
        self._spacing = 0
        self._height = None
        self._width = None
        self._wrap = False

    def draw(self, canvas: skia.Surface, x: float, y: float):
        x += self._x
        y += self._y

        content_y = self._spacing
        max_width = 0
        columns = []
        column = []
        for item in self._items:
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
        for column_info in columns:
            column = column_info['column']
            leftover_height = self._height - column_info['column_items_height']
            for idx, item_info in enumerate(column):
                item = item_info['item']
                item_width = item_info['width']
                item_height = item_info['height']

                if self._justify == VBox.JustifyRule.END and idx == 0:
                    content_y += leftover_height

                if self._justify == VBox.JustifyRule.SPACE_AROUND:
                    content_y += leftover_height / (len(column) + 1)

                if self._justify == VBox.JustifyRule.SPACE_BETWEEN and idx != 0:
                    content_y += leftover_height / (len(column) - 1)

                if self._alignment == VBox.Alignment.BEGIN:
                    item.draw(canvas, x + content_x, y + content_y)
                elif self._alignment == VBox.Alignment.END:
                    item.draw(canvas, x + content_x + (max_width - item_width), y + content_y)
                elif self._alignment == VBox.Alignment.CENTER:
                    item.draw(canvas, x + content_x + (max_width - item_width) / 2, y + content_y)

                if self._justify == VBox.JustifyRule.SPACE_AROUND and idx == len(column) - 1:
                    content_y += leftover_height / (len(column) + 1)

                content_y += item_height + self._spacing

            content_x += max_width + self._spacing
            content_y = self._spacing

        self.draw_children(canvas, x, y)

    def get_bounding_rect(self) -> BoundingRect:
        return BoundingRect(0, 0, 0, 0)  # todo implement

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
