import dataclasses
from typing import Optional, List, Dict

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
        'parent', '_children', '_x', '_y', '_width', '_height', '_top_margin', '_right_margin',
        '_bottom_margin', '_left_margin', '_top_padding', '_right_padding', '_bottom_padding',
        '_left_padding', '__context_properties', '__weakref__', '__is_abandoned',
    )

    def __init__(self):
        self.parent: View = CONTAINER_STACK[-1] if CONTAINER_STACK else None
        if self.parent:
            self.parent.append_child(self)

        self._children: List[View] = []
        self._x: float = 0
        self._y: float = 0
        self._height: float = 0
        self._width: float = 0

        self._top_margin: float = 0
        self._right_margin: float = 0
        self._bottom_margin: float = 0
        self._left_margin: float = 0

        self._top_padding: float = 0
        self._right_padding: float = 0
        self._bottom_padding: float = 0
        self._left_padding: float = 0

        self.__context_properties: Dict[type, object] = {}

    def __enter__(self):
        CONTAINER_STACK.append(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        CONTAINER_STACK.pop()

    def get_context_property(self, property_type: type):
        return self.__context_properties.get(property_type)

    def append_child(self, child):
        self._children.append(child)

    def body(self) -> Optional['View']:
        return None

    def paint(self, canvas: skia.Canvas, x: float, y: float, width: float, height: float):
        pass

    def draw(self, canvas: skia.Canvas, x: float, y: float, width: float, height: float):
        old_children: List[View] = self._children
        self._children = []
        with self:
            body: Optional[View] = self.body()

        if body is None:
            self._children = old_children
            self.paint(canvas, x + self._x, y + self._y, width, height)
        else:
            if not issubclass(type(body), View):
                raise Exception('body() method must return a View.')

            body.draw(canvas, x + self._x, y + self._y, width, height)

        self.draw_children(canvas, x + self._x, y + self._y, width, height)

    def draw_children(self, canvas: skia.Surface, x: float, y: float, width: float, height: float):
        for view in self._children:
            view.draw(canvas, x, y, width, height)

    def get_children(self) -> List['View']:
        return self._children

    def get_bounding_rect(self) -> Rect:
        body: Optional[View] = self.body()
        if not body:
            raise NotImplementedError(
                'Override get_bounding_rect() when using custom draw() method.',
            )

        if not issubclass(type(body), View):
            raise Exception('body() method must return a View.')

        return body.get_bounding_rect()

    # Properties

    def context(self, value):
        self.__context_properties[value.__class__] = value
        return self

    def x(self, x):
        self._x = x
        return self

    def y(self, y):
        self._y = y
        return self

    def width(self, width):
        self._width = width
        return self

    def height(self, height):
        self._height = height
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
        self._top_margin = top or self._top_margin
        self._right_margin = right or self._right_margin
        self._bottom_margin = bottom or self._bottom_margin
        self._left_margin = left or self._left_margin
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
        self._top_padding = top or self._top_padding
        self._right_padding = right or self._right_padding
        self._bottom_padding = bottom or self._bottom_padding
        self._left_padding = left or self._left_padding
        return self
