import mouse
import win32api

while True:
    if win32api.GetAsyncKeyState(0x01) & 0x8000 > 0:
        print(mouse.get_position())