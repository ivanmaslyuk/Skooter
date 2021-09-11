import time

import glfw
import skia
from OpenGL import GL


class App:
    def __init__(self, root_view, window_width=640, window_height=480, window_title='Window'):
        self.root_view = root_view
        self.window_width = window_width
        self.window_height = window_height
        self.window_title = window_title
        self._scaled = False
        self.glfw_window = None
        self.surface = None
        self.context = None

    def draw(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        with self.surface as canvas:
            if not self._scaled:
                canvas.scale(*glfw.get_window_content_scale(self.glfw_window))
                self._scaled = True
            start_time = time.time()
            self.root_view.draw(canvas, 0, 0, self.window_width, self.window_height)
            # print('Draw time:', round((time.time() - start_time) * 1000, 5), 'ms')
        self.surface.flushAndSubmit()
        glfw.swap_buffers(self.glfw_window)

    def mouse_pos_callback(self, window, x: float, y: float):
        if not (0 < x < self.window_width and 0 < y < self.window_height):
            return

        # if 50 < x < 100 and 50 < y < 100:
        #     glfw.set_cursor(window, glfw.create_standard_cursor(glfw.HAND_CURSOR))
        # else:
        #     glfw.set_cursor(window, None)

    def mouse_button_callback(self, window, button, action, mods):
        pass

    def create_glfw_window(self):
        if not glfw.init():
            raise RuntimeError('glfw.init() failed')
        glfw.window_hint(glfw.STENCIL_BITS, 8)
        self.glfw_window = glfw.create_window(self.window_width, self.window_height, self.window_title, None, None)
        glfw.make_context_current(self.glfw_window)

    def window_size_callback(self, window, width, height):
        self.window_width = width
        self.window_height = height
        self.create_skia_surface()
        self.draw()

    def create_skia_surface(self):
        if self.surface:
            self.context.abandonContext()
            self._scaled = False
        self.context = skia.GrDirectContext.MakeGL()
        width_scale, height_scale = glfw.get_window_content_scale(self.glfw_window)
        backend_render_target = skia.GrBackendRenderTarget(
            int(self.window_width * width_scale),
            int(self.window_height * height_scale),
            0,  # sampleCnt
            0,  # stencilBits
            skia.GrGLFramebufferInfo(0, GL.GL_RGBA8)
        )
        self.surface = skia.Surface.MakeFromBackendRenderTarget(
            self.context,
            backend_render_target,
            skia.kBottomLeft_GrSurfaceOrigin,
            skia.kRGBA_8888_ColorType,
            skia.ColorSpace.MakeSRGB()
        )
        assert self.surface is not None

    def execute(self):
        try:
            self.create_glfw_window()
            self.create_skia_surface()
            GL.glClearColor(255, 255, 255, 255)

            glfw.set_window_size_callback(self.glfw_window, self.window_size_callback)
            glfw.set_cursor_pos_callback(self.glfw_window, self.mouse_pos_callback)
            glfw.set_mouse_button_callback(self.glfw_window, self.mouse_button_callback)

            window_should_close = glfw.window_should_close(self.glfw_window)
            while glfw.get_key(self.glfw_window, glfw.KEY_ESCAPE) != glfw.PRESS and not window_should_close:
                self.draw()
                glfw.wait_events()
        finally:
            if self.surface:
                self.context.abandonContext()
            glfw.terminate()
