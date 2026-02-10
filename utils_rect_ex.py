# rect_utils_ex.py
# 矩形扩展操作和复杂逻辑
# 包含完整的边界检查和错误处理

from utils_rect import rectangle_can_contain


def rectangles_intersect(rect1, rect2):
    # 判断两个矩形是否相交
    y1, x1, h1, w1 = rect1
    y2, x2, h2, w2 = rect2

    # 有效性检查
    if h1 <= 0 or w1 <= 0 or h2 <= 0 or w2 <= 0:
        return False

    # 检查是否不相交
    no_intersect = y1 + h1 <= y2 or y2 + h2 <= y1 or x1 + w1 <= x2 or x2 + w2 <= x1

    return not no_intersect


def rectangles_adjacent(rect1, rect2):
    # 判断两个矩形是否相邻（可合并）
    y1, x1, h1, w1 = rect1
    y2, x2, h2, w2 = rect2

    # 有效性检查
    if h1 <= 0 or w1 <= 0 or h2 <= 0 or w2 <= 0:
        return False

    # 水平相邻且高度相同
    if y1 == y2 and h1 == h2:
        if x1 + w1 == x2 or x2 + w2 == x1:
            return True

    # 垂直相邻且宽度相同
    if x1 == x2 and w1 == w2:
        if y1 + h1 == y2 or y2 + h2 == y1:
            return True

    return False


def rectangle_merge(rect1, rect2):
    # 合并两个相邻矩形
    # 前提：rectangles_adjacent(rect1, rect2) == True
    y1, x1, h1, w1 = rect1
    y2, x2, h2, w2 = rect2

    # 水平相邻
    if y1 == y2 and h1 == h2:
        new_x = x1
        if x2 < x1:
            new_x = x2
        new_w = w1 + w2
        return (y1, new_x, h1, new_w)

    # 垂直相邻
    new_y = y1
    if y2 < y1:
        new_y = y2
    new_h = h1 + h2
    return (new_y, x1, new_h, w1)


def rectangle_subtract(rect, used_rect):
    # 从一个矩形中减去已使用的部分
    # 返回剩余的空闲矩形列表（0-4个矩形）
    y, x, h, w = rect
    uy, ux, uh, uw = used_rect

    # 如果不相交，直接返回原矩形
    if not rectangles_intersect(rect, used_rect):
        result = []
        result.append(rect)
        return result

    # 计算相交区域的边界
    iy = y
    if uy > iy:
        iy = uy
    ix = x
    if ux > ix:
        ix = ux

    iy_end = y + h
    uy_end = uy + uh
    if uy_end < iy_end:
        iy_end = uy_end

    ix_end = x + w
    ux_end = ux + uw
    if ux_end < ix_end:
        ix_end = ux_end

    intersect_h = iy_end - iy
    intersect_w = ix_end - ix

    # 如果没有实际相交区域
    if intersect_h <= 0 or intersect_w <= 0:
        result = []
        result.append(rect)
        return result

    # 切割出剩余部分
    result = []

    # 左侧剩余（在相交区域左侧）
    if x < ix:
        result.append((y, x, h, ix - x))

    # 右侧剩余（在相交区域右侧）
    if ix_end < x + w:
        result.append((y, ix_end, h, x + w - ix_end))

    # 顶部剩余（在相交区域上方）
    if y < iy:
        result.append((y, ix, iy - y, intersect_w))

    # 底部剩余（在相交区域下方）
    if iy_end < y + h:
        result.append((iy_end, ix, y + h - iy_end, intersect_w))

    return result


def rectangle_find_placement(rect, h, w, strategy="bottom_left"):
    # 在矩形内寻找放置位置
    # 坐标系：y向上，x向右
    if not rectangle_can_contain(rect, h, w):
        return None

    y, x, rect_h, rect_w = rect

    if strategy == "bottom_left":
        return (y, x, h, w)
    elif strategy == "bottom_right":
        return (y, x + rect_w - w, h, w)
    elif strategy == "top_left":
        return (y + rect_h - h, x, h, w)
    elif strategy == "top_right":
        return (y + rect_h - h, x + rect_w - w, h, w)

    return None


def rectangle_filter_fit_rects(rects, h, w):
    # 过滤出能容纳指定大小的矩形
    result = []
    for rect in rects:
        if rectangle_can_contain(rect, h, w):
            result.append(rect)
    return result


def rectangle_get_best_fit(rects, h, w, strategy="best_area_fit"):
    # 从能容纳的矩形中选择最佳匹配
    fit_rects = rectangle_filter_fit_rects(rects, h, w)
    if len(fit_rects) == 0:
        return None

    best_rect = None
    best_score = 0

    for rect in fit_rects:
        rect_h, rect_w = rect[2], rect[3]

        if strategy == "best_area_fit":
            score = rect_h * rect_w - h * w  # 面积浪费
        elif strategy == "best_short_side_fit":
            short_a = rect_h - h
            short_b = rect_w - w
            score = short_a
            if short_b < short_a:
                score = short_b
        elif strategy == "best_long_side_fit":
            long_a = rect_h - h
            long_b = rect_w - w
            score = long_a
            if long_b > long_a:
                score = long_b
        else:  # first_fit
            return rect

        if best_rect == None:
            best_rect = rect
            best_score = score
        else:
            if score < best_score:
                best_rect = rect
                best_score = score

    return best_rect


def rectangle_merge_all(rects):
    # 合并列表中所有相邻矩形
    if len(rects) <= 1:
        # 创建副本返回
        result = []
        for rect in rects:
            result.append(rect)
        return result

    # 工作列表
    work_list = []
    for rect in rects:
        work_list.append(rect)

    merged = True
    while merged and len(work_list) > 1:
        merged = False
        new_list = []

        while len(work_list) > 0:
            current = work_list.pop(0)
            found_merge = False

            # 尝试与后续矩形合并
            i = 0
            while i < len(work_list):
                other = work_list[i]
                # 检查是否相邻
                if rectangles_adjacent(current, other):
                    merged_rect = rectangle_merge(current, other)
                    if merged_rect != None:
                        # 成功合并
                        work_list.pop(i)
                        new_list.append(merged_rect)
                        found_merge = True
                        merged = True
                        break
                i += 1

            if not found_merge:
                new_list.append(current)

        work_list = new_list

    return work_list
