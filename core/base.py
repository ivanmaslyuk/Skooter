import dataclasses
import typing
from typing import Optional

import skia

from core import app

CONTAINER_STACK = []


@dataclasses.dataclass
class Rect:
    x: float
    y: float
    width: float
    height: float


class View:
    def __init__(self):
        self.parent: View = CONTAINER_STACK[-1] if CONTAINER_STACK else None
        if self.parent:
            self.parent.append_child(self)
        self._children: typing.List[View] = []
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

    def draw(self, canvas: skia.Canvas, x: float, y: float, width: float, height: float, env: app.Environment):
        self._children *= 0
        with self:
            body: Optional[View] = self.body()
        if not body:
            raise NotImplementedError('Views that inherit from View must implement body() or override draw().')

        if not issubclass(type(body), View):
            raise Exception('body() method must return a View.')

        body.draw(canvas, x + self._x, y + self._y, width, height, env)

        self.draw_children(canvas, x + self._x, y + self._y, width, height, env)

    def draw_children(
            self,
            canvas: skia.Surface,
            x: float,
            y: float,
            width: float,
            height: float,
            env: app.Environment,
    ):
        for view in self._children:
            view.draw(canvas, x, y, width, height, env)

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

    def margin(self, top, right=None, bottom=None, left=None):
        if top is not None and right is bottom is left is None:
            self._top_margin = self._right_margin = self._bottom_margin = self._left_margin = top
        elif top is not None and right is not None and bottom is left is None:
            self._top_margin = self._bottom_margin = top
            self._right_margin = self._left_margin = right
        else:
            self._top_margin = top
            self._right_margin = right
            self._bottom_margin = bottom
            self._left_margin = left
        return self

    def padding(self, top, right=None, bottom=None, left=None):
        if top is not None and right is bottom is left is None:
            self._top_padding = self._right_padding = self._bottom_padding = self._left_padding = top
        elif top is not None and right is not None and bottom is left is None:
            self._top_padding = self._bottom_padding = top
            self._right_padding = self._left_padding = right
        else:
            self._top_padding = top
            self._right_padding = right
            self._bottom_padding = bottom
            self._left_padding = left
        return self

    def get_bounding_rect(self) -> Rect:
        """Called by containers to lay out items in draw()."""

        body: Optional[View] = self.body()
        if not body:
            raise NotImplementedError('Override get_bounding_rect() when using custom draw() method.')

        if not issubclass(type(body), View):
            raise Exception('body() method must return a View.')

        return body.get_bounding_rect()
