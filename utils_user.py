# utils_user.py
# 用户常用移动封装

from utils_point import point_subtract
from utils_route import vector_get_path
from utils_move import path_move_along


def move_to(y, x):
    # 从当前位置移动到目标格 (y, x)，先走 y 再走 x
    cy = get_pos_y()
    cx = get_pos_x()
    vec = point_subtract((y, x), (cy, cx))
    path = vector_get_path(vec)
    path_move_along(path)
