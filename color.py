# coding: utf-8

ANSI_ESCAPE_CODES = {
    'bold': '\033[1m',
    'italic': '\033[3m',
    'underline': '\033[4m',
    'black': '\033[90m',
    'red': '\033[91m',
    'green': '\033[92m',
    'yellow': '\033[93m',
    'blue': '\033[94m',
    'magenta': '\033[95m',
    'cyan': '\033[96m',
    'white': '\033[97m',
    'END': '\033[0m'
}


def _ansi_formatted(text, key):
    if not key in ANSI_ESCAPE_CODES:
        raise KeyError('{} is not in ANSI_ESCAPE_CODES table'.format(key))

    return '{}{}{}'.format(ANSI_ESCAPE_CODES.get(key),
            text, ANSI_ESCAPE_CODES.get('END'))


def colored(text, color=None, bold=False, italic=False, underline=False):
    if bold:
        text = _ansi_formatted(text, 'bold')

    if italic:
        text = _ansi_formatted(text, 'italic')

    if underline:
        text = _ansi_formatted(text, 'underline')

    if color is None:
        return text

    return _ansi_formatted(text, color)


def colorprint(text, *args, **kwargs):
    print(colored(text, *args, **kwargs))
