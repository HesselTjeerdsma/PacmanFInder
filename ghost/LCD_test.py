from LCD_LIB import *

if __name__ == "__main__":
        LCD = Adafruit_CharLCD(25,24,23,17,21,22,2,16)

        LCD.create_char(0,bytearray([0,0,10,31,31,14,4,0]))
        LCD.create_char(1,bytearray([0,0,10,21,17,10,4,0]))
        sleep(1)

#       LCD.message("138\x01\x00")
        while True:
                LCD.set_cursor(0,0)
                LCD.message("PACMAN")

                LCD.set_cursor(12,0)
                LCD.message("4100")

                LCD.set_cursor(0,1)
                LCD.message("QUARANTAINE")

                LCD.set_cursor(13,1)
                LCD.write8(0,True)
                LCD.write8(1,True)
                LCD.write8(1,True)
                sleep(2)

                LCD.clear()

                LCD.set_cursor(0,0)
                LCD.message("GHOST")

                LCD.set_cursor(12,0)
                LCD.message("4200")

                LCD.set_cursor(0,1)
                LCD.message("Left")

                LCD.set_cursor(13,1)
                LCD.write8(0,True)
                LCD.write8(0,True)
                LCD.write8(1,True)

                sleep(2)

                LCD.clear()