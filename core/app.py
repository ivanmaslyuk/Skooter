import contextlib
import time

import glfw
import skia
from OpenGL import GL

WIDTH, HEIGHT = 640, 480
VIEW = None


def window_size_callback(window, width, height):
    """Accepts new window size in screen coordinates."""
    global WIDTH, HEIGHT
    WIDTH = width
    HEIGHT = height
    # print(width, height)
    draw(window, VIEW)


@contextlib.contextmanager
def glfw_window():
    if not glfw.init():
        raise RuntimeError('glfw.init() failed')
    glfw.window_hint(glfw.STENCIL_BITS, 8)
    window = glfw.create_window(WIDTH, HEIGHT, '', None, None)
    glfw.make_context_current(window)
    glfw.set_window_size_callback(window, window_size_callback)
    yield window
    glfw.terminate()


@contextlib.contextmanager
def skia_surface(window):
    context = skia.GrDirectContext.MakeGL()
    width_scale, height_scale = glfw.get_window_content_scale(window)
    backend_render_target = skia.GrBackendRenderTarget(
        int(WIDTH * width_scale),
        int(HEIGHT * height_scale),
        0,  # sampleCnt
        0,  # stencilBits
        skia.GrGLFramebufferInfo(0, GL.GL_RGBA8))
    surface = skia.Surface.MakeFromBackendRenderTarget(
        context, backend_render_target, skia.kBottomLeft_GrSurfaceOrigin,
        skia.kRGBA_8888_ColorType, skia.ColorSpace.MakeSRGB())
    assert surface is not None
    yield surface
    context.abandonContext()


def draw(window, view):
    with skia_surface(window) as surface:
        with surface as canvas:
            canvas.scale(*glfw.get_window_content_scale(window))
            start_time = time.time()
            view.draw(canvas, 0, 0, WIDTH, HEIGHT)
            # print('Draw time:', round((time.time() - start_time) * 1000, 5), 'ms')
        surface.flushAndSubmit()
        glfw.swap_buffers(window)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)


class App:
    def __init__(self, root_view):
        self.root_view = root_view
        global VIEW
        VIEW = self.root_view

    def execute(self):
        with glfw_window() as window:
            GL.glClearColor(255, 255, 255, 255)
            GL.glClear(GL.GL_COLOR_BUFFER_BIT)

            while glfw.get_key(window, glfw.KEY_ESCAPE) != glfw.PRESS and not glfw.window_should_close(window):
                draw(window, self.root_view)
                glfw.wait_events()
