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

# from cyberAim_val import recoilCorrection

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s - %(levelname)s - %(message)s",
                    handlers=[
                        logging.FileHandler("logs/standalone_rcs.log", mode='w'),
                        logging.StreamHandler()
                    ])


# https://github.com/gggfreak2003/PyHook3/blob/master/example.py

class Weapon:
    def __init__(self, name, sprayPattern, rateOfFire):
        self.name = name
        self.sprayPattern = sprayPattern
        self.rateOfFire = 1000 / rateOfFire

    def get_correction_by_shots(self, shotNum):
        if shotNum >= 11:
            shotNum = 0
        elif shotNum >= len(self.sprayPattern):
            shotNum = len(self.sprayPattern) - 1

        return self.sprayPattern[shotNum]


def recoil_master():
    # WEAPONS #
    NoWeapon = Weapon('NoWeapon', [(0, 0)], rateOfFire=1337)
    # Vandal = Weapon('Vandal', [(0,0), (6, 1), (13, 1), (30, 4), (58, 3), (68, 0),(96, 9),(110, 4),(121, 11)], rateOfFire=109)
    Vandal = Weapon('Vandal',
                    [(0, 0), (6, -1), (7, -1), (13, -4), (28, -3), (30, -1), (28, 9), (30, -4), (30, -11), (30, 0)],
                    rateOfFire=9.75)
    Phantom = Weapon('Phantom',
                     [(0, 0), (6, -1), (7, -1), (17, -1), (28, 0), (30, -1), (28, 0), (25, -4), (25, 0), (25, 0)],
                     rateOfFire=11)
    # Vandal = Weapon('Vandal', [(0,0), (6,-1), (15,-4), (20,-4),(30,-9), (30,0)], rateOfFire=9.75)
    # INIT #
    firstShotTime = None
    shotCount = 0
    weapons = [NoWeapon, Vandal, Phantom]
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
            # time.sleep(0.5)
            continue

        if win32api.GetAsyncKeyState(0x01) & 0x8000 > 0:
            # if left-click
            # logging.debug('[RM] LB Pressing')
            # First shot register time
            if firstShotTime is None:
                firstShotTime = time.time_ns()
                shotCount = 0
                continue

        # Main Loop mouse button is clicked

        # ShotTime is not None
        timeSinceFirstShot = (time.time_ns() - firstShotTime) // 1000000
        # logging.debug(f'[RM]timeSinceFirstShot:{timeSinceFirstShot}, Shots: {shotCount}')
        # if it's new shot time

        if math.ceil(timeSinceFirstShot / weapons[weapon_i].rateOfFire) >= shotCount:
            shotCount += 1
            # Put the recoil correction for next bullet
            logging.debug(f'[RM]timeSinceFirstShot:{timeSinceFirstShot}, Shots: {shotCount}')
            newRecoilCorr = str(weapons[weapon_i].get_correction_by_shots(shotCount)[1]) + ':' + str(
                weapons[weapon_i].get_correction_by_shots(shotCount)[0])
            data = newRecoilCorr + ";0"
            arduino.write(data.encode())
            logging.debug(f'\t[RM] Moved {newRecoilCorr}')


if __name__ == '__main__':
    arduino = serial.Serial('COM7', 115200, timeout=0)
    recoil_master()
    print("Finished Executing")
