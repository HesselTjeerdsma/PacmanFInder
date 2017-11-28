import json
import sys, os
import time
import _thread

ENERGIZER_TIME = 10
QUARANTINE_TIME = 10

GAMEWON_TEXT = "  _____                         _      __           \n / ___/ ___ _  __ _  ___       | | /| / / ___   ___ \n/ (_ / / _ `/ /  ' \\/ -_)      | |/ |/ / / _ \\ / _ \\\n\\___/  \\_,_/ /_/_/_/\\__/       |__/|__/  \\___//_//_/\n                                                   "
GAMELOST_TEXT = "  _____                          __             __ \n / ___/ ___ _  __ _  ___        / /  ___   ___ / /_\n/ (_ / / _ `/ /  ' \\/ -_)      / /__/ _ \\ (_-</ __/\n\\___/  \\_,_/ /_/_/_/\\__/      /____/\\___//___/\\__/ \n                                                   "
class PACMAN(object):
	def __init__(self):
		self.Web = web = None
		self.last_POST = {"/event/location":0,"/event/cherry":0,"/event/energizer":0,"/event/food":0,"/event/collision":0,"/event/quarantine":0,"/event/cherry_spawned":0}
		self.type = ""
		self.quarantine = False
		self.energized = False
		
		self.score = 0
		self.lives = 3
		self.game_done = False
		
		self.use_pozyx = False
		
		self.use_client = False
		
		self.magnetic = {'x':0,'y':0,'z':0,'A':0}
		self.magnetic_angle = 0
		
		self.PlayerData = {}
		self.food = []
		self.energizer = []
		self.cherry = []
		
		self.x = 56300
		self.y = 19300
		self.A = 0
		self.sendCounter = 0

		LCD_show(self)

		self.Message = ""
		
		self.prevloc = {"x":0,"y":0}
		self.newLocation = False
		
		self.Ring = LED_setup()
		self.RingColor = []
		for i in range(0,16):
			self.RingColor.append(Color(0,0,0))
		
		return
		
	def set_pozyx(self,pozyx):
		self.pozyx = pozyx
		self.use_pozyx = True
		return
	
	def set_name(self,name):
		self.name = name;
		return
	
	def loadRegistration(self,response):
		try:
			data = response.json()
		except:
			print("Failed to load")
			print(response)
			time.sleep(1)
			self.Restart()
			
		self.name = data['name']
		
		self.type = data['type']
		
		self.food = []
		self.food = data['food_locations']
		for value in self.food:
			value["distance"] = -1
			value["angle"] = 0
		
		self.energizer = []
		self.energizer = data['energizer_locations']
		for value in self.energizer:
			value["distance"] = -1
			value["angle"] = 0
		
		self.prevloc['x'] = 0
		self.prevloc['y'] = 0
		
		print("Registered")
		
		return True
	
	def newPOST(self,event,data):
		#print("POST")
		type = "text/plain"
		reply = "OK" #Standard reply
		if event == "/event/location":
			self.newLocation = True
			#Proccess player location
			for key, value in data['player_locations'].items():
				#Create of reset player
				if (key not in self.PlayerData or self.PlayerData[key]['status'] == "Left"):
					self.PlayerData[key] = {"updated":"No","status":"New","score":0,"type":"Unknown","energized":False,"x":0,"y":0,"dx":0,"dy":0,"distance":0,"angle":0}
				
				#If player exist update x & y and set Updated to Yes and its playing
				self.PlayerData[key]['status'] = "Playing"
				self.PlayerData[key]['updated'] = "Yes"
				self.PlayerData[key]['dx'] = value['x'] - self.PlayerData[key]['x']
				self.PlayerData[key]['dy'] = value['y'] - self.PlayerData[key]['y']
				self.PlayerData[key]['x'] = value['x']
				self.PlayerData[key]['y'] = value['y']
			
			for key, value in self.PlayerData.items():
				#All Players that arren't updated, are considerd that the Left the Game
				if(value['updated'] != "Yes"):
					self.PlayerData[key]['status'] = "Left"
				#Reset Updated
				self.PlayerData[key]['updated'] = "No"
				
					
			#Only send our location if its requested
			if(data['request_location']==True):
				self.get_position()
				#Reply with own coordinates
				reply = {'x':self.x,'y':self.y}
				type = "application/json"
				
				#spoofing position/debugging
				if not self.use_pozyx:
					self.incrementPos()
		elif event == "/event/cherry_spawned":
			#Add a cherry to the cherry list
			timestamp = int(time.time())
			self.cherry.append({"x":data['location']['x'],"y":data['location']['y'],"time":data['lifetime'],"timestamp":timestamp,"distance":-1,"angle":0,"active":True})
			
			
			#Create a thread with timer to delete the cherry after its lifetime
			_thread.start_new_thread(self.timer, (data['lifetime'],"cherry",timestamp))	
		elif event == "/event/food":
			#Who has taken the food
			playerName = data["who"]
			print(playerName +" ate a cherry at X:"+str(data['location']['x'])+"  Y:"+str(data['location']['y'])+" and his/her score is now "+str(data["score"]) )
			
			#Only pacman can eat a food, so set it to pacman / (doesn't cange the type when a pacman is energized)
			if(self.name != playerName):
				self.PlayerData[playerName]["type"] = "pacman"
			
				#Store score of other player
				self.PlayerData[playerName]["score"] = data["score"]
			else:
				self.score = data["score"]
				LCD_show(self)
			
			#Remove the node where the food was
			self.remove_Point('food',data['location']['x'],data['location']['y'])
		elif event == "/event/cherry":
			#Who has taken the cherry
			playerName = data["who"]
			
			if(self.name != playerName):
				#Store score of other player
				self.PlayerData[playerName]["score"] = data["score"]
			else:
				self.score = data["score"]
				LCD_show(self)
			
			#Remove the node where the cherry was
			self.remove_Point('cherry',data['location']['x'],data['location']['y'])
		elif event == "/event/energizer":
			#Who has taken the energizer
			playerName = data["who"]
			
			if(self.name != playerName and self.name.find(data["who"]+".") == -1):
				#Set that player to the energized state
				self.PlayerData[playerName]["type"] = "pacman"
				self.PlayerData[playerName]["energized"] = True
				#Store score of other player
				self.PlayerData[playerName]["score"] = data["score"]
			else:
				self.energized = True
				self.score = data["score"]
				LCD_show(self)
			
			#Remove the node where the energizer was
			self.remove_Point('energizer',data['location']['x'],data['location']['y'])
			
			_thread.start_new_thread(self.timer, (ENERGIZER_TIME,"energizer",playerName))
		elif event == "/event/quarantine":
			if(data['quarantine']):
				#Start a threaded timer to remove state
				if not (self.quarantine):
					_thread.start_new_thread(self.timer, (QUARANTINE_TIME,"quarantine"))
					
				#Add quarantine state to yourself
				self.quarantine = True
				LCD_show(self)
		elif event == "/event/collision":
			print("COLLISION")
			print(data)
			#Change score and lives
			self.score = data['score']
			self.lives = data['lives']
			LCD_show(self)
			
			if(self.type.find("pacman") != -1):
				#If I'm a pacman than is the other a ghost
				self.PlayerData[data['hit']]['type'] = "ghost"
			else:
				#If I'm a ghost than is the other a pacman
				try:
					self.PlayerData[data['hit']]['type'] = "pacman"
				except KeyError:
					self.PlayerData[data['hit']] = {"status":"New","score":0,"type":"pacman","x":0,"y":0}
					pass
		
		elif event == "/event/game_won":
			self.game_done = True
			self.score = data['score']
			self.lives = data['lives']
			self.Message = GAMEWON_TEXT
		elif event == "/event/game_over":
			self.game_done = True
			self.score = data['score']
			self.lives = data['lives']
			self.Message = GAMELOST_TEXT
			
		else:
			self.Message = "Unknown Event\n"
			self.Message += event + "\n"
			self.Message += data
			time.sleep(0.1)
			
		return (reply, type)
	
	def timer(self,timer_time,type,data1=None):
		#remove the cherry after its lifetime or remove energizer/quarantine state
		if(type == "cherry"):
			time.sleep(timer_time)
			i = -1
			for value in self.cherry:
				i += 1
				if value["timestamp"] == data1 and value["time"] == time:
					break
			
			try:
				self.cherry.pop(i)
			except:
				pass
		elif(type == "energizer"):
			time.sleep(timer_time)
			if(self.name != data1):
				#Other player
				self.PlayerData[data1]["energizer"] = False
			else:
				#Yourself
				self.energized = False
		elif(type == "quarantine"):
			time.sleep(timer_time)
			self.quarantine = False
	
	def remove_Point(self,type,x,y):
		#remove food/cherry/energizer when it was eaten
		if(type == "food"):
			i = 0
			for value in self.food:
				if(value['x'] == x and value['y'] == y):
					break
				i+=1
			try:
				self.food.pop(i)
			except KeyError:
				pass
		elif(type == "energizer"):
			i = 0
			for value in self.energizer:
				if(value['x'] == x and value['y'] == y):
					break
				i+=1
			try:
				self.energizer.pop(i)
			except KeyError:
				pass
		elif(type == "cherry"):
			i = 0
			for value in self.cherry:
				if(value['x'] == x and value['y'] == y):
					break
				i+=1
			try:
				self.cherry.pop(i)
			except KeyError:
				pass
	
	def get_position(self):
		if self.use_pozyx is not False:
			(xyz,self.magnetic) = self.pozyx.loop()
			self.magnetic['A'] += 20
			if(xyz['x'] != 0 and xyz['y'] != 0):
				self.prevloc['x'] = xyz['x']
				self.prevloc['y'] = xyz['y']
				self.x = xyz['x']
				self.y = xyz['y']
			#print("Magnetic angle: "+str(self.magnetic['A']))
			#print("Pozyx location X:"+str(xyz['x'])+"\tY:"+str(xyz['y']))

	def run(self):
		try:
			while True:
				if(self.newLocation):
					run_Algorithm(self)
				
				if(self.A == 0):
					os.system('clear')
					print("Game is running")
					print("Your name:\t" + self.name)
					print("Your type:\t"+self.type + ' ' + ('E' if (self.energized) else '') + ('Q' if (self.quarantine) else ''))
					print("Your Score:\t"+str(self.score))
					print("Your Lives:\t"+str(self.lives))
					print("Your pos.:\tX: "+str(self.x)+"\tY: "+str(self.y))
					print(self.magnetic)
					print()
					
					i = 0
					j = 0
					string = ""
					string1 = ""
					for key,value in self.last_POST.items():
						i += 1
						j += value
						string += str(value)+"x\t"+key
						for k in range(20-len(key)):
							string += " "
						if((i%2) == 0):
							string += "\n"
						else:
							string += "\t\t"
					print(str(j)+" Messages received")
					print(string)
					self.last_POST = {"/event/location":0,"/event/cherry":0,"/event/energizer":0,"/event/food":0,"/event/collision":0,"/event/quarantine":0,"/event/cherry_spawned":0}
					
					print()
					print("Player Data ("+str(len(self.PlayerData))+")")
					for key, value in self.PlayerData.items():
						string = ""
						for i in range(20-len(key)):
							string += " "
						if(value['energized']):
							key = "E "+key
						else:
							key = "  "+key
						
						try:
							print(key+string+"\tX:"+str(value['x'])+"\tY:"+str(value['y'])+"\tdX:"+str(value['dx'])+"\tdY:"+str(value['dy'])+"\t\tD:"+str(value['distance'])+"\tA:"+str(value['angle'])+"\ttype:"+value['type']+"\tstatus:"+value['status']+"\tScore:"+str(value['score']))
						except:
							pass
					print()
					print("Food ("+str(len(self.food))+") (20 closest to us)")
					string = ""
					i = 0
					for value in self.food:
						i+=1
						string += "X:"+str(value['x'])+"\tY:"+str(value['y'])+"\tD:"+str(value['distance'])+"\tA:"+str(value['angle'])
						
						if i == 20:
							break
						
						if(i % 2 == 0):
							string += "\n"
						else:
							string += "\t\t\t"
					
					print(string)
					print()
					print("Energizer ("+str(len(self.energizer))+")")
					string = ""
					i = 0
					for value in self.energizer:
						i+=1
						string += "X:"+str(value['x'])+"\tY:"+str(value['y'])+"\tD:"+str(value['distance'])+"\tA:"+str(value['angle'])
						if(i == 2):
							i = 0
							string += "\n"
						else:
							string += "\t\t\t"
					
					print(string)
					string1 = "Cherry ("
					string = ""
					i = 0
					for value in self.cherry:
						i += 1
						string += "X:"+str(value['x'])+"\tY:"+str(value['y'])+"\t\ttime:"+str(value['time'])+"\t\ttimestamp:"+str(value['timestamp'])+"\tD:"+str(value['distance'])+"\tA:"+str(value['angle'])
						if(value['active']):
							string += "\tY"
						else:
							string += "\tN"
							
						if((i % 1) == 0):
							string += "\n"
						else:
							string += "\t\t\t"
					string1 += str(i) + ")\n"
					print(string1 + string)
						
				
				time.sleep(0.5)
				self.A += 1
				if(self.A == 10):
					self.A = 0
				
				if(len(self.Message) > 0):
					print(self.Message)
					self.Message = ""
				
				if(self.game_done):
					time.sleep(10)
					#Re-enroll Game
					self.Restart()
		except KeyboardInterrupt:
			raise SystemExit
	
	def Restart(self):
		if(self.Web.register(self) == False):
			print("Failed to register")
			raise SystemExit
		self.game_done = False
		
		for key, value in self.PlayerData.items():
			self.PlayerData[key]['status'] = "Left"
		
		self.score = 0
		self.lives = 3
		
		self.x = 56300
		self.y = 19300
		self.A = -1*self.A
	
	def printPosition(self):
		print("X:{0}\tY:{1}".format(self.x,self.y))

