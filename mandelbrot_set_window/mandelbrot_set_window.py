from logging import getLogger
from config import MandelbrotSetWindowConfig


"""
logging
"""


# create a logger
logger = getLogger(__name__)


"""
config
"""

# read and format the config
config = MandelbrotSetWindowConfig()


"""
rendering and gui
"""


class MandelbrotSetWindow:
    def __init__(self) -> None:
        pass

    def run(self) -> None:
        pass


if __name__ == '__main__':
    mandelbrot_set_window = MandelbrotSetWindow()
    mandelbrot_set_window.run()
