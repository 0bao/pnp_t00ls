from config import *

def mm_to_px(mm, dpi=DPI):
    return int((mm / 25.4) * dpi)