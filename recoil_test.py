import time

# import serial
import aimbotV2
from queue import Queue
from threading import Thread
from aimbotV2 import *
# from pynput.mouse import Listener
# from pynput import mouse
# from pynput.mouse import Button, Controller
# from mouse import mouseObj
import win32api
import logging

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s",
                    handlers=[
                        logging.FileHandler("logging/recoil_m.log"),
                        logging.StreamHandler()
                    ])

# https://github.com/gggfreak2003/PyHook3/blob/master/example.py

class Weapon:
    def __init__(self, name, sprayPattern, rateOfFire):
        self.name = name
        self.sprayPattern = sprayPattern
        self.rateOfFire = rateOfFire

    def get_next_correction(self):
        return 0, 0


def recoil_master():
    firstShotTime = None
    shotCount = 0

    while True:
        vandal = Weapon('Vandal', [(0, 0), (10, 0), (10, 0), (10, 0), (10, 0)], rateOfFire=109)

        if win32api.GetAsyncKeyState(0x01) & 0x8000 == 0:
            print('LB Not Pressing')
            firstShotTime = None
            shotCount = 0
            time.sleep(1)
            continue

        if win32api.GetAsyncKeyState(0x01) & 0x8000 > 0:
            print('LB Pressing')
            time.sleep(1)

        # Main Loop mouse button is clicked

        # First shot register time
        if firstShotTime is None:
            # print('')
            firstShotTime = time.time_ns()
            shotCount = 1
            continue

        # ShotTime is not None
        timeSinceFirstShot = (time.time_ns() - firstShotTime) // 1000000
        print(f'timeSinceFirstShot:{timeSinceFirstShot}, Shots: {shotCount}')
        # if it's new shot time
        if timeSinceFirstShot / vandal.rateOfFire > shotCount:

            shotCount += 1

            # Empty the recoil var
            while recoilCorrection.full():
                recoilCorrection.get()

            # Put the recoil correction for next bullet
            try:
                newRecoilCorr = vandal.sprayPattern[shotCount]
            except IndexError:
                newRecoilCorr = vandal.sprayPattern[-1]

            recoilCorrection.put(newRecoilCorr)
            print(f'RECOIL UPDATED {newRecoilCorr}')
        else:
            print(f'RECOIL UNCHANGED')
            if not recoilCorrection.full():
                recoilCor = vandal.sprayPattern[shotCount]
                recoilCorrection.put(recoilCor)


def main():
    pass


if __name__ == '__main__':
    recoilCorrection = Queue(maxsize=1)
    recoilThread = Thread(target=recoil_master)
    recoilThread.start()
    main()
    recoilThread.join()
    print("Finished Executing")
