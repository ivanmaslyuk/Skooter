import random

from core.app import App
from views import View, Rectangle, Text, HBox, VBox


class MyButton(View):
    def __init__(self, text):
        self.text = text
        self.h = random.choice([30, 60, 80])
        self.w = random.choice([60, 80, 100])

    def body(self):
        return (
            Rectangle(width=self.w, height=self.h).children(
                Text(self.text).color('#fff')
            ).background('#f00')
        )


class MyView(View):
    def body(self):
        return (
            HBox(
                MyButton('Button 1'),
                MyButton('Button 2'),
                MyButton('Button 3'),
                MyButton('Button 4'),
                MyButton('Button 5'),
                MyButton('Button 6'),
                MyButton('Button 7'),
                MyButton('Button 8'),
                MyButton('Button 9'),
                MyButton('Button 10'),
                MyButton('Button 11'),
                Text('Hello world this is a library').color('#ffffff'),
                MyButton('Button 12'),
                MyButton('Button 13'),
                MyButton('Button 14'),
                MyButton('Button 15'),
                MyButton('Button 16'),
                MyButton('Button 17'),
                MyButton('Button 18'),
                MyButton('Кнопка 19'),
            ).spacing(6)
            .width(640)
            .height(480)
            .alignment(HBox.Alignment.END)
            .wrap(True)
            .justify(HBox.JustifyRule.SPACE_BETWEEN)
        )


class Header(View):
    def body(self):
        return (
            HBox(
                VBox(
                    Text('My App').color('#fff').size(14),
                    Text('Subtitle').color('#fff').size(10)
                ).spacing(6).children(
                    Rectangle(50, 50).background('#f0f').opacity(0.3)
                ),
                Rectangle(50, 50).background('#800')
            ).width(640).alignment(HBox.Alignment.CENTER).justify(HBox.JustifyRule.SPACE_BETWEEN)
        )


app = App(MyView())
app.execute()
