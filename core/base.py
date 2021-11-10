import dataclasses
from typing import Optional

import skia

CONTAINER_STACK = []


@dataclasses.dataclass
class Rect:
    x: float
    y: float
    width: float
    height: float


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

    def draw(self, canvas: skia.Canvas, x: float, y: float, width: float, height: float):
        self._children *= 0
        with self:
            body: Optional[View] = self.body()
        if not body:
            raise NotImplementedError('Views that inherit from View must implement body() or override draw().')

        if not issubclass(type(body), View):
            raise Exception('body() method must return a View.')

        body.draw(canvas, x + self._x, y + self._y, width, height)

        self.draw_children(canvas, x + self._x, y + self._y, width, height)

    def draw_children(self, canvas: skia.Surface, x: float, y: float, width: float, height: float):
        for view in self._children:
            view.draw(canvas, x, y, width, height)

    def children(self, *views):
        self._children = views
        return self

    def clicked(self, handler):
        self._clicked = handler
        return self

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
        if v is not None and h is None:
            self._top_margin = self._right_margin = self._bottom_margin = self._left_margin = v
        elif v is not None and h is not None:
            self._top_margin = self._bottom_margin = v
            self._right_margin = self._left_margin = h
        else:
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
        if v is not None and h is None:
            self._top_padding = self._right_padding = self._bottom_padding = self._left_padding = v
        elif v is not None and h is not None:
            self._top_padding = self._bottom_padding = v
            self._right_padding = self._left_padding = h
        else:
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
