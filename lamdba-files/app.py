#!flask/bin/python
# A* Pathfinding in Python (2.7)
# Please give credit if usedpip
from flask import Flask, jsonify, abort, request, make_response, url_for
import time
import numpy
import numpy as np
from heapq import *
from threading import Timer
from random import randint
from numpy import interp
numpy.set_printoptions(threshold=numpy.nan)
app = Flask(__name__)
Own_Position = np.array([12,1])
Goal_Position = np.array([0,0])
setupDone = False
path = []
array_x = 98
array_y = 45



@app.before_first_request
def create_array():
    global nmap
    nmap = numpy.ones(array_x, array_y)
    nmap[1:-1,1:-1] = 0

@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify( { 'error': 'Bad request' } ), 400)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)

def do_kdtree(combined_x_y_arrays,points):
    mytree = scipy.spatial.cKDTree(combined_x_y_arrays)
    dist, indexes = mytree.query(points)
    return combined_x_y_arrays[indexes]

def conversion(not_converted):
    return int(not_converted/500)


def direction(coordinate):
    if coordinate[0] and coordinate[1] == -1:
        direction = 12 #W
    elif coordinate[0] and coordinate[1] == 1:  
        direction = 4 #E
    elif coordinate[0] == -1 and coordinate[1] == 0:
        direction =  14 #NW
    elif coordinate[0] == -1 and coordinate[1] == 1:
        direction =  0 #N
    elif coordinate[0] == 0 and coordinate[1] == 1:
        direction =  2 #NE
    elif coordinate[0] == 1 and coordinate[1] == -1:
        direction =  8 # S
    elif coordinate[0] == 1 and coordinate[1] == 0:
        direction =  6 # SE
    else:
        direction =  10 #SW
    return direction

def heuristic(a, b):
    return (b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2


def astar(array, start, goal):
    neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    close_set = set()
    came_from = {}
    gscore = {start: 0}
    fscore = {start: heuristic(start, goal)}
    oheap = []

    heappush(oheap, (fscore[start], start))

    while oheap:
        current = heappop(oheap)[1]

        if current == goal:
            data = []
            while current in came_from:
                data.append(current)
                current = came_from[current]
            return data

        close_set.add(current)
        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j
            tentative_g_score = gscore[current] + heuristic(current, neighbor)
            if 0 <= neighbor[0] < array.shape[0]:
                if 0 <= neighbor[1] < array.shape[1]:
                    if array[neighbor[0]][neighbor[1]] == 1:
                        continue
                else:
                    # array bound y walls
                    continue
            else:
                # array bound x walls
                continue

            if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
                continue

            if tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1] for i in oheap]:
                came_from[neighbor] = current
                gscore[neighbor] = tentative_g_score
                fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heappush(oheap, (fscore[neighbor], neighbor))

    return False

    
@app.route('/event/register', methods = ['POST'])
def setup_handler():
    global path
    if not request.json:
            return jsonify('no json')
    else:
        settings = request.get_json() 
        global setupDone
        setupDone = True
        return jsonify("succes")    


@app.route('/event/direction', methods = ['POST'])
def locationRequest_handler():
    global Own_Position
    esp_locatation = request.get_json()
    Own_Position = [conversion(esp_locatation['own_pos']['y']), conversion(esp_locatation['own_pos']['x'])]
    Goal_Position = [conversion(esp_locatation['goal_pos']['y']), conversion(esp_locatation['goal_pos']['x'])]
    path = astar(nmap,(Own_Position[0],Own_Position[1]),(Goal_Position[0],Goal_Position[1]))
    return jsonify(direction(np.array(Own_Position) - np.array(path[-1])))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)


