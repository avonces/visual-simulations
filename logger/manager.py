import logging.config
from os import walk, remove
from datetime import datetime


"""
----------
USAGE
----------
display output for ordinary cli:
    print()

report events (status monitoring, fault investigation):
    logger.info() or
    logger.debug() for detailed output

issue warnings (particular runtime events):
    issue is avoidable and the code should be modified:
        warnings.warn()
    the event should be noticed, but there is nothing you can do about it:
        logger.warning()

report errors (particular runtime events):
    catch Error/
    raise MostSpecificError()

report suppressed errors without raising exceptions:
    logger.error() or
    logger.exception() or
    logger.critical()
----------
"""


class LogManager:
    """
    A simple manager created using the logging module providing some utility functions
    for creating and managing a logger and log files.
    """
    def __init__(self, logfile_directory: str = './logger/log') -> None:
        self.logfile_directory = logfile_directory
        self.logger = None

    def init_logger(self, name: str = __name__) -> logging.Logger:
        """Initializes a logger."""
        logging.config.fileConfig(
            'logger/logging.ini',
            encoding='utf-8',
            defaults={
                'logfilename':
                    f'./logger/log/{datetime.now().strftime("%Y-%m-%d_-_%H-%M-%S")}.log'
            }
        )

        self.logger = logging.getLogger(name)
        return self.logger

    def remove_old_log_files(self, remaining: int = 3) -> None:
        """Leave x logfiles in the logfile directory, remove the rest."""
        logfiles = list(filter(lambda file: file.endswith('.log'),
                               next(walk(self.logfile_directory), (None, None, []))[2]))

        if len(logfiles) > remaining:
            for logfile in logfiles[0:len(logfiles) - remaining]:
                remove(
                    self.logfile_directory if self.logfile_directory.endswith("/")
                    else f"{self.logfile_directory}/"
                         + logfile
                )

    def remove_all_log_files(self) -> None:
        """Remove all logfiles from the logfile directory."""
        logfiles = list(filter(lambda file: file.endswith('.log'),
                               next(walk(self.logfile_directory), (None, None, []))[2]))

        for logfile in logfiles:
            remove(
                self.logfile_directory if self.logfile_directory.endswith("/")
                else f"{self.logfile_directory}/"
                     + logfile
            )
