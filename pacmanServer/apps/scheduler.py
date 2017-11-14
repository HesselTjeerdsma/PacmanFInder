import asyncio
from core.observe import Observable, Observation
import logging
logger = logging.getLogger(__name__)


class Scheduler(Observable):
    """ Simple location scheduler """
    def __init__(self, loop, inventory):
        super().__init__()
        self._loop = loop
        self._sprite_inventory = inventory
        self._schedule = True

    def __del__(self):
        self._schedule = False  # TODO: does this help prevent asyncio errors?

    async def start(self):
        """ Start the scheduler algorithm """
        logger.debug("Scheduler started")
        while self._schedule:
            if self._sprite_inventory.players:
                for player in self._sprite_inventory.players:
                    # Create asyncio Future so that we can wait on completion of the request
                    future = asyncio.Future()

                    # Push to events API
                    self.notify(Observation(self, 'location', {
                        'player': player,
                        'future': future
                    }))

                    # Wait until location request has been completed
                    await future
            else:
                # Wait for players
                await asyncio.sleep(5)
