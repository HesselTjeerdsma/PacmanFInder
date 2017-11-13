import RPi.GPIO as GPIO
from time import sleep

GPIO.setwarnings(False)
GPIO_VIB = 26
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_VIB, GPIO.OUT)
GPIO.output(GPIO_VIB, 0)

def quarantineVib():
	for v in range(20):
		GPIO.output(GPIO_VIB, 1)
		sleep(0.25)
		GPIO.output(GPIO_VIB, 0)
		sleep(0.25)

def popupVib():
	for v in range(2):
		GPIO.output(GPIO_VIB, 1)
		sleep(0.2)
		GPIO.output(GPIO_VIB, 0)
		sleep(0.1)

def fullVib():
	try:
		while 1:
			GPIO.output(GPIO_VIB, 1)
	except KeyboardInterrupt:
		GPIO.cleanup

if __name__ == '__main__':
	fullVib()
	GPIO.cleanup()
