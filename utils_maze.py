# maze_utils.py
# 迷宫相关工具函数

from utils_area import area_get_attr, area_set_attr, area_contains_point
from utils_direction import direction_to_vector2d, direction_negate
from utils_point import point_add, point_subtract, vector_len

DIRECTIONS = [West, East, North, South]


def maze_get_next_position(point, direction):
    # 获取指定方向的下一个位置
    vec = direction_to_vector2d(direction)
    return point_add(point, vec)


def maze_manhattan_distance(p1, p2):
    # 曼哈顿距离
    vec = point_subtract(p1, p2)
    return vector_len(vec)


def maze_update_wall_pairly(area, point, direction, move_attr):
    # 成对更新墙属性（双向）
    area_set_attr(area, direction, point, move_attr)

    next_point = maze_get_next_position(point, direction)
    if area_contains_point(area, next_point):
        opposite_dir = direction_negate(direction)
        area_set_attr(area, opposite_dir, next_point, move_attr)


def maze_get_path_common_ancestor(node_len_dir_from, s, t):
    # 找最近公共祖先
    if s not in node_len_dir_from or t not in node_len_dir_from:
        return None

    while s != t:
        if node_len_dir_from[t][0] > node_len_dir_from[s][0]:
            parent = node_len_dir_from[t][2]
            if parent == None:
                return t
            t = parent
        else:
            parent = node_len_dir_from[s][2]
            if parent == None:
                return s
            s = parent

    return s


def maze_get_path(node_len_dir_from, sy, sx, ty, tx):
    # 还原路径
    root = maze_get_path_common_ancestor(node_len_dir_from, (sy, sx), (ty, tx))
    if root == None:
        return None

    path = []
    cy, cx = sy, sx

    while (cy, cx) != root:
        d = direction_negate(node_len_dir_from[(cy, cx)][1])
        path.append(d)
        cy, cx = node_len_dir_from[(cy, cx)][2]

    cy, cx = ty, tx
    reverse_path = []

    while (cy, cx) != root:
        d = node_len_dir_from[(cy, cx)][1]
        reverse_path.append(d)
        cy, cx = node_len_dir_from[(cy, cx)][2]

    reverse_path_len = len(reverse_path)
    for i in range(reverse_path_len):
        path.append(reverse_path[reverse_path_len - 1 - i])

    return path


def maze_search(area, sy, sx, ty, tx, embodied, explore_all, use_dfs):
    # BFS/DFS 探索迷宫
    node_len_dir_from = {}
    q = []
    q.append((sy, sx))
    node_len_dir_from[(sy, sx)] = (0, None, None)

    while len(q) > 0:
        if use_dfs:
            curr_point = q.pop()
        else:
            curr_point = q.pop(0)

        cl = node_len_dir_from[curr_point][0]

        if curr_point == (ty, tx):
            if not explore_all:
                break

        for d in DIRECTIONS:
            move_attr = area_get_attr(area, d, curr_point)

            if embodied and move_attr == None:
                # 检查本轮是否已观测过该格子
                if area_get_attr(area, "probed_this_round", curr_point):
                    move_attr = area_get_attr(area, d, curr_point)
                else:
                    # 走到 curr_point，观测四向
                    path_to_here = maze_get_path(
                        node_len_dir_from,
                        get_pos_y(),
                        get_pos_x(),
                        curr_point[0],
                        curr_point[1],
                    )

                    for pd in path_to_here:
                        move(pd)

                    # 观测当前格四向
                    for dd in DIRECTIONS:
                        m = can_move(dd)
                        if m != None:
                            maze_update_wall_pairly(area, curr_point, dd, m)

                    area_set_attr(area, "probed_this_round", curr_point, True)
                    move_attr = area_get_attr(area, d, curr_point)

            if move_attr == True:
                next_point = maze_get_next_position(curr_point, d)

                if not area_contains_point(area, next_point):
                    continue

                if next_point in node_len_dir_from:
                    if node_len_dir_from[next_point][0] > cl + 1:
                        node_len_dir_from[next_point] = (cl + 1, d, curr_point)
                    continue

                node_len_dir_from[next_point] = (cl + 1, d, curr_point)
                q.append(next_point)

    return node_len_dir_from
