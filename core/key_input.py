import weakref

from .base import View
from .singleton import Singleton


class Keys:
    BACKSPACE = 259
    ARROW_RIGHT = 262
    ARROW_LEFT = 263
    LEFT_SHIFT = 340
    RIGHT_SHIFT = 344


class KeyListener:
    def handle_char(self, char: str):
        pass

    def handle_key(self, key: int, action: int):
        pass


class KeyInput(metaclass=Singleton):
    __slots__ = ('__listeners', )

    def __init__(self):
        self.__listeners = weakref.WeakSet()

    def char_callback(self, window, codepoint: int):
        for instance in self.__listeners:
            instance.handle_char(chr(codepoint))

    def key_callback(self, window, key: int, scancode: int, action: int, mods: int):
        for instance in self.__listeners:
            instance.handle_key(key, action)

    def add_listener(self, listener: View):
        self.__listeners.add(listener)
