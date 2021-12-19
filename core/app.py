import time
import gc
from typing import Optional

import glfw
import skia
from OpenGL import GL

from .singleton import Singleton
from .key_input import KeyInput
from .base import View, HOVER_MATRIX, HOVER_STACK


def get_hovered_view(x: float, y: float) -> Optional[View]:
    for hover_item in HOVER_STACK:
        x_overlaps = hover_item['min_x'] <= x <= hover_item['max_x']
        y_overlaps = hover_item['min_y'] <= y <= hover_item['max_y']
        view = hover_item['view']
        if x_overlaps and y_overlaps and view.private.handles_hover:
            return view
    return None


class App(metaclass=Singleton):
    def __init__(self, root_view: View, window_width=640, window_height=480, window_title='Window'):
        self.key_input = KeyInput()
        self.root_view: View = root_view.context(self.key_input)
        self.window_width = window_width
        self.window_height = window_height
        self.window_title = window_title
        self.glfw_window = None
        self.surface = None
        self.context = None
        self.hovered_view: Optional[View] = None
        self.pressed_view: Optional[View] = None

    def draw(self):
        HOVER_STACK.clear()
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        with self.surface as canvas:
            start_time = time.time()
            self.root_view.draw(canvas, 0, 0, self.window_width, self.window_height)
            # print('Draw time:', round((time.time() - start_time) * 1000, 5), 'ms')
            canvas.flush()

        gc.collect()
        self.context.flush()
        glfw.swap_buffers(self.glfw_window)

        mouse_x, mouse_y, = glfw.get_cursor_pos(self.glfw_window)
        self.__update_hovered_view(mouse_x, mouse_y)

    def __update_hovered_view(self, mouse_x: int, mouse_y: int):
        if not (0 < mouse_x < self.window_width and 0 < mouse_y < self.window_height):
            self.hovered_view = None
            return

        hovered_view = get_hovered_view(mouse_x, mouse_y)
        if self.hovered_view == hovered_view:
            return

        if self.hovered_view is not None:
            self.hovered_view.private.handle_hover(over=False)

        self.hovered_view = hovered_view
        if hovered_view is not None:
            hovered_view.private.handle_hover(over=True)

    def __mouse_pos_callback(self, window, x: int, y: int):
        self.__update_hovered_view(x, y)

    def __mouse_button_callback(self, window, button, action, mods):
        # Left click
        if button == 0 and action == 0 and self.hovered_view:
            self.hovered_view.private.handle_click()
            self.pressed_view.private.handle_press(pressed=False)
            self.pressed_view = None
        elif button == 0 and action == 1 and self.hovered_view:
            self.hovered_view.private.handle_press(pressed=True)
            self.pressed_view = self.hovered_view

    def create_glfw_window(self):
        if not glfw.init():
            raise RuntimeError('glfw.init() failed')
        glfw.window_hint(glfw.STENCIL_BITS, 8)
        self.glfw_window = glfw.create_window(self.window_width, self.window_height, self.window_title, None, None)
        glfw.make_context_current(self.glfw_window)

    def window_size_callback(self, window, width, height):
        # self.root_view.invalidate_cache(recursive=True)
        self.window_width = width
        self.window_height = height
        # self.resize_hover_matrix() todo
        self.create_skia_surface()
        self.draw()

    def create_skia_surface(self):
        if self.surface:
            del self.surface

        width_scale, height_scale = glfw.get_window_content_scale(self.glfw_window)
        backend_render_target = skia.GrBackendRenderTarget(
            int(self.window_width * width_scale),
            int(self.window_height * height_scale),
            0,  # sampleCnt
            0,  # stencilBits
            skia.GrGLFramebufferInfo(0, GL.GL_RGBA8),
        )
        GL.glViewport(0, 0, int(self.window_width * width_scale), int(self.window_height * height_scale))
        self.surface = skia.Surface.MakeFromBackendRenderTarget(
            self.context,
            backend_render_target,
            skia.kBottomLeft_GrSurfaceOrigin,
            skia.kRGBA_8888_ColorType,
            skia.ColorSpace.MakeSRGB(),
        )
        assert self.surface is not None

        self.surface.getCanvas().scale(*glfw.get_window_content_scale(self.glfw_window))

    # def resize_hover_matrix(self):
    #     HOVER_MATRIX.clear()
    #     for _ in range(self.window_height):
    #         column = [None] * self.window_width
    #         HOVER_MATRIX.append(column)

    def execute(self):
        try:
            # self.resize_hover_matrix()
            self.create_glfw_window()
            self.context = skia.GrDirectContext.MakeGL()
            self.create_skia_surface()
            GL.glClearColor(255, 255, 255, 255)

            glfw.set_window_size_callback(self.glfw_window, self.window_size_callback)
            glfw.set_cursor_pos_callback(self.glfw_window, self.__mouse_pos_callback)
            glfw.set_mouse_button_callback(self.glfw_window, self.__mouse_button_callback)
            glfw.set_key_callback(self.glfw_window, self.key_input.key_callback)
            glfw.set_char_callback(self.glfw_window, self.key_input.char_callback)

            while not glfw.window_should_close(self.glfw_window):
                self.draw()
                glfw.wait_events()
        finally:
            if self.surface:
                self.context.abandonContext()
            glfw.terminate()
