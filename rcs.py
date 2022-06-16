import time

import math
import time

# import serial
from queue import Queue
from threading import Thread
# from pynput.mouse import Listener
# from pynput import mouse
# from pynput.mouse import Button, Controller
# from mouse import mouseObj
import keyboard
import serial
import win32api
import logging
from playsound import playsound
from tools.recoilConfig import *

# from cyberAim_val import recoilCorrection

# logging.basicConfig(level=logging.DEBUG,
#                     format="%(asctime)s - %(levelname)s - %(message)s",
#                     handlers=[
#                         logging.FileHandler("logs/recoil_m.log"),
#                         logging.StreamHandler()
#                     ])


# https://github.com/gggfreak2003/PyHook3/blob/master/example.py

def recoil_master(recoilCorrection, logger):
    # Vandal = Weapon('Vandal', [(0,0), (6,-1), (15,-4), (20,-4),(30,-9), (30,0)], rateOfFire=9.75)
    # INIT #
    firstShotTime = None
    shotCount = 0
    weapons = [NoWeapon, Vandal, Phantom, Spectre]
    weapon_i = 0
    while True:
        time.sleep(0.001)
        if win32api.GetAsyncKeyState(0x04) & 1 > 0:
            weapon_i += 1
            if weapon_i >= len(weapons):
                weapon_i = 0
            logging.info(f'[RM] Weapon: {weapons[weapon_i].name}')
            weapon_sound = f'./sounds/{weapons[weapon_i].name}.wav'
            playsound(weapon_sound)

        if win32api.GetAsyncKeyState(0x01) & 0x8000 == 0:
            # if not left-click
            # logger.debug('[RM] LB Not Pressing')
            firstShotTime = None
            shotCount = 0
            while not recoilCorrection.empty():
                recoilCorrection.get()
            recoilCorrection.put((0, 0))
            # time.sleep(0.5)
            continue

        if win32api.GetAsyncKeyState(0x01) & 0x8000 > 0:
            # if left-click
            # logging.debug('[RM] LB Pressing')
            # First shot register time
            if firstShotTime is None:
                firstShotTime = time.time_ns()
                shotCount = 1
                continue

        # Main Loop mouse button is clicked

        # ShotTime is not None
        timeSinceFirstShot = (time.time_ns() - firstShotTime) // 1000000
        # logging.debug(f'[RM]timeSinceFirstShot:{timeSinceFirstShot}, Shots: {shotCount}')
        # if it's new shot time
        # Empty the recoil var
        while not recoilCorrection.empty():
            recoilCorrection.get()

        if math.ceil(timeSinceFirstShot / weapons[weapon_i].rateOfFire) >= shotCount:
            shotCount += 1
            # Put the recoil correction for next bullet

            logger.debug(f'[RM]timeSinceFirstShot:{timeSinceFirstShot}, Shots: {shotCount}, calShots: {math.ceil(timeSinceFirstShot / weapons[weapon_i].rateOfFire)}')
            recoilCor = weapons[weapon_i].get_correction_by_shots(shotCount)[1], weapons[weapon_i].get_correction_by_shots(shotCount)[0]
            recoilCorrection.put(recoilCor)
            logger.debug(f'[RM] recoilCor {recoilCor}')
        else:
            # logger.debug(f'[RM]RECOIL UNCHANGED')
            recoilCor = weapons[weapon_i].get_correction_by_shots(shotCount)[1], weapons[weapon_i].get_correction_by_shots(shotCount)[0]
            recoilCorrection.put(recoilCor)
            # recoilCorrection.put((0,0))


# def main():
#     health = 100
#     while True:
#         if not recoilCorrection.empty():
#             damage = recoilCorrection.get()[0]
#         else:
#             damage = 0
#         health -= damage
#         logging.info(f'\t\t[MAIN]Health: {health} Taken Damage: {damage}')
#         if health < 0:
#             print('END GAME')
#             break
#         time.sleep(0.5)
#
#
# if __name__ == '__main__':
#     recoilCorrection = Queue(maxsize=1)
#     recoilThread = Thread(target=recoil_master)
#     recoilThread.start()
#     main()
#     recoilThread.join()
#     print("Finished Executing")
