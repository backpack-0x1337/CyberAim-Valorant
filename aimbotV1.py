import math
import random
import matplotlib.pyplot as plt
import numpy as np

ori_cur_loc = (0, 0)
enemy_head_local = (100, 100)
enemy_spot = True


# def aimbot():
#     if enemy_spot is True:


def spiral_function(factor_a, factor_b, ori, dest_theta):
    theta = np.linspace(0, dest_theta, 100)

    x_ori, y_ori = ori

    def x_function(theta_n):
        x_path = np.array([]).tolist()
        for items in theta_n:
            x_path.append(factor_a * math.exp(items) * math.cos(items) + x_ori)
        return x_path

    def y_function(theta_n):
        y_path = np.array([]).tolist()
        for items in theta_n:
            y_path.append(factor_b * math.exp(items) * math.sin(items) + y_ori)
        return y_path

    x = x_function(theta)
    y = y_function(theta)
    plt.scatter(x, y)
    plt.show()
    print(x)


def create_path(ori, dest):
    random_theta = random.randint(50, 100)

    print(random_theta)

    x, y = dest

    factor_a = x / (math.exp(-random_theta) * math.cos(random_theta))
    factor_b = y / (math.exp(-random_theta) * math.sin(random_theta))

    # math equation for spiral path
    # x = factor_a * theta * cos(theta)
    # y = factor_b * theta * cos(theta)

    spiral_function(factor_a, factor_b, ori, random_theta)


def aim_smooth(original_cl, destination_cl):
    pass


create_path((0, 0), (12, 23))
