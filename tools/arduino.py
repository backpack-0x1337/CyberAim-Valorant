import time
import serial


def ArduinoThread(arduino_q, recoilCorrection, loggar, SERIAL_PORT):
    arduino = serial.Serial(SERIAL_PORT, 115200, timeout=0)

    loggar.debug('Arduino is listening now')
    while True:

        x, y, stop, mode = arduino_q.get()
        corr_x, corr_y = recoilCorrection.get()

        if mode == "trigger":
            send_trigger_signal(arduino)
            continue
        # path = aimbotV2.create_path((0, 0), (x, y), stop)
        # move_x, move_y = path[0][1], path[1][1]
        # move_x, move_y = aimbotV2.create_path_new((0, 0), (x, y), stop)
        move_x, move_y = int(x / stop), int(y / stop)
        corrected_cord = [move_x + corr_x, move_y + corr_y]
        if corrected_cord[0] >= 127:
            corrected_cord[0] = 127
        if corrected_cord[1] >= 127:
            corrected_cord[1] = 127
        move_cursor(arduino, corrected_cord[0], corrected_cord[1])
        loggar.debug(
            f'[Arduino] AIMBOT put to Queue Cords:{move_x, move_y} corr: {corr_x, corr_y}')


def move_cursor(arduino, x, y):
    data = str(x) + ':' + str(y) + ";0"
    arduino.write(data.encode())


def send_trigger_signal(arduino):
    data = '0:0;1'
    arduino.write(data.encode())
