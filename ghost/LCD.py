from time import sleep, strftime
from datetime import datetime

from oled.device import ssd1306, sh1106
from oled.render import canvas
from PIL import ImageFont, ImageDraw, Image

device = ssd1306()  # rev.1 users set port=0

#heartIm = Image.open('heart.png')

def LCD_show(PACMAN):
	with canvas(device) as draw:
		font = ImageFont.truetype("/home/pi/pacman/comic.ttf", 15)
		draw.rectangle((0, 0, device.width, device.height), outline=0, fill=0)
		draw.text((10, 5), '%s'%(PACMAN.type), font=font, fill=255)
		draw.text((20, 25), '%s'%(PACMAN.score), font=font, fill=255)
		
		i = 40
		j = 50
		for q in range(PACMAN.lives):
			draw.polygon(((i+6, j+11), (i+12, j+5), (i+12, j+2), (i+10, j), (i+8, j), (i+6, j+2), (i+4, j), (i+2, j), (i, j+2), (i, j+5)),fill=255)
			i += 15
