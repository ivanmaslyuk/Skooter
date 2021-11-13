from core.app import App
from core.color import Color
from views import Rectangle, Text, Image, Flex
from views.enums import Justify, Alignment
from core.base import View


class MyButton(View):
    def __init__(self, text):
        super().__init__()
        self.text = text

    def body(self):
        with Rectangle(80, 40).background(Color('#00f')).radius(4) as root:
            text = Text(self.text).color('#fff')
            text_bounding_rect = text.get_bounding_rect()
            text.x(40 - text_bounding_rect.width / 2)
            text.y(20 - text_bounding_rect.height / 2)
        return root


class MyView(View):
    def body(self):
        with Flex().spacing(6).wrap(True).justify(Justify.SPACE_BETWEEN) as root:
            for index in range(20):
                MyButton(f'Button {index + 1}')
        return root


class Header(View):
    def body(self):
        with Flex().align(Alignment.CENTER).justify('space-between').spacing(8) as root:
            with Flex().vertical().spacing(2):
                Text('My App').size(14)
                Text('Subtitle').size(10)

            Rectangle(50, 50).background(Color('#800')).radius(25)
        return root


class RequestInfo(View):
    request_name = 'Request Name'

    def body(self):
        with Flex().vertical().padding(12, 16) as root:
            with Flex().justify('space-between'):
                Text(self.request_name)
                Text('Docs')

            with Flex().margin(12, 0).justify('space-between') as address_input:
                address_input.grow(
                    Rectangle(width=None, height=40).background(Color('#eee')).radius(4).margin(right=12),
                    1
                )
                MyButton('Send')
        return root


if __name__ == '__main__':
    app = App(RequestInfo(), window_width=500, window_height=500)
    app.execute()
