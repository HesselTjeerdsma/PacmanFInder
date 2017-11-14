import json
import copy
from util.auxillary import async_current_milli_time

import logging
logger = logging.getLogger(__name__)


class Observation:
    def __init__(self, src, action, data, clock=None):
        self._source = src
        self._action = action
        self._data = data
        if not clock:
            self._clock = async_current_milli_time()
        else:
            self._clock = clock

    @property
    def source(self):
        return self._source

    @property
    def clock(self):
        return self._clock

    @property
    def data(self):
        return self._data

    @property
    def action(self):
        return self._action

    def __str__(self):
        return json.dumps({
            'clock': self._clock,
            'action': str(self._action),
            'data': self._data
        })


class Observable:
    def __init__(self):
        super().__init__()
        self._observers = []

    @property
    def observers(self):
        return copy.deepcopy(self._observers)

    def register(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)
            return True
        return False

    def deregister(self, observer):
        if observer in self._observers:
            self._observers.remove(observer)
            return True
        return False

    def notify(self, msg):
        for observer in self._observers:
            observer.observe_callback(msg)

    def reset(self):
        del self._observers[:]


class Observer:
    def observe_callback(self, msg):
        pass
