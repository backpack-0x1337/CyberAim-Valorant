import time

import serial
import aimbotV2
from queue import Queue
from threading import Thread
from aimbotV2 import*




ori = (0,0)
dest = (10,10)
stop = 5
for path in create_path(ori, dest, stop):
    x, y = path
    print("x is {} Y is {}". format(x, y))
