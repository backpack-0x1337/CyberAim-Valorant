def move_cursor(arduino, x, y):
    data = str(x) + ':' + str(y)
    arduino.write(data.encode())


# def send_trigger_signal(arduino):
#     data = '0:0;1'
#     # arduino.write(data.encode())
