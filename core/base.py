import dataclasses
from typing import Optional, List, Dict, Callable

import skia

from core.data import DataBinding, Binding

CONTAINER_STACK = []
HOVER_STACK = []


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


class Spacing:
    def __init__(self, top: float, right: float, bottom: float, left: float):
        self._top: float = top
        self._right: float = right
        self._bottom: float = bottom
        self._left: float = left

    @staticmethod
    def calculate(
        v: float = None,
        h: float = None,
        *,
        top: float = None,
        right: float = None,
        bottom: float = None,
        left: float = None,
    ) -> 'Spacing':
        if v is not None and h is None:
            return Spacing(v, v, v, v)
        elif v is not None and h is not None:
            return Spacing(v, h, v, h)
        else:
            return Spacing(top, right, bottom, left)

    @property
    def top(self):
        return self._top

    @property
    def right(self):
        return self._right

    @property
    def bottom(self):
        return self._bottom

    @property
    def left(self):
        return self._left


class ViewPrivate:
    def __init__(self, view: 'View'):
        self.__view = view

    def __get_private_property(self, name: str):
        return getattr(self.__view, f'_View__{name}')

    def handle_hover(self, over: bool):
        handler = self.__get_private_property('on_hover')
        if handler:
            handler(over)

    def handle_click(self):
        handler = self.__get_private_property('on_click')
        if handler:
            handler()

    def handle_press(self, pressed: bool):
        handler = self.__get_private_property('on_press')
        if handler:
            handler(pressed)

    @property
    def handles_hover(self) -> bool:
        return self.__get_private_property('on_hover') is not None

    def draw(self, canvas: skia.Canvas, x: float, y: float, width: float, height: float):
        draw_method = self.__get_private_property('draw')
        draw_method(canvas, x, y, width, height)


class View:
    __slots__ = (
        'private', 'parent', '_children', '_x', '_y', '_width', '_height', '_top_margin',
        '_right_margin', '_bottom_margin', '_left_margin', '_top_padding', '_right_padding',
        '_bottom_padding', '_left_padding', '__context_properties', '__weakref__', '__on_hover',
        '__on_click', '__body', '__on_press',
    )

    def __init__(self, **props):
        self.private = ViewPrivate(self)
        self.parent: View = CONTAINER_STACK[-1] if CONTAINER_STACK else None
        if self.parent:
            self.parent.append_child(self)

        self.__fill_props(props)
        self.__check_required_props_filled(props)

        self._children: List[View] = []
        self.__body: Optional[View] = None
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
        self.__on_hover: Optional[Callable[[bool], None]] = None
        self.__on_click: Optional[Callable[[], None]] = None
        self.__on_press: Optional[Callable[[], None]] = None

    def __enter__(self):
        CONTAINER_STACK.append(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        CONTAINER_STACK.pop()

    def get_context_property(self, property_type: type):
        return self.__context_properties.get(property_type)

    def append_child(self, child):
        self._children.append(child)

    def body(self) -> 'View':
        pass

    def paint(self, canvas: skia.Canvas, x: float, y: float, width: float, height: float):
        pass

    def binding(self, property_name: str) -> DataBinding:
        if property_name not in vars(self.__class__):
            raise RuntimeError(f'Cannot create binding for undefined property "{property_name}"')
        return DataBinding(self, property_name)

    def __binding_props(self) -> list:
        return [key for key, value in vars(self.__class__).items() if type(value) == Binding]

    def __fill_props(self, props):
        binding_props = self.__binding_props()
        for key, value in props.items():
            if key not in vars(self.__class__):
                raise RuntimeError(f'{self.__class__.__name__} received an unknown prop "{key}".')
            if key in binding_props:
                binding_descriptor: Binding = vars(self.__class__)[key]
                binding_descriptor.set_data_binding(self, value)

    def __check_required_props_filled(self, props):
        required_props = set()
        required_props.update(self.__binding_props())
        for required_prop in required_props:
            if required_prop not in props:
                raise RuntimeError(
                    f'Required prop "{required_prop}" was not passed to {self.__class__.__name__}',
                )

    def __fetch_body(self):
        if self.__body:
            return
        self._children = []
        with self:
            self.__body: Optional[View] = self.body()
        if self.__body is not None and not issubclass(type(self.__body), View):
            raise Exception('body() method must return a View.')

    @property
    def __overrides_body(self) -> bool:
        return 'body' in self.__class__.__dict__

    def draw(self, canvas: skia.Canvas, x: float, y: float, width: float, height: float):
        self.__add_to_hover_stack(x, y, width, height)
        if self.__overrides_body:
            self.__fetch_body()
            self.__body.draw(canvas, x + self._x, y + self._y, width, height)
        else:
            self.paint(canvas, x + self._x, y + self._y, width, height)

        self.draw_children(canvas, x + self._x, y + self._y, width, height)

    def __add_to_hover_stack(self, x, y, width, height):
        HOVER_STACK.insert(0, {
            'view': self,
            'min_x': x,
            'min_y': y,
            'max_x': x + width,
            'max_y': y + height,
        })

    def draw_children(self, canvas: skia.Surface, x: float, y: float, width: float, height: float):
        for view in self._children:
            view.draw(canvas, x, y, width, height)

    def get_children(self) -> List['View']:
        return self._children

    def get_bounding_rect(self) -> Rect:
        self.__fetch_body()
        if not self.__body:
            raise NotImplementedError(
                'Override get_bounding_rect() when overriding paint() method.',
            )

        return self.__body.get_bounding_rect()

    def invalidate_body(self):
        if not self.__overrides_body:
            return
        self.__body = None
        self._children = []

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
            left: float = None,
    ):
        top, right, bottom, left = calculate_spacings(  # noqa
            v,
            h,
            top=top,
            right=right,
            bottom=bottom,
            left=left,
        )
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
            left: float = None,
    ):
        top, right, bottom, left = calculate_spacings(  # noqa
            v,
            h,
            top=top,
            right=right,
            bottom=bottom,
            left=left,
        )
        self._top_padding = top or self._top_padding
        self._right_padding = right or self._right_padding
        self._bottom_padding = bottom or self._bottom_padding
        self._left_padding = left or self._left_padding
        return self

    def on_hover(self, handler: Callable[[bool], None]):
        self.__on_hover = handler
        return self

    def on_click(self, handler: Callable[[], None]):
        self.__on_click = handler
        return self

    def on_press(self, handler: Callable[[bool], None]):
        self.__on_press = handler
        return self
