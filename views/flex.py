from __future__ import annotations

import dataclasses
from typing import List, Optional

import skia

from core.base import View, Rect
from core.color import Color
from .enums import Justify, Alignment, Direction


class Flex(View):
    __slots__ = (
        '_alignment', '_justify', '_direction', '_spacing', '_height', '_width', '_wrap', '_grow', '_layout_cache',
        '_background', '__debug',
    )

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
        self._layout_cache: Optional[Layout] = None
        self._background: Optional[Color] = None
        self.__debug = False

    def _get_groups(self, available_width: float, available_height: float) -> (List[dict], float):
        group_advance = self._spacing
        max_spread = 0
        groups = []
        group = []
        advance_limit = self._direction_choice(
            horizontal_choice=available_width,
            vertical_choice=available_height,
        )

        for view in self._children:
            bounding_rect = view.get_bounding_rect()
            item_advance = self._get_advance(bounding_rect.width, bounding_rect.height)
            item_spread = self._get_spread(bounding_rect.width, bounding_rect.height)
            max_spread = max(max_spread, item_spread)

            if self._wrap and group_advance + item_advance + self._spacing > advance_limit:
                groups.append({
                    'group': group,
                    'group_advance': group_advance,
                })
                group = []
                group_advance = self._spacing

            group.append({
                'advance': item_advance,
                'spread': item_spread,
                'view': view,
            })
            group_advance += item_advance + self._spacing

        if group:
            groups.append({
                'group': group,
                'group_advance': group_advance,
            })

        return groups, max_spread

    def _get_layout(self, available_width: float, available_height: float) -> Layout:
        # if self._layout_cache:
        #     return self._layout_cache

        available_width -= self._left_padding + self._right_padding
        available_height -= self._top_padding + self._bottom_padding

        groups, max_spread = self._get_groups(available_width, available_height)
        grow_sum = sum(self._grow.values())

        content_pr = self._spacing
        content_pp = self._spacing
        layout_items = []
        flex_width = 0
        flex_height = 0
        for group_info in groups:
            leftover_advance = self._direction_choice(
                horizontal_choice=available_width - group_info['group_advance'],
                vertical_choice=available_height - group_info['group_advance'],
            )
            grow_advance = leftover_advance
            if self._justify == Justify.END:
                content_pr += leftover_advance

            group = group_info['group']
            for idx, item_info in enumerate(group):
                view = item_info['view']
                item_advance = item_info['advance']
                item_spread = item_info['spread']

                if grow_sum > 0 and leftover_advance > 0:
                    item_grow_advance = (self._grow.get(view, 0) / grow_sum) * grow_advance
                    item_advance += item_grow_advance
                    leftover_advance -= item_grow_advance

                if self._justify == Justify.SPACE_AROUND:
                    content_pr += leftover_advance / (len(group) + 1)
                if self._justify == Justify.SPACE_BETWEEN and idx != 0:
                    content_pr += leftover_advance / (len(group) - 1)

                item_x = self._direction_choice(content_pr, content_pp)
                item_y = self._direction_choice(content_pp, content_pr)
                item_width = self._direction_choice(item_advance, available_width)
                item_height = self._direction_choice(available_height, item_advance)
                if self._alignment == Alignment.END:
                    if self._direction == Direction.HORIZONTAL:
                        item_y += max_spread - item_spread
                    else:
                        item_x += max_spread - item_spread
                elif self._alignment == Alignment.CENTER:
                    if self._direction == Direction.HORIZONTAL:
                        item_y += (max_spread - item_spread) / 2
                    else:
                        item_x += (max_spread - item_spread) / 2
                layout_items.append(LayoutItem(view, item_x, item_y, item_width, item_height))

                if self._justify == Justify.SPACE_AROUND and idx == len(group) - 1:
                    content_pr += leftover_advance / (len(group) + 1)

                content_pr += item_advance + self._spacing

            flex_width = max(flex_width, content_pr)
            content_pp += max_spread + self._spacing
            flex_height = content_pp
            content_pr = self._spacing

        if self._direction == Direction.VERTICAL:
            flex_width, flex_height = flex_height, flex_width

        self._layout_cache = Layout(layout_items, flex_width, flex_height)
        return self._layout_cache

    def draw(self, canvas: skia.Canvas, x: float, y: float, width: float, height: float) -> None:
        x += self._x + self._left_padding + self._left_margin
        y += self._y + self._top_padding + self._top_margin

        width = self._width or width - self._left_margin - self._left_margin
        height = self._height or height - self._top_margin - self._bottom_margin

        layout = self._get_layout(width, height)

        if self._background:
            canvas.drawRect(
                skia.Rect.MakeXYWH(x, y, layout.width, layout.height),  # noqa
                skia.Paint(Color=self._background.as_skia_color()),  # noqa
            )

        for layout_item in layout.items:
            layout_item.view.draw(canvas, x + layout_item.x, y + layout_item.y, layout_item.width, layout_item.height)

    def get_bounding_rect(self) -> Rect:
        view_width = self._width or 500
        view_height = self._height or 500
        layout = self._get_layout(view_width, view_height)

        return Rect(
            x=0,
            y=0,
            width=self._left_margin + layout.width + self._right_margin,
            height=self._top_margin + layout.height + self._bottom_margin,
        )

    def _direction_choice(self, horizontal_choice, vertical_choice):
        if self._direction == Direction.HORIZONTAL:
            return horizontal_choice
        else:
            return vertical_choice

    def _get_advance(self, view_width: float, view_height: float) -> float:
        """
        Returns the advance of a view down the axis.
        This would be width if direction is horizontal and height if direction is vertical.
        """
        return self._direction_choice(
            horizontal_choice=view_width,
            vertical_choice=view_height,
        )

    def _get_spread(self, view_width: float, view_height: float) -> float:
        """
        Returns the spread of a view around the axis.
        This would be height if direction is horizontal and width if direction is vertical.
        """
        return self._direction_choice(
            horizontal_choice=view_height,
            vertical_choice=view_width,
        )

    # Properties

    def align(self, alignment) -> Flex:
        self._alignment = alignment
        return self

    def justify(self, justify) -> Flex:
        self._justify = justify
        return self

    def direction(self, direction) -> Flex:
        self._direction = direction
        return self

    def horizontal(self) -> Flex:
        self._direction = Direction.HORIZONTAL
        return self

    def vertical(self) -> Flex:
        self._direction = Direction.VERTICAL
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
        if view not in self._children:
            raise RuntimeError('Flex.grow() can only accept children.')
        self._grow[view] = priority
        return self

    def background(self, color: Color) -> Flex:
        self._background = color
        return self

    def debug(self):
        self.__debug = True
        return self


@dataclasses.dataclass
class LayoutItem:
    view: View
    x: float
    y: float
    width: float
    height: float


@dataclasses.dataclass
class Layout:
    items: List[LayoutItem]
    width: float
    height: float
