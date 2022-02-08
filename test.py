import json
import os
import time
import cv2
import mss.tools
import numpy as np
import math
import keyboard
import serial
import torch
import win32api
import win32con
import win32gui
import win32ui
from pynput.mouse import Listener

import aimbotV2


from pynput import mouse

def on_click(x, y, button, pressed):
    if button == mouse.Button.left:
        print('{} at {}'.format('Pressed Left Click' if pressed else 'Released Left Click', (x, y)))
        return False # Returning False if you need to stop the program when Left clicked.
    else:
        print('{} at {}'.format('Pressed Right Click' if pressed else 'Released Right Click', (x, y)))


while True:
    listener = mouse.Listener(on_click=on_click)
    listener.start()
    listener.join()
    print(1)
    # continue
