import json
import time
import cv2
import numpy as np
import math
import keyboard
import serial
import torch
import logging
import win32api
import tools.aimbotV2
from tools.capture_screen import grab_screen, sct, monitor
from tools.arduino import *
from tools.util import *
from queue import Queue
from threading import Thread
from rcs import recoil_master, Weapon

# from pynput.mouse import Listener
# from pynput import mouse
# from mouse import mouseObj

###################################/ SETTING /###########################################
CONFIDENCE_THRESHOLD = 0.4
ACTIVATION_RANGE = 414  # change this in capture_screen.py
# global SERIAL_PORT
SERIAL_PORT = 'COM7'
MAX_DET = 10  # 5 body and 5 head
AIM_KEY = ['p']
TRIGGER_KEY = ['alt']
AIM_FOV = 200
AIM_SMOOTH = 5
MAGNET_PIXEL = 70
PT_PATH = 'lib/val414-n.pt'
# PT_PATH = 'lib/val-414-train3.pt'
# PT_RE_PATH = 'lib/reinforce-model1800.pt'
FORCE_RELOAD = False
ALWAYS_ON = False
DEFAULT_AIM_LOCATION = 'enemyHead'  # 0 is both 1 is head 2 is body
DEBUG = True
# MOVEMENT_MAX_PIXEL = 15
TRIGGER_PIXEL = 5

if DEBUG is True:
    loggingStatus = logging.DEBUG
else:
    loggingStatus = logging.INFO

logging.basicConfig(level=loggingStatus,
                    format="%(asctime)s - %(levelname)s - %(message)s",
                    handlers=[
                        logging.FileHandler("logs/recoil_m.log"),
                        logging.StreamHandler()
                    ])

loggar = logging.getLogger(__name__)
loggar.level = loggingStatus

handler = logging.FileHandler("logs/recoil_m.log")
handler2 = logging.StreamHandler()

handler.setLevel(loggingStatus)
handler2.setLevel(loggingStatus)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
handler2.setFormatter(formatter)
loggar.addHandler(handler)
loggar.addHandler(handler2)


##################################/ Function /##############################################


def get_updated_aim_mode(aim_mode):
    if keyboard.is_pressed('7'):
        aim_mode = "ALL"
        print("AIM-MODE: {}".format(aim_mode))
    elif keyboard.is_pressed('8'):
        aim_mode = "enemyHead"
        print("AIM-MODE: {}".format(aim_mode))
    elif keyboard.is_pressed('9'):
        aim_mode = "enemyBody"
        print("AIM-MODE: {}".format(aim_mode))
    return aim_mode


def get_scan_list_by_aim_position(aim_position, json_result):
    if aim_position == 'ALL':
        return json_result
    elif aim_position == "enemyHead" or aim_position == "enemyBody":
        return get_list_by_classname(json_result, aim_position)
    else:
        return []


def is_aim_key_pressed():
    for key in AIM_KEY:
        if keyboard.is_pressed(key):
            return True
    return False


def is_trigger_button_pressed():
    for key in TRIGGER_KEY:
        if keyboard.is_pressed(key):
            return True
    return False


