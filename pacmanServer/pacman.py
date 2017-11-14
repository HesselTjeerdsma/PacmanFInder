#!/usr/bin/env python

import pygame
import asyncio
from core.game import Game
from core.inventory import SpriteInventory
from core.definitions import *
from apps.registration import RegistrationAPI
from apps.events import EventAPI
from apps.scheduler import Scheduler

import logging
logging.basicConfig(level=LOGGING_LEVEL, format=LOGGING_FORMAT)

logging.getLogger('aiohttp.access').setLevel(logging.WARNING)
logging.getLogger('asyncio').setLevel(logging.WARNING)
logging.getLogger('websockets').setLevel(logging.WARNING)

from the_websocket import *

if __name__ == "__main__":
    # Asyncio event loop
    loop = asyncio.get_event_loop()

    # os.putenv('SDL_VIDEODRIVER', 'dummy')  # To run headlessly; not working with collide_mask()

    # Init pygame lib
    pygame.init()

    # Init sprite inventory
    inventory = SpriteInventory()

    # Init game
    game = Game(loop, inventory, PROJECT_DIR + '/' + MAP_DIR + '/' + MAP, WINDOW_CAPTION)

    # Init registration server
    reg = RegistrationAPI(loop, inventory, REGISTRATION_IP, REGISTRATION_PORT)

    # Init events client
    events = EventAPI(loop, inventory, EVENT_PORT)
    game.register(events)  # events observes game; for game specific events, such as gathering food

    # Init scheduler
    scheduler = Scheduler(loop, inventory)
    scheduler.register(events)  # events observes scheduler; to request location

    # Start it all
    asyncio.ensure_future(reg.start())
    asyncio.ensure_future(scheduler.start())

    bound_handler = functools.partial(serve_websocket, game_object=game)
    start_server = websockets.serve(bound_handler, '0.0.0.0', 443)

    loop.run_until_complete(start_server)

    try:
        # Run asyncio loop until game stops playing
        loop.run_until_complete(game.play())
    except KeyboardInterrupt:
        pass
    finally:
        pending = asyncio.Task.all_tasks()
        for i in pending:
            i.cancel()
        loop.close()
