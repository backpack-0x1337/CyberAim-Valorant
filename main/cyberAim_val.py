import json
import threading
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

###################################/ SETTING /###########################################
CONFIDENCE_THRESHOLD = 0.6
ACTIVATION_RANGE = 414  # change this in capture_screen.py
SERIAL_PORT = 'COM9'
MAX_DET = 10  # 5 body and 5 head
AIM_KEY = ['shift', 'alt', 'ctrl']
AIM_FOV = 50
AIM_IGNORE_PIXEL = 10
AIM_SMOOTH = 5

##################################/ Function /##############################################


def get_updated_aim_mode(aim_mode):
    if keyboard.is_pressed('0'):
        aim_mode = "ALL"
    elif keyboard.is_pressed('1'):
        aim_mode = "enemyHead"
    elif keyboard.is_pressed('2'):
        aim_mode = "enemyBody"
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


def talk_to_arduino(x, y, stop):
    ori_cur_pos = (0, 0)
    path = aimbotV2.create_path(ori_cur_pos, (x, y), stop)
    for i in range(stop):
        move_cursor(arduino, path[0][i], path[1][i])
    time.sleep(0.00001)


######################################/ Global Var /###############################################
arduino = serial.Serial(SERIAL_PORT, 115200, timeout=0)
model = torch.hub.load('ultralytics/yolov5', 'custom', path='../lib/valorant-414-ss-train2.pt', force_reload=False)
model.conf = CONFIDENCE_THRESHOLD
model.max_det = MAX_DET
mid_point_screen = int(ACTIVATION_RANGE / 2)
# aim_position = 'ALL'  # 0 is both 1 is head 2 is body
print("Welcome to CyberAim Have Fun!!")
thread_flag = 'free'


def main():
    aim_position = 'ALL' # 0 is both 1 is head 2 is body
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

            cv2.line(frame, (int(X), int(Y)), mid_point_screen, mid_point_screen, (0, 255, 0), 1, cv2.LINE_AA)

            cur_X = cur_Y = mid_point_screen
            difX = int(X - mid_point_screen)
            difY = int(Y - mid_point_screen)

            if abs(difX) < AIM_IGNORE_PIXEL and abs(difY) < AIM_IGNORE_PIXEL:
                pass
            else:
                if (is_aim_key_pressed()) and closestObjectDistance < AIM_FOV:
                    # move_cursor(arduino, difX, difY)

                    # ori_cur_pos = (0, 0)
                    # path = aimbotV2.create_path(ori_cur_pos, (difX, difY), stop
                    arduino_thread = threading.Thread(target=talk_to_arduino, args=[difX, difY, AIM_SMOOTH])
                    arduino_thread.start()
                    # for i in range(5):
                    #     to_moveX = path[0][i]
                    #     to_moveY = path[1][i]
                    #     move_cursor(path[0][i], path[1][i])
                    # time.sleep(0.00001)

        display_fps(frame, start)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cv2.destroyAllWindows()
    sct.close()
    exit(0)


if __name__ == '__main__':

    main()