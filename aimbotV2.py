import math
import random
import matplotlib.pyplot as plt
import numpy as np


# https://www.youtube.com/watch?v=pnYccz1Ha34

def spiral_function(ori, middle, dest, t):
    point = ((1 - t) ** 2) * ori + 2 * (1 - t) * t * middle + (t ** 2) * dest
    return point

def get_random_between(p1, p2):
    if p1 > p2:
        return random.randint(p2, p1)
    elif p2 > p1:
        return random.randint(p1, p2)
    else:
        # == 0
        return 0


def straight_path(ori, dest, stop):
    x_path = []
    y_path = []

    lengthX = dest[0] - ori[0]
    lengthY = dest[1] - ori[1]
    diffX = lengthX / stop
    diffY = lengthY / stop
    for i in range(stop):
        x_path.append(diffX)
        y_path.append(diffY)
    return x_path, y_path



def create_path(ori, dest, stop):
    time_range = np.linspace(0, 1, stop)

    x_ori, y_ori = ori
    x_dest, y_dest = dest

    # x_path = np.array([]).tolist()
    # y_path = np.array([]).tolist()
    x_path = []
    y_path = []

    middle_x = get_random_between(x_ori, x_dest)
    middle_y = get_random_between(y_ori, y_dest)

    pre_cord_x = 0
    pre_cord_y = 0

    for t in time_range:
        # pre_cord_x = cord_diff_x = spiral_function(x_ori, middle_x, x_dest, t) - pre_cord_x
        # pre_cord_y = cord_diff_y = spiral_function(y_ori, middle_y, y_dest, t) - pre_cord_y

        if t == 1:
            cord_diff_x = spiral_function(x_ori, middle_x, x_dest, t) - pre_cord_x
            pre_cord_x += cord_diff_x
            cord_diff_y = spiral_function(y_ori, middle_y, y_dest, t) - pre_cord_y
            pre_cord_y += cord_diff_y
        else:
            cord_diff_x = spiral_function(x_ori, middle_x, x_dest, t) - pre_cord_x + random.randint(1, 9) / 100
            pre_cord_x += cord_diff_x
            cord_diff_y = spiral_function(y_ori, middle_y, y_dest, t) - pre_cord_y + random.randint(1, 9) / 100
            pre_cord_y += cord_diff_y

        x_path.append(cord_diff_x)
        y_path.append(cord_diff_y)

    # plt.scatter(x_path, y_path)
    # plt.show()
    return x_path, y_path


# create_path((0, 0), (10, 0), 10)


# print(create_path((0, 0), (12, 23), 10)[0][1])
# print(straight_path((0, 0), (100, 100), 10)[0][1])
