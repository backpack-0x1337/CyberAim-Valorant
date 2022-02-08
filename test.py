import time

import serial
import aimbotV2
from queue import Queue
from threading import Thread



def move_cursor(arduino, x, y):
    data = str(x) + ':' + str(y)
    arduino.write(data.encode())




def ArduinoThread(arduino_q):
    print('Arduino is listening now')
    arduino = serial.Serial('COM7', 115200, timeout=0)
    # move_cursor(arduino, 100, 100)
    while True:
        print('asd')
        if arduino_q.full():
            x, y, stop = arduino_q.get()
            ori_cur_pos = (0, 0)
            path = aimbotV2.create_path(ori_cur_pos, (x, y), stop)
            for i in range(stop):
                move_cursor(arduino, path[0][i], path[1][i])
                time.sleep(0.00001)
            print('thread End')


def main(arduino_q):
    while True:
        # print("product is running now")
        if arduino_q.empty():
            arduino_q.put((5, 5, 10))
            print("product add to queue")


if __name__ == '__main__':
    thread_kill = False
    # global arduino_q
    # arduino_q = Queue(maxsize=0)
    arduino_q = Queue(maxsize=1)
    try:
        worker = Thread(target=ArduinoThread, args=(arduino_q,))
        worker.setDaemon(True)
        worker.start()
        # with concurrent.futures.ProcessPoolExecutor() as executor:
        #     ArduinoT = executor.submit(ArduinoThread)

        main(arduino_q)
    except KeyboardInterrupt:
        print("Thanks for using cyberAim!")
        thread_kill = True
# talk_to_arduino(100, 100, 10)
