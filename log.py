# coding: utf-8
# Simple logging module
import os, sys
from datetime import datetime
sys.path.insert(0, os.path.dirname(__file__))
from color import colored

class Level(object):
    """
    Log level
    """
    class Label(object):
        def __init__(self, name, level, color=None):
            self.name = name
            self.level = level
            self.color = color

        def __str__(self):
            return self.name

        def __cmp__(self, other):
            if isinstance(other, Level.Label):
                l = other.level
            elif isinstance(other, int):
                l = other
            else:
                raise TypeError

            if self.level < other:
                return -1
            elif self.level > other:
                return 1
            else:
                return 0

        def __lt__(self, other): return self.__cmp__(other) < 0

        def __gt__(self, other): return self.__cmp__(other) > 0

        def __eq__(self, other): return self.__cmp__(other) == 0

        def __ne__(self, other): return not self.__eq__(other)

        def __le__(self, other): return self.__lt__(other) or self.__eq__(other)

        def __ge__(self, other): return self.__gt__(other) or self.__eq__(other)

    DEBUG = Label('DEBUG', 0)
    INFO = Label('INFO', 1)
    WARN = Label('WARN', 2, color='yellow')
    ERROR = Label('ERROR', 3, color='red')
    FATAL = Label('FATAL', 4, color='red')

    @classmethod
    def labelize(cls, level):
        if level is None:
            return cls.INFO
        if isinstance(level, Level.Label):
            return level
        if isinstance(level, str):
            if hasattr(cls, level):
                return getattr(cls, level)
            else:
                raise ValueError('Undefined logging level: {}'.format(level))
        raise TypeError


class Logger(object):
    """
    Simple logging
    [Usage]
        from log import Logger
        logger = Logger()
        logger('message', level='DEBUG')
    """
    def __init__(self, output=None, min_level=None, colored=True):
        self.min_level = Level.labelize(min_level)

        if output:
            self.output = output
        else:
            self.output = sys.stdout

    def write(self, message, level=None, color=None):
        level = Level.labelize(level)
        if level < self.min_level:
            return
        now = datetime.now().isoformat()
        if color:
            text = colored('{} [{}] {}\n'.format(now, level, message), 
                    color=color)
            self.output.write(text)

    def __call__(self, *args, **kwargs):
        self.write(*args, **kwargs)


# Default logging object
LOG = Logger()

