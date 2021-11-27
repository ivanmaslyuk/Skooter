from .singleton import Singleton


class KeyInput(metaclass=Singleton):
    __instances = []

    def __init__(self):
        KeyInput.__instances.append(self)

    def handle_char(self, char: str):
        pass

    def handle_key(self, key: int, action: int):
        pass

    @staticmethod
    def key_callback(window, key: int, scancode: int, action: int, mods: int):
        pass

    @staticmethod
    def char_callback(window, codepoint: int):
        for instance in KeyInput.__instances:
            instance.handle_char(chr(codepoint))
