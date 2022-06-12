import time


class mouseObj:
    current_mouse_status = False
    arduino = None
    mouse_hold_counter = 0
    prev_click_status = False

    def __init__(self, arduino):
        self.arduino = arduino
        self.current_mouse_status = False
        self.start_time = 0

    def on_click(x, y, button, pressed):
        print(x, y, button, pressed)

    def is_button_onclick(self, x, y, button, pressed):
        self.current_mouse_status = pressed

        print(pressed)

        if pressed is True:
            self.start_time = time.time()

        else:
            self.start_time = 0

    def move_cursor(self, x, y):
        data = str(x) + ':' + str(y)
        self.arduino.write(data.encode())

    def get_mouse_status(self):
        return self.current_mouse_status
