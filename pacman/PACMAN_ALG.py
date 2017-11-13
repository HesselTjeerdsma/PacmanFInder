import math as Math
from PATH import *


def sortDistance(elem):
    return elem['distance']

def run_Algorithm(PACMAN):
	#print("Algorithm")
	i = 0
	for value in PACMAN.food:
		dx = -(PACMAN.x - PACMAN.food[i]['x'])
		dy = (PACMAN.y - PACMAN.food[i]['y'])
		
		#Lenght of vector
		PACMAN.food[i]["distance"] = int(Math.hypot(dx,dy))
		#Angle of vector referenced x=1,y=0
		PACMAN.food[i]["angle"]    = int(Math.degrees(Math.atan2(dy,dx)))-90
		i+=1
		
	PACMAN.food = sorted(PACMAN.food,key=sortDistance,reverse=False)
	
	for key,value in PACMAN.PlayerData.items():
		dx = -(PACMAN.x - PACMAN.PlayerData[key]['x'])
		dy = (PACMAN.y - PACMAN.PlayerData[key]['y'])
		
		#Lenght of vector
		PACMAN.PlayerData[key]["distance"] = int(Math.hypot(dx,dy))
		#Angle of vector referenced x=1,y=0
		PACMAN.PlayerData[key]["angle"]    = int(Math.degrees(Math.atan2(dy,dx)))-90
		i+=1
		
	#PACMAN.PlayerData = sorted(PACMAN.PlayerData,key=sortDistance,reverse=False)
	
	i = 0
	for value in PACMAN.energizer:
		dx = -(PACMAN.x - PACMAN.energizer[i]['x'])
		dy = (PACMAN.y - PACMAN.energizer[i]['y'])
		
		#Lenght of vector
		PACMAN.energizer[i]["distance"] = int(Math.hypot(dx,dy))
		#Angle of vector referenced x=1,y=0
		PACMAN.energizer[i]["angle"]    = int(Math.degrees(Math.atan2(dy,dx)))-90
		i+=1
		
	PACMAN.energizer = sorted(PACMAN.energizer,key=sortDistance,reverse=False)
	
	i = 0
	for value in PACMAN.cherry:
		try:
			dx = -(PACMAN.x - PACMAN.cherry[i]['x'])
			dy = (PACMAN.y - PACMAN.cherry[i]['y'])
			
			#Lenght of vector
			PACMAN.cherry[i]["distance"] = int(Math.hypot(dx,dy))
			#Angle of vector referenced x=1,y=0
			PACMAN.cherry[i]["angle"]    = int(Math.degrees(Math.atan2(dy,dx)))-90
			i+=1
		except:
			continue
	
	try:
		PACMAN.cherry = sorted(PACMAN.cherry,key=sortDistance,reverse=False)
	except:
		pass

	"""
	if(PACMAN.type == 'pacman'):
	
	elif(PACMAN.type == 'ghost'):
		PACMAN.path = astar(tilemap, (PACMAN.x, startx), (targety, targetx))
	"""