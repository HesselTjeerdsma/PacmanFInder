import asyncio
from core.definitions import PM_RATIO


def async_current_milli_time():
    return int(round(asyncio.get_event_loop().time() * 1000))


def x_mm_to_px(mm):
    # TODO: find dynamic way to get screen size from map here
    return 1600-_mm_to_px(mm)


def y_mm_to_px(mm):
    return _mm_to_px(mm)


def x_px_to_mm(px):
    # TODO: find dynamic way to get screen size from map here
    return _px_to_mm(1600-px)


def y_px_to_mm(px):
    return _px_to_mm(px)


def _mm_to_px(mm):
    return round(int(mm)/1000/PM_RATIO)


def _px_to_mm(px):
    return round(int(px)*1000*PM_RATIO)
