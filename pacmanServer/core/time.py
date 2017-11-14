import asyncio
from collections import deque

import logging
logger = logging.getLogger(__name__)


class AsyncClock:
    """ Asyncio version of Pygame.time.Clock() """
    def __init__(self, loop):
        self._loop = loop
        self._last_tick = self._loop.time()
        self._passed_times = deque(maxlen=10)

    async def tick(self, fps):
        """ Wait for a specified amount of time so that the framerate is capped """
        max_passed_time = 1/fps
        now = self._loop.time()
        passed_time = now - self._last_tick
        time_to_sleep = max_passed_time - passed_time

        self._last_tick = now

        if time_to_sleep > 0:
            await asyncio.sleep(time_to_sleep)
            self._passed_times.append(max_passed_time)
            return max_passed_time
        else:
            self._passed_times.append(passed_time)
            return passed_time

    def get_fps(self):
        """ Return the current framerate """
        try:
            return len(self._passed_times) / sum(self._passed_times)
        except ZeroDivisionError:
            return 0
