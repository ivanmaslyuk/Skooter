import random
from typing import Optional

from core.app import App
from core.color import Color
from core.data import State, ContextProperty
from core.key_input import KeyInput, KeyListener
from views import Rectangle, Text, Image, Flex, Input
from views.enums import Justify, Alignment
from core.base import View


class MyButton(View):
    def __init__(self, text):
        super().__init__()
        self.text = text

    def body(self):
        # with Rectangle(80, 40).background(Color('#00f')).radius(4) as root:
        #     text = Text(self.text).color(Color.white())
        #     text_bounding_rect = text.get_bounding_rect()
        #     text.x(40 - text_bounding_rect.width / 2)
        #     text.y(20 - text_bounding_rect.height / 2)
        with Flex().align('center').justify('center').background(Color('#00f')) as root:
            Text(self.text).color(Color.white()).height(40)
        return root


class Buttons(View):
    def body(self):
        with Flex().wrap(True).justify(Justify.SPACE_BETWEEN).padding(4) as root:
            for index in range(20):
                MyButton(f'Button {index + 1}')
        return root


class Header(View):
    def body(self):
        with Flex().align(Alignment.CENTER).justify('space-between') as root:
            with Flex().vertical():
                Text('My App').size(14)
                Text('Subtitle').size(10)

            Rectangle(50, 50).background(Color('#800')).radius(25)
        return root


class RequestInfo(View):
    request_name = 'Request Name'
    query_params = [
        ('q', 'how to cook chicken'),
        ('dark_mode', 'on'),
        ('version', 'mobile'),
    ]

    def body(self):
        with Flex().vertical().padding(12, 16) as root:
            with Flex().justify('space-between'):
                Text(self.request_name)
                Text('Docs')

            with Flex().margin(12, 0).justify('space-between') as input_row:
                url_field = Rectangle(width=20, height=None).background(Color('#eee')).radius(4).margin(right=12)
                input_row.grow(url_field, 1)
                MyButton('Send')

            with Flex().vertical().background(Color('#eee')):
                for key, value in self.query_params:
                    with Flex() as query_params_row:
                        key_text = Text(key).margin(12)
                        query_params_row.grow(key_text, 1)

                        Rectangle(1, 30).background(Color('#999'))

                        value_text = Text(value).margin(12)
                        query_params_row.grow(value_text, 2)

        return root


class InputTest(View):
    over_input = False

    def body(self):
        with Flex().padding(50).vertical().background(Color.blue()) as root:
            Input('abcde').background(Color.red())
            Input('12345').on_click(self.handle_click).background(
                Color.red() if self.over_input else Color.black(),
            ).on_hover(self.hover_handler)
            Text('sample text SAMPLE TEXT').size(16).background(Color.green())
            # Rectangle(100, 100).background(Color.black()).on_hover(self.hover_handler)
        return root

    def hover_handler(self, over: bool):
        self.over_input = over

    def handle_click(self):
        print('input clicked!!!!!')


class TestFlex(View, KeyListener):
    text = State('initial')

    __key_input: KeyInput = ContextProperty()

    def __init__(self):
        super().__init__()
        self.__key_input.add_listener(self)

    def body(self) -> Optional[View]:
        with Flex().vertical().background(Color('#eee')).margin(12, 16).debug() as root:
            Rectangle(50, 50).background(Color.red()).radius(4)
            Rectangle(100, 100).margin(top=20).background(Color.green()).radius(4).opacity(0.1)
            Text(self.text)
        return root

    def handle_char(self, char: str):
        self.text = char


class TestFlexWrapper(View):
    def body(self) -> Optional['View']:
        return TestFlex()


if __name__ == '__main__':
    app = App(TestFlexWrapper(), window_width=500, window_height=500)
    app.execute()
