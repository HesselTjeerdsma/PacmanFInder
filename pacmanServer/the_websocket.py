import asyncio
import datetime
import random
import websockets
import functools
import json

import logging
logger = logging.getLogger(__name__)

async def serve_websocket(websocket, path,game_object,loop):
    prev_food = []
    prev_energizer = []
    prev_cherry = []
    prev_players = []
    prev_msg = {}
    loop.create_task(websocket_read(websocket,game_object))
    while True:
        food_locations = [{'x': food.rect.x,
                           'y': food.rect.y} for food in game_object._sprite_inventory.food]
        energizer_locations = [{'x': energizer.rect.x,
                                'y': energizer.rect.y} for energizer in game_object._sprite_inventory.energizers]
        cherry_locations = [{'x': cherries.rect.x,
                                'y': cherries.rect.y} for cherries in game_object._sprite_inventory.cherries]
        player_data = {}
        for opponent in game_object._sprite_inventory.players:
            player_data[opponent.name] = {
                'x': opponent.rect.centerx,
                'y': opponent.rect.centery,
                'type': opponent.p_type,
                'real_name': opponent._rname
            }

        payload = {}
        if(prev_food != food_locations):
             payload['Food'] = food_locations
             prev_food = food_locations
        if(prev_cherry != cherry_locations):
            payload['Cherry'] = cherry_locations
            prev_cherry = cherry_locations
        if(prev_energizer != energizer_locations):
            payload['Energizer'] = energizer_locations
            prev_energizer = energizer_locations
        if(prev_players != player_data):
            payload['Players'] = player_data
            prev_players = player_data

        if(prev_msg != payload):
            await websocket.send(json.dumps(payload))
            prev_msg = payload


        await asyncio.sleep(0.5)


async def websocket_read(websocket,game_object):
    while True:
        try:   
            msg = await websocket.recv()
        except:
            break
        else:
            try:
                json_msg = json.loads(msg)
                if(json_msg['name'] == ""):
                    continue
            except:
                await websocket.send("Wrong Format")
            else:
                try:
                    name_found = False
                    for opponent in game_object._sprite_inventory.players:
                        if(opponent.name == json_msg['name']):
                            logger.info("Player Found")
                            opponent._rname = json_msg['rname']
                            await websocket.send("Name: "+json_msg['name']+" is now: "+json_msg['rname'])
                            name_found = True
                    if not name_found:
                        logger.info("Player Name Not Found")
                        await websocket.send("Player Name Not Found")
                        
                except:
                    await websocket.send("Failed Parsing")

