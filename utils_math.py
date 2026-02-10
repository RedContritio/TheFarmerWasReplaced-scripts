# math_utils.py
# 数学工具函数


def sign(x):
    # 返回数字的符号
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0


def clamp(value, min_value, max_value):
    # 将值限制在指定范围内
    if value < min_value:
        return min_value
    elif value > max_value:
        return max_value
    else:
        return value
