from datetime import datetime
import configparser
import logging.config
from os import walk, remove
import pathlib
import moderngl as mgl
import moderngl_window as mgl_w
from moderngl_window.geometry import quad_fs
import imgui
import moderngl_window.integrations.imgui


"""
logging
"""


def delete_old_log_files() -> None:
    logfiles = list(filter(lambda file: file.endswith('.log'),
                           next(walk('./logging/log'), (None, None, []))[2]))
    if len(logfiles) > 3:
        for logfile in logfiles[0:len(logfiles) - 3]:
            remove(f'./logging/log/{logfile}')


# configure logger, manage .log files
logging.config.fileConfig(
    'logging/logging.ini',
    encoding='utf-8',
    defaults={
        'logfilename':
            f'./logging/log/{datetime.now().strftime("%Y-%m-%d_-_%H-%M-%S")}.log'
    }
)

delete_old_log_files()

logger = logging.getLogger(__name__)

# display output for ordinary cli:
#   print()
# report events (status monitoring, fault investigation):
#   logger.info() or
#   logger.debug() for detailed output
# issue warnings (particular runtime events):
#   issue is avoidable and the code should be modified:
#       warnings.warn()
#   the event should be noticed, but there is nothing you can do about it:
#       logger.warning()
# report errors (particular runtime events):
#   catch Error/
#   raise MostSpecificError()
# report suppressed errors without raising exceptions:
#   logger.error() or
#   logger.exception() or
#   logger.critical()


"""
config
"""

logger.info('Reading the config file...')
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')


class FormattedConfig:
    logger.info('Formatting data from the config file...')

    clr_fg_rgb = (
        float(config['color']['foreground_red']),
        float(config['color']['foreground_green']),
        float(config['color']['foreground_blue'])
    )
    clr_bg_rgb = (
        float(config['color']['background_red']),
        float(config['color']['background_green']),
        float(config['color']['background_blue'])
    )


"""
rendering and application window
"""


