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
    def __init__(self):
        self.parent: View = CONTAINER_STACK[-1] if CONTAINER_STACK else None
        if self.parent:
            self.parent.append_child(self)
        self._children = []
        self._x = 0
        self._y = 0

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

    def get_bounding_rect(self) -> Rect:
        body: Optional[View] = self.body()
        if not body:
            raise NotImplementedError('Override get_bounding_rect() when using custom draw() method.')

        if not issubclass(type(body), View):
            raise Exception('body() method must return a View.')

        return body.get_bounding_rect()
