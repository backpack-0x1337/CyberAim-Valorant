import time

import serial
import aimbotV2
from queue import Queue
from threading import Thread
from aimbotV2 import *
from pynput.mouse import Listener
from pynput import mouse
from mouse import mouseObj

# def on_move(x, y):
#     print(x, y)


arduino_port = serial.Serial('COM7', 115200, timeout=0)

m = mouseObj(arduino_port)
listener = mouse.Listener(on_click=m.is_button_onclick)
listener.start()
while True:
    if m.get_mouse_status is True:
        print(1)
        # if 0.5 <= time.time() - m.start_time <= 2.0:
        #     m.move_cursor(0, 5)
        #     time.sleep(0.000001)
