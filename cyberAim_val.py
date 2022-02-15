import json
import time
import cv2
import numpy as np
import math
import keyboard
import serial
import torch
import aimbotV2
from capture_screen import grab_screen, sct, monitor
from arduino import move_cursor
from util import *
from queue import Queue
from threading import Thread
from pynput.mouse import Listener
from pynput import mouse
from mouse import mouseObj

###################################/ SETTING /###########################################
CONFIDENCE_THRESHOLD = 0.4
ACTIVATION_RANGE = 414  # change this in capture_screen.py
# global SERIAL_PORT
SERIAL_PORT = 'COM7'
MAX_DET = 10  # 5 body and 5 head
AIM_KEY = ['alt', 'ctrl']
AIM_FOV = 100
AIM_IGNORE_PIXEL = 2
AIM_SMOOTH = 4
PT_PATH = 'lib/val-414-train3.pt'
FORCE_RELOAD = False
ALWAYS_ON = True
DISABLE_Y_TIME = 2
DEFAULT_AIM_LOCATION = 'enemyHead'  # 0 is both 1 is head 2 is body


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


def display_fps(frame, start):
    end = time.time()
    fps_label = "FPS: %.2f" % (1 / (end - start))
    cv2.putText(frame, fps_label, (0, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("CyberAim-AI", frame)


def on_click(x, y, button, pressed):
    print(x, y, button, pressed)


def is_button_onclick(x, y, button, pressed):
    current_mouse_status = pressed
    # print(current_mouse_status)


def ArduinoThread():
    global y_disable_bool
    arduino = serial.Serial(SERIAL_PORT, 115200, timeout=0)

    print('Arduino is listening now')
    prev_shots = 0
    last_shot_time = time.time()

    while True:
        x, y, stop = arduino_q.get()
        ori_cur_pos = (0, 0)

        if (time.time() - last_shot_time) > 0.8:
            prev_shots = 0
            last_shot_time = time.time()

        # if 5 <= prev_shots <= 20:
        if 5 <= prev_shots <= 20:
            y = 0 # todo recoil
            # y += 60
            # # x -= 10
            prev_shots += 1
            last_shot_time = time.time()
        else:
            prev_shots += 1


        # print(time.time() - last_shot_time)
        # print(prev_shots)
        # print("\n")


        path = aimbotV2.create_path(ori_cur_pos, (x, y), stop)
        for i in range(stop):
            move_cursor(arduino, path[0][i], path[1][i])
            time.sleep(0.00000001)
        arduino_q.get()
        arduino_q.get()


def main():
    model = torch.hub.load('ultralytics/yolov5', 'custom', path=PT_PATH, force_reload=FORCE_RELOAD)
    model.conf = CONFIDENCE_THRESHOLD
    model.max_det = MAX_DET
    mid_point_screen = int(ACTIVATION_RANGE / 2)
    aim_position = DEFAULT_AIM_LOCATION  # 0 is both 1 is head 2 is body
    prev_aim = False
    global y_disable_bool


    print("Welcome to CyberAim Have Fun!!")
    while True:
        start = time.time()

        frame = np.array(grab_screen(region=monitor))

        results = model(frame)
        target_list = json.loads(results.pandas().xyxy[0].to_json(orient="records"))
        aim_position = get_updated_aim_mode(aim_position)
        target_list = get_scan_list_by_aim_position(aim_position, target_list)

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

            cv2.line(frame, (int(X), int(Y)), (mid_point_screen, mid_point_screen), (0, 255, 0), 1, cv2.LINE_AA)

            cur_X = cur_Y = mid_point_screen
            difX = int(X - mid_point_screen)
            difY = int(Y - mid_point_screen)

            if abs(difX) < AIM_IGNORE_PIXEL and abs(difY) < AIM_IGNORE_PIXEL:
                pass

            elif is_aim_key_pressed() and closestObjectDistance < AIM_FOV:
                if arduino_q.empty() is True:
                    arduino_q.put((difX, difY, AIM_SMOOTH))

            # if not is_aim_key_pressed():
            #     prev_shot = False
        display_fps(frame, start)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            cv2.destroyAllWindows()
            sct.close()
            raise Exception


# arduino_q = Queue(maxsize=0)
# arduino_q = Queue(maxsize=1)
# y_disable_q = Queue(maxsize=1)
if __name__ == '__main__':
    arduino_q = Queue(maxsize=1)
    y_disable_bool = False

    try:
        ArduinoT = Thread(target=ArduinoThread)
        ArduinoT.setDaemon(True)
        ArduinoT.start()
        main()

    except Exception as e:
        print("Thanks for using cyberAim!")
        cv2.destroyAllWindows()
        sct.close()
        exit(0)
