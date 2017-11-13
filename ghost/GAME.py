from PACMAN import *
from SERVER_LIB import *
from POZYX import *
from time import sleep
import os
import json
import socket
import _thread

import pypozyx

if __name__ == "__main__":
	#Our player name
	GAME.set_name("BIERoT");
	#GAME.set_name(fish)

	#Start HTTP server
	Web = WebServer(ADDR,PORT);
	
	GAME.set_Web(Web)
	
	#Try to get serial com port
	try:
		serial_port = get_serial_ports()[0].device
		serial_port = "/dev/ttyACM0"
		remote_id = None
	except:
		print("No com port")
		serial_port = ""
		pass
	
	# Anchor data (necessary data for calibration)
	"""
	anchors = [DeviceCoordinates(0x6847, 1, Coordinates(2, 2050, 2499)),
				DeviceCoordinates(0x6877, 1, Coordinates(2819, 22828, 2595)),
				DeviceCoordinates(0x6170, 1, Coordinates(13745, 2, 2621)),
				DeviceCoordinates(0x6169, 1, Coordinates(19923, 27836, 2655)),
				
				DeviceCoordinates(0x682d, 1, Coordinates(31750, 2010, 2636)),
				DeviceCoordinates(0x6147, 1, Coordinates(35166, 2080, 2658)),
				DeviceCoordinates(0x6823, 1, Coordinates(26342, 27810, 2628)),
				DeviceCoordinates(0x614b, 1, Coordinates(34639, 25070, 2692))]
	"""
	anchors = [DeviceCoordinates(0x6847, 1, Coordinates(0, 50, 2499)),
				DeviceCoordinates(0x6877, 1, Coordinates(2619, 20828, 2595)),
				DeviceCoordinates(0x6170, 1, Coordinates(11745, 0, 2621)),
				DeviceCoordinates(0x6169, 1, Coordinates(17923, 25836, 2655))]
	
	algorithm = POZYX_POS_ALG_TRACKING	# positioning algorithm to use
	dimension = POZYX_3D				# positioning dimension
	height = 1000						# height of device, required in 2.5D positioning
	
	#Try connecting to the Pozyx
	try:
		pozyx_com = PozyxSerial(serial_port,debug_trace=True)
		pozyx = Pozyx_Obj(pozyx_com, anchors, algorithm, dimension, height)
		pozyx.setup()
		GAME.set_pozyx(pozyx)
	except Exception as e:
		print("Unable to reach Pozyx on\n")
		print(e)
		print("Starting without...")
		raise SystemExit
	except:
		print("Exception2")
		raise SystemExit
	
	#Serve all POST requests in a thread
	_thread.start_new_thread(Web.run, ())
	
	#Register to Service using GAME object
	if(Web.register(GAME) == False):
		print("Failed to register")
		raise SystemExit
	
	GAME.run()
