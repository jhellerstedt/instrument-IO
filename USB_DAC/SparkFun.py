
'''
commands can be found here:
https://www.sparkfun.com/datasheets/DevTools/Arduino/SerIO%20User%20Guide.pdf

tl;dr
ser.write(b'W,<channel#>,<0-255>\r') -> set D <channel#> to voltage, where 0-255 maps to 0-3.3V
'''

from threading import Thread
import time
import serial

global value

def thread2(threadname):
# this thread opens the serial to comm w the SparkIO and writes some value 
          global value
          ser = serial.Serial(
          port='/dev/cu.usbserial-A10134HX',
          baudrate=57600,
          parity=serial.PARITY_NONE,
          stopbits=serial.STOPBITS_ONE,
          bytesize=serial.EIGHTBITS
          )

          ser.isOpen()
          ser.write(b'W,11,0\r')

          while True:
                 to_write = 'W,8,'+str(value)+'\r'
                 to_write = bytes(to_write)
                 ser.write(to_write)
                 time.sleep(2.0)

thread2 = Thread( target=thread2, args=("Thread-2", ) )

thread2.start()

thread2.join()