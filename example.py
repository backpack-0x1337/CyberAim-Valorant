import time
import cv2
import mss.tools
import numpy as np
import math
import keyboard
import serial
import win32api
import win32con
import win32gui
import win32ui

CONFIDENCE_THRESHOLD = 0.5
NMS_THRESHOLD = 0.5
COLORS = [(0, 255, 255), (255, 255, 0), (0, 255, 0), (255, 0, 0)]

AIMING_POINT = 0  # 0 for "head", 1 for chest, 2 for legs
ACTIVATION_RANGE = 400

arduino = serial.Serial('COM6', 115200, timeout=0)


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


# todo what does this mean
# todo does this matter if we are using yolov5 model
with open("E:/AIstuff/yolov4/coco-dataset.labels", "r") as f:
    class_names = [cname.strip() for cname in f.readlines()]


net = cv2.dnn.readNet("E:/AIstuff/yolov4/yolov4-tiny.weights", "E:/AIstuff/yolov4/yolov4-tiny.cfg")
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

# Todo set model to yov5?
model = cv2.dnn_DetectionModel(net)

# todo Maybe we dont need to set input params for yolo5
model.setInputParams(size=(416, 416), scale=1 / 255, swapRB=True)

while True:
    #start = time.time()

    frame = np.array(grab_screen(region=monitor))

    # todo change to yolov5 format??
    classes, scores, boxes = model.detect(frame, CONFIDENCE_THRESHOLD, NMS_THRESHOLD)

    #for (classID, score, box) in zip(classes, scores, boxes):
    #color = COLORS[int(classID) % len(COLORS)]
    #label = "%s : %f" % (class_names[classID[0]], score)
    #cv2.rectangle(frame, box, color, 2)
    #cv2.putText(frame, label, (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # todo I think boxes is an array and
    # num of enemy boxs
    enemyNum = len(boxes)

    if enemyNum == 0:
        pass
    else:
        # Reset distances array to prevent duplicating items
        distances = []
        closest = 1000
        closestObject = None

        # Cycle through results (enemies) and get the closest to the center of detection box
        for i in range(enemyNum):

            X = float(boxes[i][0])
            Y = float(boxes[i][1])
            width = float(boxes[i][2])
            height = float(boxes[i][3])

            centerX = X + (width / 2)
            centerY = Y + (height / 2)

            distance = math.sqrt(((centerX - ACTIVATION_RANGE / 2) ** 2) + ((centerY - ACTIVATION_RANGE / 2) ** 2))
            distances.append(distance)

            if distances[i] < closest:
                closest = distances[i]
                closestObject = i

        X = float(boxes[closestObject][0])
        Y = float(boxes[closestObject][1])
        width = float(boxes[closestObject][2])
        height = float(boxes[closestObject][3])

        if AIMING_POINT == 0:
            height = (height / 8) * 1

        elif AIMING_POINT == 1:
            height = (height / 8) * 2

        elif AIMING_POINT == 2:
            height = (height / 8) * 5

        cClosestX = X + (width / 2)
        cClosestY = Y + height

        #cv2.line(frame, (int(cClosestX), int(cClosestY)), (int(ACTIVATION_RANGE / 2), int(ACTIVATION_RANGE / 2)),
        #(255, 0, 0), 1, cv2.LINE_AA)

        difX = int(cClosestX - (ACTIVATION_RANGE / 2))
        difY = int(cClosestY - (ACTIVATION_RANGE / 2))

        if abs(difX) < 2 and abs(difY) < 2:
            pass
        else:
            if keyboard.is_pressed('v'):
                data = str(difX) + ':' + str(difY)
                arduino.write(data.encode())

    #end = time.time()
    #fps_label = "FPS: %.2f" % (1 / (end - start))
    #cv2.putText(frame, fps_label, (0, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # cv2.imshow("", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        cv2.destroyAllWindows()
        sct.close()
        break