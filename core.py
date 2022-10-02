from logger import LogManager
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton


"""
logging
"""

# create a logger
logging = LogManager(logfile_directory='./logger/log')
logger = logging.init_logger(name=__name__)

logging.remove_old_log_files(remaining=3)


"""
launcher
"""


class VisualSimulationsLauncher(QMainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setGeometry(0, 0, 854, 480)
        self.setWindowTitle('Visual Simulations Launcher')

        self.create_ui()

    def create_ui(self) -> None:
        widget = QWidget()
        vbox = QVBoxLayout(widget)
        vbox.setAlignment(Qt.AlignCenter)

        open_ts_window_btn = QPushButton('Texture Shaders', self)
        open_ts_window_btn.setMinimumWidth(200)
        open_ts_window_btn.setMinimumHeight(50)
        open_ts_window_btn.clicked.connect(self.open_ts_window)
        vbox.addWidget(open_ts_window_btn)

        open_sm_window_btn = QPushButton('Slime Mold Simulation', self)
        open_sm_window_btn.setMinimumWidth(200)
        open_sm_window_btn.setMinimumHeight(50)
        # open_sm_window_btn.clicked.connect()
        vbox.addWidget(open_sm_window_btn)

        open_mbs_window_btn = QPushButton('Mandelbrot Set', self)
        open_mbs_window_btn.setMinimumWidth(200)
        open_mbs_window_btn.setMinimumHeight(50)
        # open_mbs_window_btn.clicked.connect()
        vbox.addWidget(open_mbs_window_btn)

        self.setCentralWidget(widget)

    @staticmethod
    def open_ts_window() -> None:
        from texture_shader_window import TextureShaderWindow
        TextureShaderWindow.run()


"""
executing
"""


if __name__ == '__main__':
    application = QApplication([])
    window = VisualSimulationsLauncher()
    window.show()
    application.exec()
