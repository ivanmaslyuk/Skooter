from core.app import App
from views import View, Rectangle, Text, HBox, VBox, Image, Justify, Alignment


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
        with VBox().padding(12, 16) as root:
            with HBox().justify('space-between'):
                Text(self.request_name)
                Text('Docs')

            with HBox().justify('space-between').margin(12, 0, 0, 0):
                Rectangle(width=300, height=40).background('#eee').radius(4)
                MyButton('Send')

            Image('sample_image.png').width(200).height(200)
        return root


app = App(RequestInfo(), window_width=500, window_height=500)
app.execute()
