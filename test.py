import random
from typing import Optional

from core.app import App
from core.color import Color
from core.data import State, ContextProperty
from core.key_input import KeyInput, KeyListener
from views import Rectangle, Text, Image, Flex, Input
from views.enums import Justify, Alignment
from core.base import View


class Button(View):
    hovered = State(False)
    pressed = State(False)

    def __init__(self, text):
        super().__init__()
        self.text = text
        self.on_hover(self.handle_hover)
        self.on_press(self.handle_press)

    def handle_hover(self, over: bool):
        self.hovered = over

    def handle_press(self, pressed: bool):
        self.pressed = pressed

    def body(self):
        background_color = Color.blue()
        if self.hovered:
            background_color = Color('#0000aa')
        if self.pressed:
            background_color = Color('#000077')
        with Flex().align('center').justify('center').background(background_color) as root:
            Text(self.text).color(Color.white()).height(40)
        return root


class Buttons(View):
    def body(self):
        with Flex().wrap(True).justify(Justify.SPACE_BETWEEN).padding(4) as root:
            for index in range(20):
                Button(f'Button {index + 1}')
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
                Button('Send')

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
    text = State("hello")

    def body(self):
        with Flex().padding(50).vertical() as root:
            Input(self.binding('text'))
            Text(f'text: {self.text}')
        return root


class TestFlex(View, KeyListener):
    text = State('initial')
    hovered = State(False)

    __key_input: KeyInput = ContextProperty()

    def __init__(self):
        super().__init__()
        self.__key_input.add_listener(self)

    def body(self) -> Optional[View]:
        with Flex().vertical().background(Color('#eee')).margin(12, 16) as root:
            Rectangle(50, 50).background(Color.red()).radius(4)
            Rectangle(100, 100).margin(top=20).background(
                Color.green() if self.hovered else Color.black()
            ).radius(4).on_hover(self.hover)
            Text(self.text)
        return root

    def handle_char(self, char: str):
        self.text = char

    def hover(self, over):
        self.hovered = over


class TestFlexWrapper(View):
    def body(self) -> Optional['View']:
        return TestFlex()


class ReactiveTest(View):
    number = State(0)

    def body(self) -> 'View':
        with Flex() as root:
            Text(self.binding('number'))
            Button("Increment").on_click(self.button_clicked)
        return root

    def button_clicked(self):
        self.number += 1


if __name__ == '__main__':
    app = App(InputTest(), window_width=500, window_height=500)
    app.execute()
