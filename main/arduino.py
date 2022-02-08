

def move_cursor(arduino, x, y):
    data = str(x) + ':' + str(y)
    arduino.write(data.encode())


