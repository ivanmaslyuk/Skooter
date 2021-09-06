import contextlib
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

    def draw(self, window, surface):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        with surface as canvas:
            canvas.scale(*glfw.get_window_content_scale(window))
            start_time = time.time()
            self.root_view.draw(canvas, 0, 0, self.window_width, self.window_height)
            print('Draw time:', round((time.time() - start_time) * 1000, 5), 'ms')
        surface.flushAndSubmit()
        glfw.swap_buffers(window)

    # def window_size_callback(self, window, surface):
    #     def func(window, width, height):
    #         self.

    @contextlib.contextmanager
    def skia_surface(self, window):
        context = skia.GrDirectContext.MakeGL()
        width_scale, height_scale = glfw.get_window_content_scale(window)
        backend_render_target = skia.GrBackendRenderTarget(
            int(self.window_width * width_scale),
            int(self.window_height * height_scale),
            0,  # sampleCnt
            0,  # stencilBits
            skia.GrGLFramebufferInfo(0, GL.GL_RGBA8)
        )
        surface = skia.Surface.MakeFromBackendRenderTarget(
            context,
            backend_render_target,
            skia.kBottomLeft_GrSurfaceOrigin,
            skia.kRGBA_8888_ColorType,
            skia.ColorSpace.MakeSRGB()
        )
        assert surface is not None
        yield surface
        context.abandonContext()

    @contextlib.contextmanager
    def glfw_window(self):
        if not glfw.init():
            raise RuntimeError('glfw.init() failed')
        glfw.window_hint(glfw.STENCIL_BITS, 8)
        window = glfw.create_window(self.window_width, self.window_height, self.window_title, None, None)
        glfw.make_context_current(window)
        yield window
        glfw.terminate()

    def execute(self):
        with self.glfw_window() as window:
            GL.glClearColor(255, 255, 255, 255)

            with self.skia_surface(window) as surface:
                print(dir(surface))
                def window_size_callback(_, width, height):
                    width_scale, height_scale = glfw.get_window_content_scale(window)
                    surface.width = int(self.window_width * width_scale)
                    self.window_width = width
                    self.window_height = height
                    self.draw(window, surface)
                glfw.set_window_size_callback(window, window_size_callback)

                while glfw.get_key(window, glfw.KEY_ESCAPE) != glfw.PRESS and not glfw.window_should_close(window):
                    self.draw(window, surface)
                    glfw.wait_events()
