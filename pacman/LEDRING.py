import time
from neopixel import *
import math

# LED strip configuration:
LED_COUNT = 16  # Number of LED pixels.
LED_PIN = 18  # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 5  # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0  # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP = ws.WS2811_STRIP_GRB  # Strip type and colour ordering

LED_DEGREE = 0
LED_TOP = 8

def LED_setup():
	strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL,LED_STRIP)
	strip.begin()
	return strip

def LED_show(strip,array):
    for i in range(len(array)):
        strip.setPixelColor(15-i,array[i])
    strip.show()

def LED_unknown(strip,pos):
    strip.setPixelColor(pos, Color(30, 30, 30))
    strip.show()
    print('Unknown appeared')

def LED_pacman(strip,pos):
    strip.setPixelColor(pos, Color(30,15, 0))
    strip.show()
    print('Pacman appeared')

def LED_ghost(strip,pos):
    strip.setPixelColor(pos, Color(0,0,30))
    strip.show()
    print('Ghost appeared')

def LED_degreeToLed(degree):
    degree = degree % 360
    #print(str(degree) + "    " + str(degree/360))
    led =  math.floor(((degree*1000)/360000)*16)
    #led = 15 - led
    #print("Led "+str(led))
    return led

def LED_quarantine(strip):
    for r in range(20):
        for x in range(1,16,2):
            strip.setPixelColor(x, Color(30,0,0))
            strip.setPixelColor(x-1, Color(0,0,0))
        strip.show()
        time.sleep(0.25)
        for y in range(0,16,2):
            strip.setPixelColor(y, Color(30,0,0))
            strip.setPixelColor(y+1, Color(0,0,0))
        strip.show()
        time.sleep(0.25)

def LED_clear(strip):
    for c in range(0,16,1):
        strip.setPixelColor(c, Color(0,0,0))
    strip.show()

if __name__ == '__main__':
    #define strip info
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL,
                              LED_STRIP)
    # Start the library
    strip.begin()

    unknown(strip, degreeToLed(180))
    unknown(strip, degreeToLed(250))
    pacman(strip, degreeToLed(24))
    ghost(strip, degreeToLed(0))
    clear(strip)
    #i = 0
    #while True:
    #    ghost(strip, degreeToLed(i))
    #    i += 20
    #    i = i % 360
    #    time.sleep(0.5)
    #time.sleep(5)
    #quarantaine(strip,10)
