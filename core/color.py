from typing import Optional

import skia

from webcolors import hex_to_rgb


class Color:
    __slots__ = ('__red', '__green', '__blue')

    def __init__(self, *args):
        if len(args) == 1:
            hex_code = args[0]
            self.__red, self.__green, self.__blue = hex_to_rgb(hex_code)
        elif len(args) == 3:
            self.__red, self.__green, self.__blue = args
        else:
            raise RuntimeError('Unacceptable number of arguments given to Color()')

    def as_skia_color(self) -> skia.Color:
        return skia.Color(self.__red, self.__green, self.__blue)

    @classmethod
    def red(cls) -> 'Color':
        return cls(255, 0, 0)

    @classmethod
    def green(cls) -> 'Color':
        return cls(0, 255, 0)

    @classmethod
    def blue(cls) -> 'Color':
        return cls(0, 0, 255)
