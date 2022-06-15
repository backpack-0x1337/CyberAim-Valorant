import time

# import serial
from queue import Queue
from threading import Thread
# from pynput.mouse import Listener
# from pynput import mouse
# from pynput.mouse import Button, Controller
# from mouse import mouseObj
import keyboard
import win32api
import logging


# from cyberAim_val import recoilCorrection

# logging.basicConfig(level=logging.DEBUG,
#                     format="%(asctime)s - %(levelname)s - %(message)s",
#                     handlers=[
#                         logging.FileHandler("logs/recoil_m.log"),
#                         logging.StreamHandler()
#                     ])


# https://github.com/gggfreak2003/PyHook3/blob/master/example.py

class Weapon:
    def __init__(self, name, sprayPattern, rateOfFire):
        self.name = name
        self.sprayPattern = sprayPattern
        self.rateOfFire = rateOfFire

    def get_correction_by_shots(self, shotNum):
        if shotNum >= len(self.sprayPattern):
            shotNum = len(self.sprayPattern) - 1
        return self.sprayPattern[shotNum]


def recoil_master(recoilCorrection, logger):
    # WEAPONS #
    NoWeapon = Weapon('NoWeapon', [(0, 0)], rateOfFire=1337)
    # Vandal = Weapon('Vandal', [(0,0), (6, 1), (13, 1), (30, 4), (58, 3), (68, 0),(96, 9),(110, 4),(121, 11)], rateOfFire=109)
    Vandal = Weapon('Vandal', [(0,0), (6, 1), (13, 1), (30, 4), (58, 3), (68, 0)], rateOfFire=109)
    # INIT #
    firstShotTime = None
    shotCount = 0
    weapon = Vandal
    while True:
        time.sleep(0.001)
        if win32api.GetAsyncKeyState(0x6E) & 1:
            logger.info(f'asd[RM] Weapon: {weapon.name}')
            if weapon == NoWeapon:
                weapon = Vandal
            else:
                weapon = NoWeapon
            logger.info(f'[RM] Weapon: {weapon.name}')

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
            logger.debug('[RM] LB Pressing')
            # First shot register time
            if firstShotTime is None:
                firstShotTime = time.time_ns()
                shotCount = 1
                continue

        # Main Loop mouse button is clicked

        # ShotTime is not None
        timeSinceFirstShot = (time.time_ns() - firstShotTime) // 1000000
        logger.debug(f'[RM]timeSinceFirstShot:{timeSinceFirstShot}, Shots: {shotCount}')
        # if it's new shot time
        # Empty the recoil var
        while not recoilCorrection.empty():
            recoilCorrection.get()

        if timeSinceFirstShot / weapon.rateOfFire > shotCount:
            shotCount += 1
            # Put the recoil correction for next bullet
            newRecoilCorr = 0, weapon.get_correction_by_shots(shotCount)[0]

            recoilCorrection.put(newRecoilCorr)
            logger.debug(f'\t[RM]RECOIL UPDATED {newRecoilCorr}')
        else:
            logger.debug(f'[RM]RECOIL UNCHANGED')
            recoilCor = 0, weapon.get_correction_by_shots(shotCount)[0]
            recoilCorrection.put(recoilCor)


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
