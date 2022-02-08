import json
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
import aimbotV2
from pynput.mouse import Listener
CONFIDENCE_THRESHOLD = 0.5
NMS_THRESHOLD = 0.5
COLORS = [(0, 255, 255), (255, 255, 0), (0, 255, 0), (255, 0, 0)]

AIMING_POINT = 0  # 0 for "head", 1 for chest, 2 for legs
ACTIVATION_RANGE = 400

arduino = serial.Serial('COM7', 115200, timeout=0)


def grab_screen(region=None):
    hwin = win32gui.GetDesktopWindow()

    if region:
        left, top, x2, y2 = region
        widthScr = x2 - left + 1
        heightScr = y2 - top + 1
    else:
        widthScr = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        heightScr = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
        left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
        top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

    hwindc = win32gui.GetWindowDC(hwin)
    srcdc = win32ui.CreateDCFromHandle(hwindc)
    memdc = srcdc.CreateCompatibleDC()
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(srcdc, widthScr, heightScr)
    memdc.SelectObject(bmp)
    memdc.BitBlt((0, 0), (widthScr, heightScr), srcdc, (left, top), win32con.SRCCOPY)

    signedIntsArray = bmp.GetBitmapBits(True)
    img = np.frombuffer(signedIntsArray, dtype='uint8')
    img.shape = (heightScr, widthScr, 4)

    srcdc.DeleteDC()
    memdc.DeleteDC()
    win32gui.ReleaseDC(hwin, hwindc)
    win32gui.DeleteObject(bmp.GetHandle())

    return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)


with mss.mss() as sct:
    # Get the width and height of monitor #n
    Wd, Hd = sct.monitors[1]["width"], sct.monitors[1]["height"]

    # Set monitor rectangle side length
    monitor = (int(Wd / 2 - ACTIVATION_RANGE / 2),
               int(Hd / 2 - ACTIVATION_RANGE / 2),
               int(Wd / 2 + ACTIVATION_RANGE / 2),
               int(Hd / 2 + ACTIVATION_RANGE / 2))


def get_enemy_data_by_key(list, key):
    return list['key']


def get_column_by_key(list, key):
    list = []
    for obj in list:
        for data in obj:
            if data is key:
                pass

def move_cursor(x, y):
    data = str(x) + ':' + str(y)
    arduino.write(data.encode())

def get_center_cord(p1, p2):
    return float((p1 + p2) / 2)

#  set model to yov5
# model = torch.hub.load('ultralytics/yolov5', 'custom', path='lib/val_latest.pt', force_reload=False)
model = torch.hub.load('ultralytics/yolov5', 'custom', path='../lib/aimlab-200.pt', force_reload=False)
model.conf = 0.5
max_det = 10 # 5 body and 5 head

while True:
    start = time.time()

    frame = np.array(grab_screen(region=monitor))

    # todo change to yolov5 format??
    # classes, scores, boxes = model.detect(frame, CONFIDENCE_THRESHOLD, NMS_THRESHOLD)
    results = model(frame)
    json_result = results.pandas().xyxy[0].to_json(orient="records")
    json_result = json.loads(json_result)

    # for (classID, score, box) in zip(classes, scores, boxes):
    # color = COLORS[int(classID) % len(COLORS)]
    # label = "%s : %f" % (class_names[classID[0]], score)
    # cv2.rectangle(frame, box, color, 2)
    # cv2.putText(frame, label, (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    cv2.imshow('CyberAim-AI', np.squeeze(results.render()))
    # num of enemy boxs
    enemyNum = len(json_result)

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
            X = get_center_cord(json_result[i]['xmax'], json_result[i]['xmin'])
            Y = get_center_cord(json_result[i]['ymax'], json_result[i]['ymin'])


            distance = math.sqrt(((X - ACTIVATION_RANGE / 2) ** 2) + ((Y - ACTIVATION_RANGE / 2) ** 2))
            distances.append(distance)
            if distances[i] < closest:
                closest = distances[i]
                closestObject = i
                closestObjectDistance = distance

        X = get_center_cord(json_result[closestObject]['xmax'], json_result[closestObject]['xmin'])
        Y = get_center_cord(json_result[closestObject]['ymax'], json_result[closestObject]['ymin'])


        cv2.line(frame, (int(X), int(Y)), (int(ACTIVATION_RANGE / 2), int(ACTIVATION_RANGE / 2)), (0, 255, 0), 1, cv2.LINE_AA)
        # # (255, 0, 0), 1, cv2.LINE_AA)
        #
        cur_X = cur_Y = (ACTIVATION_RANGE / 2)
        difX = int(X - (ACTIVATION_RANGE / 2))
        difY = int(Y - (ACTIVATION_RANGE / 2))
        #
        if abs(difX) < 2 and abs(difY) < 2:
            pass
        else:
            if keyboard.is_pressed('v') and closestObjectDistance < 50:
                # move_cursor(difX, difY)
                ori_cur_pos = (0, 0)
                stop = 3
                path = aimbotV2.create_path(ori_cur_pos, (difX, difY), stop)
                # path = aimbotV2.straight_path(ori_cur_pos, (difX, difY), stop)
                for i in range(stop):
                    move_cursor(path[0][i], path[1][i])
                    time.sleep(0.00001)


    end = time.time()
    fps_label = "FPS: %.2f" % (1 / (end - start))
    cv2.putText(frame, fps_label, (0, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("CyberAim-AI", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
cv2.destroyAllWindows()
cv2.destroyAllWindows()
sct.close()
