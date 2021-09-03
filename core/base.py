import dataclasses

import skia


@dataclasses.dataclass
class BoundingRect:
    x: float
    y: float
    width: float
    height: float


class View:
    _children = []
    _clicked = None
    _x = 0
    _y = 0

    def body(self):
        return None

    def draw(self, canvas: skia.Surface, x: float, y: float):
        body = self.body()
        if not body:
            raise NotImplementedError('Views that inherit from View must implement body() or override draw().')

        if not issubclass(type(body), View):
            raise Exception('body() method must return a View.')

        body.draw(canvas, x + self._x, y + self._y)

        self.draw_children(canvas, x + self._x, y + self._y)

    def draw_children(self, canvas: skia.Surface, x: float, y: float):
        for view in self._children:
            view.draw(canvas, x, y)

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

    def get_bounding_rect(self) -> BoundingRect:
        body = self.body()
        if not body:
            raise NotImplementedError('Override get_bounding_rect() when using custom draw() method.')

        if not issubclass(type(body), View):
            raise Exception('body() method must return a View.')

        return body.get_bounding_rect()
