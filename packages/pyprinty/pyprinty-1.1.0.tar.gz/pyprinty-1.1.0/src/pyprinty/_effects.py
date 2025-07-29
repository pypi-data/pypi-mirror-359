class Spacial:
    URL = lambda url, text: f"\033]8;;{url}\033\\{text}\033]8;;\033\\"
    WINDOW_TITLE = lambda title: f"\033]0;{title}\007"
    WINDOW_COLOR = lambda r, g, b: f"\033]11;{f"#{r:02X}{g:02X}{b:02X}"}\007"
    DONG = "\a"


class Effects:
    Bold          = "\033[1m"
    Dim           = "\033[2m"
    Italic        = "\033[3m"
    Underline     = "\033[4m"
    Dubleline     = "\033[21m"
    Blink         = "\033[5m"
    Speedblink    = "\033[6m"
    Strikethrough = "\033[9m"
    Upline        = "\033[53m"
    Transparent = "\033[8m"
    CLEAR_EFFECTS = "\033[0m"


class Cursor:
    JUMP = lambda x, y: f"\033[{y};{x}H"
    RIGHT = lambda num: f"\033[{num}C"
    DOWN = lambda num: f"\033[{num}B"
    LEFT = lambda num: f"\033[{num}D"
    UP = lambda num: f"\033[{num}F"
    CLEAR_LINE = "\033[2K\r"
    CLEAR_ALL = "\033c"
    HIDE = "\033[?25l"
    SHOW = "\033[?25h"
    SAVE = "\x1b[s"
    BACK = "\x1b[u"
    PRINT = lambda name: print(name, end="", flush=True)
    MODE_DEFAULT = "\033[0 q"
    MODE_THICK = "\033[2 q"
    MODE_BLINKING_THICK = "\033[1 q"
    MODE_BL = "\033[4 q"
    MODE_BLINKING_BL = "\033[3 q"
    MODE_BLINKING_CLASSIC = "\033[5 q"
    MODE_CLASSIC = "\033[6 q"