class VisualSimulationApp(mgl_w.WindowConfig):
    title = 'Visual Simulations'
    gl_version = (4, 3)

    window_size = (1440, 720)
    aspect_ratio = None

    resource_dir = (pathlib.Path(__file__).parent / 'resources').resolve()

    texture_dimensions = (1440, 720)
    group_size = (1, 1, 1)

    def __init__(self, **kwargs) -> None:
        """initialization"""
        super().__init__(**kwargs)

        # initialize imgui context
        imgui.create_context()
        # initialize a renderer for rendering the imgui elements in the moderngl-window window
        self.imgui_renderer = moderngl_window.integrations.imgui.ModernglWindowRenderer(self.wnd)

        # create a texture that represents our canvas as a grid with the dimensions map_size = (x, y)
        self.displayed_texture = self.ctx.texture(self.texture_dimensions, 4)
        self.displayed_texture.repeat_x, self.displayed_texture.repeat_y = False, False
        self.displayed_texture.filter = mgl.NEAREST, mgl.NEAREST    # weighted average of the four closest
        # texture elements

        # quad fragments
        self.quad_fs = quad_fs()

        # textured quad rendering
        self.texture_renderer = self.load_program(
            vertex_shader='vertex_shader.glsl',
            fragment_shader='fragment_shader.glsl'
        )

        # compute shader
        self.compute_shader = self.load_compute_shader(
            'compute_shader.glsl',
            defines={
                'destText': 0
            }
        )
        # clr_fg needs to be passed to the compute shader initially, because it is a uniform
        self.compute_shader['clr_fg'] = FormattedConfig.clr_fg_rgb

    # ----------
    # rendering
    # ----------

    def render(self, time: float, frame_time: float) -> None:
        """called every frame - render everything"""
        self.render_simulation_frame(time)
        self.render_ui_frame()

    # ----------
    # rendering: simulation
    # ----------

    def render_simulation_frame(self, time: float) -> None:
        """render the textures"""
        # clear screen (background color)
        self.ctx.clear(*FormattedConfig.clr_bg_rgb)

        # pass the time to the compute shader
        try:
            self.compute_shader['time'] = time
        except Exception as e:
            logger.exception(e)

        # automatically binds as a GL_R32F / r32f (read from the texture)
        self.displayed_texture.bind_to_image(0, read=True, write=True)
        # run the compute shader and let it compute a value for EVERY FUCKING PIXEL
        self.compute_shader.run(self.texture_dimensions[0], self.texture_dimensions[1], 1)

        # render texture
        self.displayed_texture.use(location=0)
        self.quad_fs.render(self.texture_renderer)

    # ----------
    # rendering: imgui ui
    # ----------

    def render_ui_frame(self) -> None:
        """create and render rhe ui"""
        # start new imgui frame context
        imgui.new_frame()

        # open new window context
        imgui.begin('COLORS')
        # ----------
        imgui.push_item_width(imgui.get_window_width() * 0.75)
        imgui.text('Foreground Color')
        imgui.begin_child('clr_fg', 0, 35, True)  # child region with border
        changed, FormattedConfig.clr_fg_rgb = imgui.color_edit3(
            "fg", *FormattedConfig.clr_fg_rgb
        )
        imgui.end_child()
        if changed:
            # pass new value to the compute shader
            self.compute_shader['clr_fg'] = FormattedConfig.clr_fg_rgb
        imgui.dummy(0, 5)  # spacing
        imgui.text('Background Color')
        imgui.begin_child('clr_bg', 0, 35, True)
        changed, FormattedConfig.clr_bg_rgb = imgui.color_edit3(
            "bg", *FormattedConfig.clr_bg_rgb
        )
        imgui.end_child()
        if changed:
            # pass new value to the compute shader
            # self.compute_shader['clr_bg'] = FormattedConfig.clr_bg_rgb
            pass
        imgui.pop_item_width()
        # ----------
        # close current window context
        imgui.end()

        # pass all drawing commands to the rendering pipeline:
        #   render imgui elements and display them in the moderngl-window window
        imgui.render()
        self.imgui_renderer.render(imgui.get_draw_data())
        # close imgui frame context
        imgui.end_frame()

    # ----------
    # ui events
    # ----------

    def mouse_position_event(self, x, y, dx, dy) -> None:
        """forward mouse_position_event to imgui"""
        self.imgui_renderer.mouse_position_event(x, y, dx, dy)

    def mouse_drag_event(self, x, y, dx, dy) -> None:
        """forward mouse_drag_event to imgui"""
        self.imgui_renderer.mouse_drag_event(x, y, dx, dy)

    def mouse_scroll_event(self, x_offset, y_offset) -> None:
        """forward mouse_scroll_event to imgui"""
        self.imgui_renderer.mouse_scroll_event(x_offset, y_offset)

    def mouse_press_event(self, x, y, button) -> None:
        """forward mouse_press_event to imgui"""
        self.imgui_renderer.mouse_press_event(x, y, button)

    def mouse_release_event(self, x: int, y: int, button: int) -> None:
        """forward mouse_release_event to imgui"""
        self.imgui_renderer.mouse_release_event(x, y, button)

    def unicode_char_entered(self, char) -> None:
        """forward unicode_char_entered to imgui"""
        self.imgui_renderer.unicode_char_entered(char)

    def resize(self, width: int, height: int) -> None:
        """forward resize event to imgui"""
        self.imgui_renderer.resize(width, height)

    def close(self):
        """write changes to the config file when the window is closed"""
        # prepare everything for being saved in the config file
        logger.info('Reformatting the data for the config file...')

        config['color']['foreground_red'], config['color']['foreground_green'], config['color']['foreground_blue'] = \
            str(FormattedConfig.clr_fg_rgb[0]), str(FormattedConfig.clr_fg_rgb[1]), str(FormattedConfig.clr_fg_rgb[2])
        config['color']['background_red'], config['color']['background_green'], config['color']['background_blue'] = \
            str(FormattedConfig.clr_bg_rgb[0]), str(FormattedConfig.clr_bg_rgb[1]), str(FormattedConfig.clr_bg_rgb[2])

        # write everything to the config file
        logger.info('Writing the reformatted data to the config file...')
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
            configfile.close()


"""
executing
"""


def main():
    """main function - executed when running the program"""
    logger.info('\n----------\nExecuting...\n----------')
    VisualSimulationApp.run()
    logger.info('\n----------\nStopping...\n----------')


if __name__ == '__main__':
    main()
