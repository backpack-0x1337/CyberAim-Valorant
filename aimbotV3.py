import math
import random
import matplotlib.pyplot as plt
import numpy as np

ori_cur_loc = (0, 0)
enemy_head_local = (100, 100)
enemy_spot = True


# https://www.youtube.com/watch?v=pnYccz1Ha34

# def spiral_function(ori, middle, dest, t):
#     point = ((1 - t) ** 2) * ori + 2 * (1 - t) * t * middle + (t ** 2) * dest
#     return point

def spiral_function(ori, p1, p2, dest, t):
    x = 1 - t
    point = ((x**3) * ori) + (3 * (x**2) * t * p1) + (3 * x * (t**2) * p2) + ((t**3) + dest)
    return point


def create_path(ori, dest):
    ########################################################################################
    time_range = np.linspace(0, 1, 100)

    x_ori, y_ori = ori
    x_dest, y_dest = dest

    p2_x = random.randint(x_ori, x_dest)
    p2_y = random.randint(y_ori, y_dest)

    p1_x = random.randint(x_ori, p2_x)
    p1_y = random.randint(y_ori, p2_y)

    ########################################################################################
    x_path = np.array([]).tolist()
    y_path = np.array([]).tolist()

    for t in time_range:
        x_path.append(spiral_function(x_ori, p1_x, p2_x, x_dest, t))
        y_path.append(spiral_function(y_ori, p1_y, p2_y, y_dest, t))

    temp = [(x_ori, y_ori), (p1_x, p1_y), (p2_x, p2_y)]
    # plt.scatter(x_path, y_path)
    plt.scatter((x_ori, y_ori),(p1_x, p1_y),(p2_x, p2_y))
    plt.show()




create_path((0, 0), (12, 23))