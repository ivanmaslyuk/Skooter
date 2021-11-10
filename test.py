from core.app import App
from core.color import Color
from views import Rectangle, Text, HBox, VBox, Image, Flex
from views.enums import Justify, Alignment
from core.base import View


class MyButton(View):
    def __init__(self, text):
        super().__init__()
        self.text = text

    def body(self):
        with Rectangle(80, 40).background('#00f').radius(4) as root:
            text = Text(self.text).color('#fff')
            text_bounding_rect = text.get_bounding_rect()
            text.x(40 - text_bounding_rect.width / 2)
            text.y(20 - text_bounding_rect.height / 2)
        return root


class MyView(View):
    def body(self):
        with HBox().spacing(6).wrap(True).justify(Justify.SPACE_BETWEEN) as root:
            for index in range(20):
                MyButton(f'Button {index + 1}')
        return root


class Header(View):
    def body(self):
        with HBox().alignment(Alignment.CENTER).justify(Justify.SPACE_BETWEEN).spacing(8) as root:
            with VBox().spacing(2):
                Text('My App').size(14)
                Text('Subtitle').size(10)

            Rectangle(50, 50).background('#800').radius(25)
        return root


class RequestInfo(View):
    request_name = 'Request Name'

    def body(self):
        with Flex().vertical().padding(12, 16) as root:
            with Flex().justify('space-between'):
                Text(self.request_name)
                Text('Docs')

            with Flex().margin(12, 0).justify('space-between') as address_input:
                address_field = Rectangle(width=300, height=40).background('#eee').radius(4).margin(right=12)
                address_input.grow(address_field, 1)
                MyButton('Send')

            Image('sample_image.png', 200, 200)
        return root


class SimpleView(View):
    def body(self):
        with Rectangle() as root:
            Text('Request Name').x(16).y(12)
            Text('Docs').x(350).y(12)

            Rectangle(width=300, height=40).background('#eee').radius(4).x(16).y(50)
            MyButton('Send').x(324).y(50)

            Image('sample_image.png', 200, 200).x(16).y(100)
        return root


if __name__ == '__main__':
    app = App(RequestInfo(), window_width=500, window_height=500)
    app.execute()
