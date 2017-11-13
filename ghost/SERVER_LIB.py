import requests
import json
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
from time import sleep
from PACMAN import *

ADDR = ""   #optional localhost
PORT = 50001

GAME = PACMAN()

class requestHandler(BaseHTTPRequestHandler):
	def do_POST(self):
		try:
			#Get the length of the received payload
			length = int(self.headers['Content-length'])
		
			#Read and decode payload
			data = json.loads(self.rfile.read(length).decode())
		
			#Proccess data
			(reply, type) = GAME.newPOST(self.path,data);
		
			#Set response code and Content type
			self.send_response(200)		
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
		
			#Write payload to connection
			self.wfile.write(str(json.dumps(reply)).encode())
		except:
			raise SystemExit
		
	def log_message(self, format, *args):
		try:
			GAME.last_POST[self.path] += 1
		except KeyError:
			print("KeyError last_POST")
			print(self.path)
		return


class WebServer(object):
	def __init__(self,ADDR,PORT):
		#Start HTTP Server on ADDR:PORT, with the requestHandler class
		self.httpd = HTTPServer((ADDR, PORT), requestHandler)
		
	def register(self,GAME):
		# Request a registration from the PACMAN service
		print("Register")
		reg = requests.post('http://pacman.autonomic-networks.ele.tue.nl/register', json={"name":GAME.name})
		#reg = requests.post('http://127.0.0.1/register', json={"name":GAME.name})
		
		return GAME.loadRegistration(reg) #Save registration data in Object
	
	def run(self):
		while True:
			self.httpd.handle_request()
			sleep(0.05)
