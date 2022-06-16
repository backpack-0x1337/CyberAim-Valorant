import math
import time
from queue import Queue
from threading import Thread
import keyboard
import serial
import win32api
import logging
from playsound import playsound
from tools.recoilConfig import *

# from cyberAim_val import recoilCorrection

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s - %(levelname)s - %(message)s",
                    handlers=[
                        logging.FileHandler("logs/standalone_rcs.log", mode='w'),
                        logging.StreamHandler()
                    ])


def recoil_master():
    # INIT #
    firstShotTime = None
    shotCount = 0
    weapons = [NoWeapon, Vandal, Phantom, Spectre]
    weapon_i = 3

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
