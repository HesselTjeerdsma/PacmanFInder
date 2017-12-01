import aiohttp
import asyncio
from core.observe import Observer, Observation
from util.auxillary import x_px_to_mm, y_px_to_mm
import pygame
from json import JSONDecodeError

import logging
logger = logging.getLogger(__name__)


class EventAPI(Observer):
    """ Interface that handles all possible actions that happen in the game and deals with device interaction """
    def __init__(self, loop, inventory, port: int):
        super().__init__()
        self._loop = loop
        self._sprite_inventory = inventory
        self._port = port
        self._session = aiohttp.ClientSession(loop=self._loop)

    def __del__(self):
        self._session.close()

    async def _post_event(self, event, data):
        if isinstance(data, dict):
            try:
                player = data['player']
            except KeyError:  # dict does not contain player
                logger.error("Event data should have player object")
                return
        else:
            player = data

        # TODO: remove this debug:
        if player.debug:
            if event == 'location':
                # Continue scheduler
                data['future'].set_result(True)
            return

        if event == 'location':
            payload = {
                'request_location': True,
                'player_locations': {}
            }
            for opponent in self._sprite_inventory.players:
                if opponent is not player:
                    payload['player_locations'][opponent.name] = {
                        'x': x_px_to_mm(opponent.rect.centerx),
                        'y': y_px_to_mm(opponent.rect.centery),
                        'rname': opponent._rname
                    }
        elif event == 'location_error':
            payload = {
                'x': data['x'],
                'y': data['y']
            }
        elif event == 'food' or event == 'cherry' or event == 'energizer':
            payload = {
                'who': data['who'].name,
                'score': player.score,
                'location': {
                    'x': x_px_to_mm(data['location']['x']),
                    'y': y_px_to_mm(data['location']['y'])
                }
            }
        elif event == 'cherry_spawned':
            payload = {
                'lifetime': data['lifetime'],
                'location': {
                    'x': x_px_to_mm(data['location']['x']),
                    'y': y_px_to_mm(data['location']['y'])
                }
            }
        elif event == 'collision':
            payload = {
                'hit': data['hit'].name,
                'lives': player.lives,
                'score': player.score
            }
        elif event == 'quarantine':
            payload = {'quarantine': True}
        elif event == 'game_over':
            payload = {
                'game_over': True,
                'lives': player.lives,
                'score': player.score
            }
        elif event == 'game_won':
            payload = {
                'game_won': True,
                'lives': player.lives,
                'score': player.score
            }
        else:
            return

        attempts = 3
        while attempts != 0:
            try:
                # logger.debug("Post event: %s with payload: %s", event, payload)
                async with self._session.post('http://' + player.ip + ':' + str(self._port) + '/event/' + event,
                                              json=payload, timeout=1) as response:
                    assert response.status == 200

                    # Depends on player's idea of responses
                    # JSON needed for `location` event needed anyhow
                    if 'application/json' in response.headers.get('content-type'):
                        try:
                            response_data = await response.json()
                        except JSONDecodeError:
                            logger.error("Could not decode JSON")
                            continue  # Re-do request
                    else:
                        response_data = await response.text()

                    # If location request, push coordinates to the game
                    if event == 'location':
                        # Continue scheduler
                        try:
                            data['future'].set_result(True)
                        except:
                            logger.error("Cannot set asyncio future")

                        # Push pygame event to update location
                        event_data = {
                            'player': player,
                            'x': response_data['x'],
                            'y': response_data['y'],
                        }
                        my_event = pygame.event.Event(pygame.USEREVENT + 1, event_data)
                        try:
                            pygame.event.post(my_event)
                        except pygame.error:
                            logger.error("Failed to post pygame event")

                    return  # or break
            except:  # (asyncio.TimeoutError, aiohttp.ClientError, aiohttp.ClientOSError, AssertionError, TypeError):  # TypeError if ip is `None` for example
                attempts -= 1
                logger.warning("Could not reach player `%s`, attempts left: %d", player.name, attempts)
                await asyncio.sleep(1)
        else:  # All attempts are done
            logger.error("Could not reach player `%s`, will deregister", player.name)
            player.kill()

            # Continue scheduler after failed attempts
            if event == 'location':
                try:
                    data['future'].set_result(False)
                except:
                    logger.error("Cannot set asyncio future")

    def observe_callback(self, msg):
        """ Act on the following events:
            - `location`: request location
            - `location_error`: location error
            - `food`: a player got food
            - `cherry`: a player got cherry
            - `cherry_spawned`: a cherry was spawned
            - `energizer`: a player got energizer
            - `quarantine`: player is in quarantine
            - `collision`: player collided
            - `game_over`: player is game over
            - `game_won`: player won the game

        :param msg: `Observation` object that contains `Player` object
        """
        if isinstance(msg, Observation):
            events = ['location', 'location_error', 'food', 'cherry', 'cherry_spawned', 'energizer',
                      'collision', 'quarantine', 'game_over', 'game_won']
            if msg.action in events:
                self._loop.create_task(self._post_event(msg.action, msg.data))
