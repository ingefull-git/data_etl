import logging
import sys

from base import LoggerGeneric
from decorators import debuglog

SINGLE_LINE = '-' * 79
DOUBLE_LINE = '=' * 79
STAR_LINE = '*' * 79


class LoggerPowerSchool(LoggerGeneric):
    """
    This class is a subclass of LoggerGeneric, and it's used to log messages to a file.
    """
   
    def formatter(self):
        """
        A function that takes in a string and returns a string with the first letter capitalized.
        """        
        if self.format:
            FORMAT = self.format
        else:
            FORMAT = '%(asctime)s %(levelname)-8s {0}: %(message)s'.format('[%(funcName)-15.15s]' if self.log_level == 'DEBUG' else '')
        return FORMAT

    def stream_handler(self):
        """
        It takes a stream of data and returns a stream of data
        """
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(CustomFormatter(self.formatter(), '%Y-%m-%d %H:%M:%S'))
        return stream_handler

    def file_handler(self, log_level=None):
        """
        A function that takes two arguments, self and log_level.

        :param log_level: The log level to use for the handler
        """
        file_handler = logging.FileHandler(self.file)
        if log_level and log_level in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'):
            file_handler.setLevel(getattr(logging, log_level))
        else:
            file_handler.setLevel(getattr(logging, self.log_level))
        formatter = logging.Formatter(self.formatter())
        file_handler.setFormatter(CustomFormatter(self.formatter(), '%Y-%m-%d %H:%M:%S'))
        return file_handler

    def memory_handler(self, capacity=None, flush_level=None, target=None):
        memoryhandler = logging.handlers.MemoryHandler(
                            capacity=1024*100,
                            flushLevel=logging.Debug,
                            target=target
                        )

    def flush_memory(self, ):
        pass


# @debuglog()
class CustomFormatter(logging.Formatter):
    """
    Custom formatter, overrides funcName with value of name_override if it exists
    """
    def format(self, record):
        if hasattr(record, 'name_override'):
            record.funcName = record.name_override
        name_to_show = record.funcName
        if len(name_to_show) > 15:
            name_to_show = '{}...{}'.format(name_to_show[:6], name_to_show[-6:])
        record.funcName = name_to_show
        return super(CustomFormatter, self).format(record)

@debuglog()
def log_time(t1, t2):
    """
    This function takes two time values and prints the difference between them.

    :param t1: The time the function was called
    :param t2: The time the function was called
    """
    addz = lambda ispl: '0' if int(ispl) < 10 else ''
    fix_time = lambda ft: '{0}{1}:{2}{3}:{4}{5}'.format(
        addz(int(ft // 60)),
        int(ft // 60),
        addz(int(ft % 60)),
        int(ft % 60),
        addz(round(ft % 1 * 60, 2)),
        round(ft % 1 * 60, 3)
    )
    time_seconds = t2 - t1
    mins = time_seconds / 60
    return fix_time(mins)

@debuglog()
def error_log(msg, params=None, logger=logging):
    """
    It logs an error message

    :param msg: The message to log
    :param params: a dictionary of parameters to be logged
    :param logger: The logger object to use. Defaults to the standard logging module
    """
    logger.error(STAR_LINE)
    logger.error(msg, params) if params else logger.error(msg)
    logger.error(STAR_LINE)
    logger.debug('Exiting')
    sys.exit()

@debuglog()
def except_log(msg, params=None, logger=logging):
    """
    It logs an exception with a message and optional parameters

    :param msg: The message to log
    :param params: a dictionary of parameters to be logged
    :param logger: The logger to use. Defaults to the root logger
    """
    logger.error(STAR_LINE)
    logger.exception(msg, params) if params else logger.exception(msg)
    logger.error(STAR_LINE)

@debuglog()
def start_log(version, logger=logging):
    """
    It sets up the logger for the program.

    :param version: The version of the program
    :param logger: The logger to use. Defaults to the standard library's logging module
    """
    logger.debug('Starting debug logging...')
    logger.info(DOUBLE_LINE)
    logger.info('Power Queries Pull Generic version {0} is starting'.format(version))