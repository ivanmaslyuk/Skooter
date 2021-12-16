import dataclasses
import weakref
from typing import Optional, List, Dict, Callable

import skia

CONTAINER_STACK = []
HOVER_MATRIX = []
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

    def draw(self, canvas: skia.Canvas, x: float, y: float, width: float, height: float):
        draw_method = self.__get_private_property('draw')
        draw_method(canvas, x, y, width, height)


class View:
    __slots__ = (
        'private', 'parent', '_children', '_x', '_y', '_width', '_height', '_top_margin',
        '_right_margin', '_bottom_margin', '_left_margin', '_top_padding', '_right_padding',
        '_bottom_padding', '_left_padding', '__context_properties', '__weakref__', '__on_hover',
        '__on_click', '__picture', '__body',
    )

    def __init__(self):
        print('INIT VIEW')
        self.private = ViewPrivate(self)
        self.parent: View = CONTAINER_STACK[-1] if CONTAINER_STACK else None
        if self.parent:
            self.parent.append_child(self)

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
        self.__picture: Optional[skia.Picture] = None

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
        if self.__picture:
            self.__picture.playback(canvas)  # noqa
            return

        # self.__add_to_hover_matrix(x, y, width, height)
        old_children: List[View] = self._children
        self._children = []
        if not self.__body:
            with self:
                self.__body: Optional[View] = self.body()

        picture_recorder = skia.PictureRecorder()
        recorder_canvas = picture_recorder.beginRecording(width, height)
        if self.__body is None:
            self._children = old_children
            self.paint(recorder_canvas, x + self._x, y + self._y, width, height)
        else:
            if not issubclass(type(self.__body), View):
                raise Exception('body() method must return a View.')
            self.__body.draw(recorder_canvas, x + self._x, y + self._y, width, height)
        self.__picture = picture_recorder.finishRecordingAsPicture()
        self.__picture.playback(canvas)

        self.draw_children(canvas, x + self._x, y + self._y, width, height)
        # self.invalidate_cache()  # todo fixme delete!!!!!!

    def __add_to_hover_matrix(self, x: float, y: float, width: float, height: float):
        for row in range(int(x), int(x) + int(height)):
            for col in range(int(y), int(y) + int(width)):
                try:
                    HOVER_MATRIX[row][col] = weakref.ref(self)
                except IndexError:
                    print('err', f'x={x}, y={y}, w={width}, h={height},'
                                 f' row={row}, col={col}')
                    print(f'{self}     w={int(x) + int(width)}, h={int(y) + int(height)}')
                    print(f'arr h={HOVER_MATRIX} w={HOVER_MATRIX[0]}')
                    raise
        if self.__on_hover or self.__on_click:
            pass


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

    def invalidate_cache(self, recursive: bool = False):
        self.__picture = None
        if recursive:
            for child in self._children:
                child.invalidate_cache(recursive=True)

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
