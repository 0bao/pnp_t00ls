# 🧩 默认配置
defaults = {
    "MAX_CARD_WIDTH_MM": 44,
    "MAX_CARD_HEIGHT_MM": 66,
    "CARD_WIDTH_MM": 42.5,
    "CARD_HEIGHT_MM": 64.5,
    "REPEAT": False,
    "REPEAT_COUNT": 0,
    "WRITE_TEXT": "",
    "ROWS": -1,
    "COLS": -1,
    "RIGHT_TO_LEFT": False,
}

DPI = 300

A4_WIDTH_MM = 210
A4_HEIGHT_MM = 297

A4_WIDTH = int(A4_WIDTH_MM / 25.4 * DPI)
A4_HEIGHT = int(A4_HEIGHT_MM / 25.4 * DPI)