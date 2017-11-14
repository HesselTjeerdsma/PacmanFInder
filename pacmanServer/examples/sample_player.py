import asyncio
import aiohttp
from aiohttp import web

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logging.getLogger('aiohttp.access').setLevel(logging.WARNING)
logging.getLogger('asyncio').setLevel(logging.WARNING)

#PACMAN_SERVICE_HOST = 'pacman.autonomic-networks.ele.tue.nl'
#PACMAN_SERVICE_PORT = 80
PACMAN_SERVICE_HOST = '127.0.0.1'
PACMAN_SERVICE_PORT = 50000
EVENT_HOST = '127.0.0.1'
EVENT_PORT = 50001


class SampleServer:
    def __init__(self, loop, host, port):
        super().__init__()
        self.__loop = loop
        self.__host = host
        self.__port = port
        # Setup server and routes
        self.__app = web.Application(loop=self.__loop)
        self.__app.router.add_post('/event/{event}', self.handle_events)

        # Fake coordinate
        self.__x = 10*1000
        self.__y = 75*100

    async def start(self):
        """ Start aiohttp server """
        logger.debug("Server started")
        await self.__loop.create_server(self.__app.make_handler(), self.__host, self.__port)

    async def handle_events(self, request):
        event = request.match_info['event']

        if 'application/json' in request.headers.get('content-type'):
            try:
                payload = await request.json()
            except:
                logger.error("Could not decode JSON")
                return web.Response(text='Could not decode JSON', status=403)
        else:
            payload = await request.text()

        if event == 'location':
            #logger.debug("Requested my location")
            data = {'x': self.__x, 'y': self.__y, 'z': 100}
            if self.__x < 79*1000 and self.__y == 75*100:
                self.__x += 1*50
            elif self.__x == 79*1000 and self.__y < 20*1000:
                self.__y += 1*50
            elif self.__x > 64*1000 and self.__y == 20*1000:
                self.__x -= 1*50
            elif self.__x == 64*1000 and self.__y > 75*100:
                self.__y -= 1*50
            await asyncio.sleep(0.01)
            return web.json_response(data)
        elif event == 'location_error':
            logger.debug("Movement error %d %d", payload['x'], payload['y'])
            return web.Response(text='shit')
        elif event == 'food' or event == 'cherry' or event == 'energizer':
            logger.info("%s ate %s and I have %d points now", payload['who'], event, payload['score'])
            return web.Response(text='nice')
        elif event == 'cherry_spawned':
            logger.info("A cherry spawned on %d %d for %0.1f seconds", payload['location']['x'],
                        payload['location']['y'], payload['lifetime'])
            return web.Response(text='cool')
        elif event == 'collision':
            logger.info("I collided with: %s. I got %d lives left and %d points",
                        payload['hit'], payload['lives'], payload['score'])
            return web.Response(text='ok')
        elif event == 'quarantine':
            logger.info("I am in quarantine...")
            return web.Response(text='oh no')
        elif event == 'game_over':
            logger.info("Game over :( with %d points and %d lives", payload['score'], payload['lives'])
            return web.Response(text='oh no')
        elif event == 'game_won':
            logger.info("Game won :) with %d points and %d lives", payload['score'], payload['lives'])
            return web.Response(text='YAAY')
        else:
            return web.Response(text='Unsupported event', status=403)


async def register(name: str, service_host: str, service_port: int):
    """ Register player to the game """
    payload = {'name': name}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post('http://' + service_host + ':' + str(service_port) + '/register',
                                    json=payload) as response:
                assert response.status == 200
                return await response.json()
    except (aiohttp.ClientError, AssertionError) as e:
        logger.error("Could not register: %s", e)
        return False


async def main(loop):
    name = 'Floran'
    server = SampleServer(loop, EVENT_HOST, EVENT_PORT)

    data = await register(name, PACMAN_SERVICE_HOST, PACMAN_SERVICE_PORT)
    if data:
        logger.debug("Successfully registered:\n %s", data)
        await server.start()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    asyncio.ensure_future(main(loop))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        pending = asyncio.Task.all_tasks()
        for i in pending:
            i.cancel()
        loop.close()
