from aiohttp import web
from core.objects import Player
from core.definitions import PG_RATIO, COLOR_GREEN, COLOR_RED, ALLOWED_PROXIES
from util.auxillary import x_px_to_mm, y_px_to_mm
from json import JSONDecodeError

import logging
logger = logging.getLogger(__name__)


class RegistrationAPI:
    """ Simple player registration """
    # TODO: host str to ipaddress
    def __init__(self, loop, inventory, host: str, port: int):
        super().__init__()
        self._loop = loop
        # Sprite inventory
        self._sprite_inventory = inventory
        # Server settings
        self._host = host
        self._port = port
        # Setup server and routes
        self._app = web.Application(loop=self._loop)
        self._app.router.add_post('/register', self._handle_registration)

    async def start(self):
        """ Start aiohttp server """
        logger.debug("Server started")
        await self._loop.create_server(self._app.make_handler(), self._host, self._port)

    async def _handle_registration(self, request):
        """ Handle registration requests """
        # Get requester's IP
        peername = request.transport.get_extra_info('peername')
        if peername is None:
            logger.error('Invalid peername')
            return web.Response(text='Permission denied.', status=403)
        host, port = peername

        # If behind a proxy?
        if peername in ALLOWED_PROXIES or host in ALLOWED_PROXIES:
            host = request.headers.get('X-FORWARDED-FOR')

        try:  # Try to decode JSON
            payload = await request.json()
        except JSONDecodeError:
            return web.Response(text='Could not decode JSON', status=403)

        # Correct payload?
        if 'name' not in payload:
            return web.Response(text='Missing `name` key in JSON', status=403)

        payload['name'] = payload['name'][:30]  # Cap player name to 30 chars

        # Check whether ip and name already occurs
        for player in self._sprite_inventory.players:
            if player.ip == host:
                return web.Response(text='A player is already registered on this IP', status=403)
            elif player.name == payload['name']:  # TODO: enforce unique player names?
                return web.Response(text='Player name already taken', status=403)

        # Depending on ratio, player type: `pacman` or `ghost`
        # if len(self._sprite_inventory.ghosts) >= len(self._sprite_inventory.pacmans) * PG_RATIO:
        #    player = Player(-50, -50, COLOR_GREEN, p_type='pacman', ip=host, name=payload['name'])
        #    self._sprite_inventory.pacmans.add(player)
        # else:
        #    player = Player(-50, -50, COLOR_RED, p_type='ghost', ip=host, name=payload['name'])
        #    self._sprite_inventory.ghosts.add(player)

        if payload['name'].find("pacman"):
            player = Player(-50, -50, COLOR_GREEN, p_type='pacman', ip=host, name=payload['name'])
            self._sprite_inventory.pacmans.add(player)
        else:
	   player = Player(-50, -50, COLOR_RED, p-type='ghost', ip=host, name=payload['name'])
	   self._sprite_inventory.ghosts.add(player)
 
        self._sprite_inventory.players.add(player)
        self._sprite_inventory.all.add(player)

        # Gather food/energizer locations
        food_locations = [{'x': x_px_to_mm(food.rect.x),
                           'y': y_px_to_mm(food.rect.y)} for food in self._sprite_inventory.food]
        energizer_locations = [{'x': x_px_to_mm(energizer.rect.x),
                                'y': y_px_to_mm(energizer.rect.y)} for energizer in self._sprite_inventory.energizers]

        # Respond with type and food/energizer locations
        return web.json_response(data={
            'type': player.p_type,
            'food_locations': food_locations,
            'energizer_locations': energizer_locations
        })
