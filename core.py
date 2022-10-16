from logger import LogManager
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton
from multiprocessing import Process

from texture_shader_window import TextureShaderWindow
from slime_mold_window import SlimeMoldWindow
from mandelbrot_set_window import MandelbrotSetWindow


"""
logging
"""

# create a logger
logging = LogManager(logfile_directory='./logger/log')
logger = logging.init_logger(name=__name__)

logging.remove_old_log_files(remaining=3)


"""
application as global variable
"""
application = QApplication([])


"""
launcher
"""


class VisualSimulationsLauncher(QMainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.subprocess = None

        self.setGeometry(0, 0, 854, 480)
        self.setWindowTitle('Visual Simulations Launcher')

        self.create_ui()

    def create_ui(self) -> None:
        self.widget = QWidget()
        self.vbox = QVBoxLayout(self.widget)
        self.vbox.setAlignment(Qt.AlignCenter)

        self.open_ts_window_btn = QPushButton('Texture Shaders', self)
        self.open_ts_window_btn.setMinimumWidth(200)
        self.open_ts_window_btn.setMinimumHeight(50)
        self.open_ts_window_btn.clicked.connect(self.open_ts_window)
        self.vbox.addWidget(self.open_ts_window_btn)

        self.open_sm_window_btn = QPushButton('Slime Mold Simulation', self)
        self.open_sm_window_btn.setMinimumWidth(200)
        self.open_sm_window_btn.setMinimumHeight(50)
        self.open_sm_window_btn.clicked.connect(self.open_sm_window)
        self.vbox.addWidget(self.open_sm_window_btn)

        self.open_mbs_window_btn = QPushButton('Mandelbrot Set', self)
        self.open_mbs_window_btn.setMinimumWidth(200)
        self.open_mbs_window_btn.setMinimumHeight(50)
        self.open_mbs_window_btn.clicked.connect(self.open_mbs_window)
        self.vbox.addWidget(self.open_mbs_window_btn)

        self.setCentralWidget(self.widget)

    def open_ts_window(self) -> None:
        if self.subprocess:
            self.subprocess.terminate()

            if self.subprocess.name == 'smw':
                self.open_sm_window_btn.setText('Slime Mold Simulation')
                self.open_sm_window_btn.setEnabled(True)

            else:
                self.open_mbs_window_btn.setText('Mandelbrot Set')
                self.open_mbs_window_btn.setEnabled(True)

        self.subprocess = Process(name='tsw', target=TextureShaderWindow.run, args=())
        self.subprocess.start()

        self.open_ts_window_btn.setText('Currently Running')
        self.open_ts_window_btn.setDisabled(True)

        # application.closeAllWindows()  # close the launcher
        # application.exit(0)

    def open_sm_window(self) -> None:
        if self.subprocess:
            self.subprocess.terminate()

            if self.subprocess.name == 'tsw':
                self.open_ts_window_btn.setText('Texture Shaders')
                self.open_ts_window_btn.setEnabled(True)

            else:
                self.open_mbs_window_btn.setText('Mandelbrot Set')
                self.open_mbs_window_btn.setEnabled(True)

        self.subprocess = Process(name='smw', target=SlimeMoldWindow.run, args=())
        self.subprocess.start()

        self.open_sm_window_btn.setText('Currently Running')
        self.open_sm_window_btn.setDisabled(True)

        # application.closeAllWindows()  # close the launcher
        # application.exit(0)

    def open_mbs_window(self) -> None:
        if self.subprocess:
            self.subprocess.terminate()

            if self.subprocess.name == 'tsw':
                self.open_ts_window_btn.setText('Texture Shaders')
                self.open_ts_window_btn.setEnabled(True)

            else:
                self.open_sm_window_btn.setText('Slime Mold Simulation')
                self.open_sm_window_btn.setEnabled(True)

        self.subprocess = Process(name='mbsw', target=MandelbrotSetWindow().run, args=())
        self.subprocess.start()

        self.open_mbs_window_btn.setText('Currently Running')
        self.open_mbs_window_btn.setDisabled(True)

        # application.closeAllWindows()  # close the launcher
        # application.exit(0)


"""
executing
"""


if __name__ == '__main__':
    window = VisualSimulationsLauncher()
    window.show()
    application.exec()
