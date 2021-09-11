from core.app import App
from views import View, Rectangle, Text, HBox, VBox


class MyButton(View):
    def __init__(self, text):
        super().__init__()
        self.text = text

    def body(self):
        with Rectangle(80, 35).background('#00f') as root:
            Text(self.text).color('#fff')
        return root


class MyView(View):
    def body(self):
        with HBox().spacing(6).alignment(HBox.Alignment.END).wrap(True).justify(HBox.JustifyRule.SPACE_BETWEEN) as root:
            for index in range(20):
                MyButton(f'Button {index + 1}')
        return root


class Header(View):
    def body(self):
        with HBox().alignment(HBox.Alignment.CENTER).justify(HBox.JustifyRule.SPACE_BETWEEN) as root:
            with VBox().spacing(2):
                Text('My App').size(14)
                Text('Subtitle').size(10)

            Rectangle(50, 50).background('#800')
        return root


class SecondView(View):
    def body(self):
        with VBox().alignment(VBox.Alignment.CENTER) as root:
            Rectangle(50, 70).background('#f0f')
            Text('lol')
        return root


class TestView(View):
    def body(self):
        with HBox().alignment(HBox.Alignment.END) as root:
            Text('Hello world TestView')
            MyView()
        return root


app = App(TestView())
app.execute()
