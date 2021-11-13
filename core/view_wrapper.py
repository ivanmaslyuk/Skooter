from typing import List, Optional

import skia

from .base import View


class ViewWrapper:
    __slots__ = ('__view', '__parent', '__surface', '__children', )

    def __init__(self, view: View, parent: 'ViewWrapper' = None):
        self.__view: View = view
        self.__parent: ViewWrapper = parent
        self.__surface: Optional[skia.Surface] = None

        self.__children: List[ViewWrapper] = []
        for child_view in view.get_children():
            child_view.body()
            self.__children.append(ViewWrapper(child_view, parent=self))

    def draw(self, canvas, x, y, width, height):
        if self.__surface:
            self.__surface.draw(canvas)
            return

        self.create_surface()
        self.__view.draw(self.__surface.getCanvas(), x, y, width, height)
        self.__surface.draw(canvas)

    def redraw(self):
        self.__surface = None
        self.draw(canvas, x, y, width, height)

    def create_surface(self):
        self.__surface = skia.Surface(self.__view)
