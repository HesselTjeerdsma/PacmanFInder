import asyncio
import datetime
import random
import websockets
import functools
import json

async def serve_websocket(websocket, path,game_object):
    prev_food = []
    prev_energizer = []
    prev_cherry = []
    while True:
        now = datetime.datetime.utcnow().isoformat() + 'Z'

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
                'y': opponent.rect.centery
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
        payload['Players'] = player_data

        await websocket.send(json.dumps(payload))
        await asyncio.sleep(0.5)


