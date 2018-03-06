
DEBUG = 1 << 1
INFO = 1 << 2
WARNING = 1 << 3
ERROR = 1 << 4
CRITICAL = 1 << 5
DEFAULT_LEVELS = int('11111', 2)

class Logger(object):
    """
    TODO: Figure out why the default logger doesn't work as expected
    """

    def __init__(self, name="", level=DEFAULT_LEVELS):
        self.level = level
        self.name = name

    def to_level(self, level_names: str):
        mask = 0

        for level_name in levels:
            if level in levels_by_name[level_name]:
                mask |= levels_by_name[level_name]
            else:
                raise Exception('Invalid level name ' + str(level_name))

        return mask

    def set_level(self, level):
        self.level = level

    def _log(self, args, level_name=''):
        print('{}:{}'.format(self.name, level_name), *args)

    def debug(self, *args):
        if self.level & DEBUG != 0:
            self._log(args, level_name='DEBUG')

    def info(self, *args):
        if self.level & INFO != 0:
            self._log(args, level_name='INFO')

    def warning(self, *args):
        if self.level & WARNING != 0:
            self._log(args, level_name='WARNING')

    def error(self, *args):
        if self.level & ERROR != 0:
            self._log(args, level_name='ERROR')

    def critical(self, *args):
        if self.level & CRITICAL != 0:
            self._log(args, level_name='CRITICAL')


levels_by_name = {
    'DEBUG': DEBUG,
    'INFO': INFO,
    'WARNING': WARNING,
    'ERROR': ERROR,
    'CRITICAL': CRITICAL,
}
