from __future__ import annotations

import skia

from core.base import View, Rect
from .enums import Justify, Alignment, Direction


class Flex(View):
    def __init__(self):
        super(Flex, self).__init__()
        self._alignment = Alignment.BEGIN
        self._justify = Justify.BEGIN
        self._direction = Direction.HORIZONTAL
        self._spacing = 0
        self._height = None
        self._width = None
        self._wrap = False
        self._grow = {}

        self._view_width = 0
        self._view_height = 0

    def _lay_out_items(
            self,
            canvas: skia.Canvas,
            x: float,
            y: float,
            width: float,
            height: float,
            draw: bool = False
    ) -> None:
        content_x = self._spacing
        parallel_coord: int = 0  # This would be X if horizontal and Y if vertical
        max_height = 0
        rows = []
        row = []
        view_width = self._width or width
        if view_width:
            view_width -= self._left_padding + self._right_padding
        for item in self._children:
            bounding_rect = item.get_bounding_rect()  # todo might be affecting performance
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
                item = item_info['item']
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
                        item.draw(canvas, x + content_x, y + content_y, width, height)
                    elif self._alignment == Alignment.END:
                        item.draw(canvas, x + content_x, y + content_y + (max_height - item_height), width, height)
                    elif self._alignment == Alignment.CENTER:
                        item.draw(canvas, x + content_x, y + content_y + (max_height - item_height) / 2, width, height)

                if self._justify == Justify.SPACE_AROUND and idx == len(row) - 1:
                    content_x += leftover_width / (len(row) + 1)

                content_x += item_width + self._spacing

            self._view_width = max(self._view_width, content_x)
            content_y += max_height + self._spacing
            self._view_height = content_y
            content_x = self._spacing

    def draw(self, canvas: skia.Canvas, x: float, y: float, width: float, height: float) -> None:
        x += self._x + (self._left_padding or 0) + (self._left_margin or 0)
        y += self._y + (self._top_padding or 0) + (self._top_margin or 0)

        self._lay_out_items(
            canvas,
            x,
            y,
            width - (self._left_padding or 0) - (self._right_padding or 0),
            height - (self._top_padding or 0) - (self._bottom_padding or 0),
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

    def alignment(self, alignment) -> Flex:
        self._alignment = alignment
        return self

    def justify(self, justify) -> Flex:
        self._justify = justify
        return self

    def spacing(self, spacing: float) -> Flex:
        self._spacing = spacing
        return self

    def width(self, width: float) -> Flex:
        self._width = width
        return self

    def height(self, height: float) -> Flex:
        self._height = height
        return self

    def wrap(self, wrap: bool = False) -> Flex:
        self._wrap = wrap
        return self

    def grow(self, view: View, priority: int) -> Flex:
        self._grow[view] = priority
        return self
