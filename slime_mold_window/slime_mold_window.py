from logging import getLogger
from config import SlimeMoldWindowConfig
import numpy
from pathlib import Path
from os import walk
import moderngl as mgl
from moderngl_window import WindowConfig
import moderngl_window.integrations.imgui
from moderngl_window.geometry import quad_fs
import imgui


"""
logging
"""


# inherit the logger from the parent
logger = getLogger(__name__)


"""
config
"""

# read and format the config
config = SlimeMoldWindowConfig()


"""
utility
"""


def generate_agent_data(agent_count: int = config.number_of_agents, dimensions: tuple = (1920, 1080)) -> numpy.array:
    # generate a list of x coordinates
    x = numpy.array([dimensions[0] / 2] * agent_count)  # TODO: all agents (slimes) will be spawned in the middle
    # generate a list of y coordinates
    y = numpy.array([dimensions[1] / 2] * agent_count)
    # generate a list of angles (unit: radians -> 2 * pi * random); random values range from 0.0 to 1.0
    angle = 2 * numpy.pi * numpy.random.random(agent_count)

    # translate slice objects to concatenation along the second axis:
    # array([[x, y, angle]
    #        [x, y, angle]
    #        [x, y, angle]
    #        [...]])
    return numpy.c_[x, y, angle]


"""
rendering and gui
"""


class SlimeMoldWindow(WindowConfig):
    title = 'Visual Simulations - Slime Mold Simulations'
    gl_version = (4, 3)

    window_size = (1440, 720)
    aspect_ratio = None

    resource_dir = (Path(__file__).parent / 'shader').resolve()
    # get a list of all the available shaders in the resource dir
    shader_dirs = list(next(walk(resource_dir), ([], None, None))[1])

    texture_dimensions = (720, 360)  # (1920, 1080)
    group_size = (1, 1)

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

        # create a buffer to store position and angle of every agent (slime)
        self.buffer_agent_data = self.ctx.buffer(
            data=generate_agent_data(
                config.number_of_agents,
                self.texture_dimensions
            ).astype('f4')
        )

        # quad fragments
        self.quad_fs = quad_fs()

        # textured quad rendering
        self.texture_renderer = self.load_program(
            vertex_shader=f'{config.most_recent_shader_directory}/vertex_shader.glsl',
            fragment_shader=f'{config.most_recent_shader_directory}/fragment_shader.glsl'
        )

        # blur compute shader
        self.blur_compute_shader = self.load_compute_shader(
            f'{config.most_recent_shader_directory}/blur_compute_shader.glsl',
            defines={
                'destText': 0
            }
        )
        # These values need to be passed to the compute shader initially, because they are uniforms
        self.blur_compute_shader['diffusion_speed'] = config.blur_diffusion_speed
        self.blur_compute_shader['evaporation_speed'] = config.blur_evaporation_speed

        # slime compute shader
        self.slime_compute_shader = self.load_compute_shader(
            f'{config.most_recent_shader_directory}/slime_compute_shader.glsl',
            defines={
                'destText': 0,
                'width': self.texture_dimensions[0],
                'height': self.texture_dimensions[1],
                'nOA': config.number_of_agents
            }
        )
        # These values need to be passed to the compute shader initially, because they are uniforms
        self.slime_compute_shader['clr_fg'] = config.clr_fg_rgb
        self.slime_compute_shader['movement_speed'] = config.slime_movement_speed
        # self.slime_compute_shader['rotation_speed'] = config.slime_rotation_speed
        # self.slime_compute_shader['sensor_distance'] = config.slime_sensor_distance
        # self.slime_compute_shader['sensor_angle'] = config.slime_sensor_angle
        # self.slime_compute_shader['sensor_size'] = config.slime_sensor_size

    # ----------
    # rendering
    # ----------

    def render(self, time: float, frame_time: float) -> None:
        """called every frame - render everything"""
        self.render_simulation_frame(frame_time)
        self.render_ui_frame()

    # ----------
    # rendering: simulation
    # ----------

    def render_simulation_frame(self, frame_time: float) -> None:
        """render the textures"""
        # clear screen (background color)
        self.ctx.clear(*config.clr_bg_rgb)

        # pass the frame time to the compute shader s
        try:
            self.slime_compute_shader['frame_time'] = frame_time
        except Exception as e:
            logger.exception(e)

        try:
            self.blur_compute_shader['frame_time'] = frame_time
        except Exception as e:
            logger.exception(e)

        # automatically binds as a GL_R32F / r32f (read from the texture)
        self.displayed_texture.bind_to_image(0, read=True, write=True)

        self.buffer_agent_data.bind_to_storage_buffer(1)

        # run the compute shaders and let them compute values for EVERY GODDAMN PIXEL
        # first blur the texture, then render the agents to display the agents at full brightness
        # TODO: implement group sizes
        self.blur_compute_shader.run(self.texture_dimensions[0], self.texture_dimensions[1])
        self.slime_compute_shader.run(self.texture_dimensions[0], self.texture_dimensions[1])

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
        if imgui.begin('COLORS'):
            imgui.push_item_width(imgui.get_window_width() * 0.75)  # max item with: 75% of the window from the left

            imgui.text('Foreground Color')
            imgui.begin_child('clr_fg', 0, 35, True)  # child region with border
            changed, config.clr_fg_rgb = imgui.color_edit3(
                "fg", *config.clr_fg_rgb
            )
            imgui.end_child()
            if changed:  # pass the new value to the compute shader
                self.slime_compute_shader['clr_fg'] = config.clr_fg_rgb

            imgui.dummy(0, 5)  # spacing

            imgui.text('Background Color')
            imgui.begin_child('clr_bg', 0, 35, True)
            changed, config.clr_bg_rgb = imgui.color_edit3(
                "bg", *config.clr_bg_rgb
            )
            imgui.end_child()

            imgui.pop_item_width()
            imgui.end()  # close current window context

        if imgui.begin('COMPUTE SHADERS'):
            imgui.push_item_width(imgui.get_window_width() * 0.75)

            visible = True
            expanded, visible = imgui.collapsing_header('Select a compute shader.', visible)
            if expanded:  # create a button for every available compute shader
                for shader_dir in self.shader_dirs:
                    if imgui.button(shader_dir, -1, 25):  # load the compute shader if the button is clicked
                        if config.most_recent_shader_directory != shader_dir:  # change the most recent shader dir
                            config.most_recent_shader_directory = shader_dir  # to the selected shader dir

                        # textured quad rendering
                        self.texture_renderer = self.load_program(
                            vertex_shader=f'{shader_dir}/vertex_shader.glsl',
                            fragment_shader=f'{shader_dir}/fragment_shader.glsl'
                        )

                        # blur compute shader
                        self.blur_compute_shader = self.load_compute_shader(
                            f'{config.most_recent_shader_directory}/blur_compute_shader.glsl',
                            defines={
                                'destText': 0
                            }
                        )

                        # compute shader
                        self.slime_compute_shader = self.load_compute_shader(
                            f'{shader_dir}/compute_shader.glsl',
                            defines={
                                'destText': 0
                            }
                        )
                        # clr_fg needs to be passed to the compute shader initially, because it is a uniform
                        self.slime_compute_shader['clr_fg'] = config.clr_fg_rgb

            imgui.pop_item_width()
            imgui.end()

        # TODO: blur and slime shader uniforms

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
        config.save()


if __name__ == '__main__':
    SlimeMoldWindow.run()
