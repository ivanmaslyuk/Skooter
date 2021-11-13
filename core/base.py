import dataclasses
from typing import Optional, List

import skia

CONTAINER_STACK = []


@dataclasses.dataclass
class Rect:
    x: float
    y: float
    width: float
    height: float


def calculate_spacings(
        v: float = None,
        h: float = None,
        *,
        top: float = None,
        right: float = None,
        bottom: float = None,
        left: float = None
    ):
    if v is not None and h is None:
        return v, v, v, v
    elif v is not None and h is not None:
        return v, h, v, h
    else:
        return top, right, bottom, left


class View:
    __slots__ = (
        'parent', '_children', '_x', '_y', '_top_margin', '_right_margin', '_bottom_margin', '_left_margin',
        '_top_padding', '_right_padding', '_bottom_padding', '_left_padding',
    )

    def __init__(self):
        self.parent: View = CONTAINER_STACK[-1] if CONTAINER_STACK else None
        if self.parent:
            self.parent.append_child(self)
        self._children = []
        self._x = 0
        self._y = 0

        self._top_margin = 0
        self._right_margin = 0
        self._bottom_margin = 0
        self._left_margin = 0

        self._top_padding = 0
        self._right_padding = 0
        self._bottom_padding = 0
        self._left_padding = 0

    def __enter__(self):
        CONTAINER_STACK.append(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        CONTAINER_STACK.pop()

    def append_child(self, child):
        self._children.append(child)

    def body(self):
        return None

    def paint(self, canvas: skia.Canvas, x: float, y: float, width: float, height: float):
        pass

    def draw(self, canvas: skia.Canvas, x: float, y: float, width: float, height: float):
        self._children = []
        with self:
            body: Optional[View] = self.body()

        if body is None:
            self.paint(canvas, x, y, width, height)
        else:
            if not issubclass(type(body), View):
                raise Exception('body() method must return a View.')

            body.draw(canvas, x + self._x, y + self._y, width, height)

        self.draw_children(canvas, x + self._x, y + self._y, width, height)

    def draw_children(self, canvas: skia.Surface, x: float, y: float, width: float, height: float):
        for view in self._children:
            view.draw(canvas, x, y, width, height)

    def x(self, x):
        self._x = x
        return self

    def y(self, y):
        self._y = y
        return self

    def margin(
            self,
            v: float = None,
            h: float = None,
            *,
            top: float = None,
            right: float = None,
            bottom: float = None,
            left: float = None
    ):
        top, right, bottom, left = calculate_spacings(v, h, top=top, right=right, bottom=bottom, left=left)
        if top is not None:
            self._top_margin = top
        if right is not None:
            self._right_margin = right
        if bottom is not None:
            self._bottom_margin = bottom
        if left is not None:
            self._left_margin = left
        return self

    def padding(
            self,
            v: float = None,
            h: float = None,
            *,
            top: float = None,
            right: float = None,
            bottom: float = None,
            left: float = None
    ):
        top, right, bottom, left = calculate_spacings(v, h, top=top, right=right, bottom=bottom, left=left)
        if top is not None:
            self._top_padding = top
        if right is not None:
            self._right_padding = right
        if bottom is not None:
            self._bottom_padding = bottom
        if left is not None:
            self._left_padding = left
        return self

    def get_bounding_rect(self) -> Rect:
        body: Optional[View] = self.body()
        if not body:
            raise NotImplementedError('Override get_bounding_rect() when using custom draw() method.')

        if not issubclass(type(body), View):
            raise Exception('body() method must return a View.')

        return body.get_bounding_rect()

    def get_children(self) -> List['View']:
        return self._children
