import contextlib
import glfw
import skia
from OpenGL import GL

WIDTH, HEIGHT = 640, 480


@contextlib.contextmanager
def glfw_window():
    if not glfw.init():
        raise RuntimeError('glfw.init() failed')
    glfw.window_hint(glfw.STENCIL_BITS, 8)
    window = glfw.create_window(WIDTH, HEIGHT, '', None, None)
    glfw.make_context_current(window)
    yield window
    glfw.terminate()


@contextlib.contextmanager
def skia_surface(window):
    context = skia.GrDirectContext.MakeGL()
    backend_render_target = skia.GrBackendRenderTarget(
        WIDTH,
        HEIGHT,
        0,  # sampleCnt
        0,  # stencilBits
        skia.GrGLFramebufferInfo(0, GL.GL_RGBA8))
    surface = skia.Surface.MakeFromBackendRenderTarget(
        context, backend_render_target, skia.kBottomLeft_GrSurfaceOrigin,
        skia.kRGBA_8888_ColorType, skia.ColorSpace.MakeSRGB())
    assert surface is not None
    yield surface
    context.abandonContext()


class App:
    def __init__(self, root_view):
        self.root_view = root_view

    def execute(self):
        with glfw_window() as window:
            GL.glClear(GL.GL_COLOR_BUFFER_BIT)

            with skia_surface(window) as surface:
                with surface as canvas:
                    self.root_view.draw(canvas, 0, 0)
                surface.flushAndSubmit()
                glfw.swap_buffers(window)

                while glfw.get_key(window, glfw.KEY_ESCAPE) != glfw.PRESS and not glfw.window_should_close(window):
                    glfw.wait_events()
