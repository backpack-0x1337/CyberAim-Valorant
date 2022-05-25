import time


def move_cursor(arduino, x, y):
    data = str(x) + ':' + str(y) + ";0"
    arduino.write(data.encode())
    arduino.flush()


def send_trigger_signal(arduino):
    data = '0:0;1'
    arduino.write(data.encode())
    data = '0:0;3'
    arduino.write(data.encode())