def display_fps(frame, start):
    end = time.time()
    fps_label = "FPS: %.2f" % (1 / (end - start))
    cv2.putText(frame, fps_label, (0, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("CyberAim-AI", frame)



def object_detection(arduino_q):
    model = torch.hub.load('ultralytics/yolov5', 'custom', path=PT_PATH, force_reload=FORCE_RELOAD)
    model.conf = CONFIDENCE_THRESHOLD
    model.max_det = MAX_DET
    model.classes = 1  # head detection only
    mid_point_screen = int(ACTIVATION_RANGE / 2)
    aim_position = DEFAULT_AIM_LOCATION  # 0 is both 1 is head 2 is body

    print("Welcome to CyberAim Have Fun!!")
    while True:
        start = time.time()
        frame = np.array(grab_screen(region=monitor))
        results = model(frame)
        target_list = json.loads(results.pandas().xyxy[0].to_json(orient="records"))
        # aim_position = get_updated_aim_mode(aim_position)
        # target_list = get_scan_list_by_aim_position(aim_position, target_list)
        if DEBUG:
            cv2.imshow('CyberAim-AI', np.squeeze(results.render()))
        # num of enemy boxs
        enemyNum = len(target_list)
        if enemyNum == 0:
            pass
        else:
            # Reset distances array to prevent duplicating items
            distances = []
            closest = 1000
            closestObject = None
            closestObjectDistance = None
            # Cycle through results (enemies) and get the closest to the center of detection box
            for i in range(enemyNum):
                X = get_center_cord(target_list[i]['xmax'], target_list[i]['xmin'])
                Y = get_center_cord(target_list[i]['ymax'], target_list[i]['ymin'])

                distance = math.sqrt(((X - ACTIVATION_RANGE / 2) ** 2) + ((Y - ACTIVATION_RANGE / 2) ** 2))
                distances.append(distance)
                if distances[i] < closest:
                    closest = distances[i]
                    closestObject = i
                    closestObjectDistance = distance

            X = get_center_cord(target_list[closestObject]['xmax'], target_list[closestObject]['xmin'])
            Y = get_center_cord(target_list[closestObject]['ymax'], target_list[closestObject]['ymin'])
            targetSize_x = (target_list[closestObject]['xmax'] - target_list[closestObject]['xmin']) * 0.8
            targetSize_y = (target_list[closestObject]['ymax'] - target_list[closestObject]['ymin']) * 0.8
            cv2.line(frame, (int(X), int(Y)), (mid_point_screen, mid_point_screen), (0, 255, 0), 1, cv2.LINE_AA)

            difX = int(X - mid_point_screen)
            difY = int(Y - mid_point_screen)

            if is_trigger_button_pressed() and abs(difX) < TRIGGER_PIXEL and abs(difY) < TRIGGER_PIXEL:
                # print(targetSize)
                arduino_q.put((0, 0, 2, 'trigger'))
                loggar.debug('[MAIN] Sent Trigger Signal')
                continue

            if abs(difX) < targetSize_x and abs(difY) < targetSize_y:
                pass

            elif (is_aim_key_pressed() and closestObjectDistance < AIM_FOV) or ALWAYS_ON:
                # while not arduino_q.empty():  # empty the list so we can update it
                #     arduino_q.get()
                # if recoilCorrection.full():
                #     corr_x, corr_y = recoilCorrection.get()
                # else:
                #     corr_x, corr_y = 0, 0
                #     logger.warning("[MAIN] Recoil Queue is empty")

                if closestObjectDistance < MAGNET_PIXEL:
                    arduino_q.put((difX, difY, 1, 'aimbot'))
                    # loggar.debug(
                    #     f'[MAIN] AIMBOT put to Queue Cords:{difX, difY}, Smooth{1},'
                    #     f' Target Distance:{closestObjectDistance}')
                else:
                    arduino_q.put((difX, difY, AIM_SMOOTH, 'aimbot'))
                    # loggar.debug(
                    #     f'[MAIN] AIMBOT put to Queue Cords:{difX, difY} Smooth{AIM_SMOOTH},'
                    #     f' Target Distance:{closestObjectDistance}')

        if DEBUG:
            display_fps(frame, start)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            cv2.destroyAllWindows()
            sct.close()
            raise Exception


def main():
    arduino_q = Queue(maxsize=5)
    recoilCorrection = Queue(maxsize=5)
    try:
        ArduinoT = Thread(target=ArduinoThread, args=(arduino_q, recoilCorrection, loggar, SERIAL_PORT))
        RecoilThread = Thread(target=recoil_master, args=(recoilCorrection, loggar,))
        RecoilThread.setDaemon(True)
        ArduinoT.setDaemon(True)
        ArduinoT.start()
        loggar.info(f'Arduino Thread Started')
        RecoilThread.start()
        loggar.info(f'Recoil Master Thread Started')
        object_detection(arduino_q)

    except Exception as e:
        print(e)
        print("Thanks for using cyberAim!")
        cv2.destroyAllWindows()
        sct.close()
        exit(0)


if __name__ == '__main__':
    main()
