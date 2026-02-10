from utils_direction import (
    direction_to_vector2d,
    vector_to_direction,
    vector1d_y_to_direction,
    vector1d_x_to_direction,
    direction_negate,
)
from utils_math import sign
from utils_list import list_foreach
from utils_dict import dict_foreach
from utils_rect import (
    rectangle_opposite_vertex,
    rectangle_center,
    rectangle_nearest_vertex,
)
from utils_point import point_subtract, point_add

# 螺旋方向向量：(outward/inward, clockwise/counterclockwise) -> [(dy, dx), ...]
__SPIRAL_DIRECTION_VECTORS = {
    ("outward", "clockwise"): [(0, 1), (-1, 0), (0, -1), (1, 0)],
    ("outward", "counterclockwise"): [(0, -1), (-1, 0), (0, 1), (1, 0)],
    ("inward", "clockwise"): [(0, 1), (1, 0), (0, -1), (-1, 0)],
    ("inward", "counterclockwise"): [(1, 0), (0, 1), (-1, 0), (0, -1)],
}

#
# 内旋螺旋的步数规律：
# - 每一圈 4 段，除了最后一段为了“进入内圈”少走 1 步（即 -2），其余都是边长 -1
# - 具体用 w 还是 h 取决于该段方向是横向还是纵向（不能简单随方向序列旋转公式）


def __vectors_to_directions(vecs):
    return list_foreach(vecs, vector_to_direction)


# 将方向向量转换为方向枚举
__SPIRAL_DIRECTIONS = dict_foreach(__SPIRAL_DIRECTION_VECTORS, __vectors_to_directions)


def __vector1d_y_append_path_helper(dy, path):
    direction = dy.sign().vector1d_y_to_direction()
    for _ in range(abs(dy)):
        path.append(direction)
    return path


def __vector1d_x_append_path_helper(dx, path):
    direction = dx.sign().vector1d_x_to_direction()
    for _ in range(abs(dx)):
        path.append(direction)
    return path


def __vector2d_append_path_helper(vec, path):
    __vector1d_y_append_path_helper(vec[0], path)
    __vector1d_x_append_path_helper(vec[1], path)
    return path


def vector_get_path(vec):
    path = []
    __vector2d_append_path_helper(vec, path)
    return path


def __rect_append_hamiltonian_path_snake_x(rect, path, start_point):
    path_start = rectangle_nearest_vertex(rect, start_point)
    opposite = rectangle_opposite_vertex(rect, path_start)
    vec = point_subtract(opposite, path_start)

    y, x = vec
    dy = y.sign().vector1d_y_to_direction()
    dx = x.sign().vector1d_x_to_direction()
    x_abs = abs(x)

    for _ in range(x_abs):
        path.append(dx)
    for _ in range(abs(y)):
        path.append(dy)
        dx = dx.direction_negate()
        for _ in range(x_abs):
            path.append(dx)

    return path_start


def __rect_append_hamiltonian_path_snake_y(rect, path, start_point):
    path_start = rectangle_nearest_vertex(rect, start_point)
    opposite = rectangle_opposite_vertex(rect, path_start)
    vec = point_subtract(opposite, path_start)

    y, x = vec
    dy = y.sign().vector1d_y_to_direction()
    dx = x.sign().vector1d_x_to_direction()
    y_abs = abs(y)

    for _ in range(y_abs):
        path.append(dy)
    for _ in range(abs(x)):
        path.append(dx)
        dy = dy.direction_negate()
        for _ in range(y_abs):
            path.append(dy)

    return path_start


def __rect_spiral_peel_segments(rect, start_corner, mode_key):
    # 生成“外层剥洋葱”的 inward 螺旋段列表：[(direction, count), ...]
    # 只生成段（不是逐步路径），段数约 O(h+w)，性能更好
    y, x, h, w = rect
    min_y = y
    max_y = y + h - 1
    min_x = x
    max_x = x + w - 1

    py, px = start_corner
    vecs = __SPIRAL_DIRECTION_VECTORS[("inward", mode_key)]
    dirs = __SPIRAL_DIRECTIONS[("inward", mode_key)]

    # 旋转方向序列：确保第一步不会立刻越界（退化尺寸也更稳）
    rot = 0
    for r in range(4):
        dy, dx = vecs[r]
        ny = py + dy
        nx = px + dx
        if min_y <= ny and ny <= max_y and min_x <= nx and nx <= max_x:
            rot = r
            break

    rot_vecs = []
    rot_dirs = []
    for i in range(4):
        rot_vecs.append(vecs[(i + rot) % 4])
        rot_dirs.append(dirs[(i + rot) % 4])

    segments = []
    while min_x <= max_x and min_y <= max_y:
        for i in range(4):
            dy, dx = rot_vecs[i]
            d = rot_dirs[i]

            if dy == 0 and dx == 1:
                cnt = max_x - px
            elif dy == 0 and dx == -1:
                cnt = px - min_x
            elif dy == 1 and dx == 0:
                cnt = max_y - py
            else:
                cnt = py - min_y

            if cnt > 0:
                segments.append((d, cnt))
                py = py + dy * cnt
                px = px + dx * cnt

            # 走完一条边后收缩边界
            if dy == 0:
                if py == min_y:
                    min_y = min_y + 1
                else:
                    max_y = max_y - 1
            else:
                if px == min_x:
                    min_x = min_x + 1
                else:
                    max_x = max_x - 1

            if not (min_x <= max_x and min_y <= max_y):
                break

    return segments, (py, px)


def __rect_append_hamiltonian_path_spiral_outward(rect, path, start_point, mode):
    # outward：走到中心后，严格不重复走满整个 rect（Hamiltonian path）
    # 性能敏感：用“段”反向输出，不构造整条 inward 路径
    y, x, h, w = rect
    ideal_center = rectangle_center(rect)

    # 退化为 1D：直接线性走满（从中心向一侧，再反向扫另一侧）
    if h == 1:
        # 1xN 线性图无法从中心作为 Hamiltonian 起点而不重复
        # 这里选择从左端点开始扫满
        for _ in range(w - 1):
            path.append(East)
        return (y, x)
    if w == 1:
        # Nx1 线性图无法从中心作为 Hamiltonian 起点而不重复
        # 这里选择从下端点开始扫满
        for _ in range(h - 1):
            path.append(North)
        return (y, x)

    # outward 的旋向与 inward 反转后的旋向相反：outward_cw = reverse(inward_ccw)
    if mode == "spiral_outward_cw":
        inward_mode_key = "counterclockwise"
    else:
        inward_mode_key = "clockwise"

    # 选择一个边界起点，使剥洋葱 inward 的终点刚好落在 center
    corners = [(y, x), (y, x + w - 1), (y + h - 1, x), (y + h - 1, x + w - 1)]
    chosen_segments = None
    chosen_end = corners[0]
    best_dist = 999999
    for corner in corners:
        segs, end_point = __rect_spiral_peel_segments(rect, corner, inward_mode_key)
        dy = end_point[0] - ideal_center[0]
        dx = end_point[1] - ideal_center[1]
        dist = abs(dy) + abs(dx)
        if dist < best_dist:
            best_dist = dist
            chosen_segments = segs
            chosen_end = end_point
            if dist == 0:
                break

    # 若没有段（极端退化尺寸已在上面 return），则结束
    if chosen_segments == None:
        return ideal_center

    # 反向输出 outward：段逆序 + 方向取反
    seg_len = len(chosen_segments)
    for i in range(seg_len - 1, -1, -1):
        d, cnt = chosen_segments[i]
        nd = d.direction_negate()
        for _ in range(cnt):
            path.append(nd)

    return chosen_end


def __spiral_inward_rotation_offset(vy, vx):
    # 根据起点角到对角的方向，得到首边方向在 [东,北,西,南] 中的偏移
    sy = sign(vy)
    sx = sign(vx)
    if sy > 0:
        if sx > 0:
            return 0
        else:
            return 1
    elif sy < 0:
        if sx < 0:
            return 2
        else:
            return 3
    else:
        if sx > 0:
            return 0
        else:
            return 1


def __rect_append_hamiltonian_path_spiral_inward(rect, path, start_point, mode):
    path_start = rectangle_nearest_vertex(rect, start_point)
    opposite = rectangle_opposite_vertex(rect, path_start)
    vec = point_subtract(opposite, path_start)

    y, x, h, w = rect
    vy, vx = vec

    clockwise = mode == "spiral_inward_cw"
    if clockwise:
        mode_key = "clockwise"
    else:
        mode_key = "counterclockwise"
    base_dirs = __SPIRAL_DIRECTIONS[("inward", mode_key)]
    rot = __spiral_inward_rotation_offset(vy, vx)
    dirs = []
    vecs = __SPIRAL_DIRECTION_VECTORS[("inward", mode_key)]
    rot_vecs = []
    for i in range(4):
        dirs.append(base_dirs[(i + rot) % 4])
        rot_vecs.append(vecs[(i + rot) % 4])

    # 直接用“剥洋葱”方式在边界内走满：对任意长方形都正确且不需要特殊补丁
    min_y = y
    max_y = y + h - 1
    min_x = x
    max_x = x + w - 1
    py, px = path_start

    while min_x <= max_x and min_y <= max_y:
        for i in range(4):
            dy, dx = rot_vecs[i]
            d = dirs[i]

            if dy == 0 and dx == 1:
                cnt = max_x - px
            elif dy == 0 and dx == -1:
                cnt = px - min_x
            elif dy == 1 and dx == 0:
                cnt = max_y - py
            else:
                cnt = py - min_y

            for _ in range(cnt):
                path.append(d)

            py = py + dy * cnt
            px = px + dx * cnt

            # 收缩刚走过的那条边
            if dy == 0:
                if py == min_y:
                    min_y = min_y + 1
                else:
                    max_y = max_y - 1
            else:
                if px == min_x:
                    min_x = min_x + 1
                else:
                    max_x = max_x - 1

            if not (min_x <= max_x and min_y <= max_y):
                break

    return path_start


__RECT_MODE_HANDLERS = {
    "snake_x": __rect_append_hamiltonian_path_snake_x,
    "snake_y": __rect_append_hamiltonian_path_snake_y,
    "spiral_outward_cw": __rect_append_hamiltonian_path_spiral_outward,
    "spiral_outward_ccw": __rect_append_hamiltonian_path_spiral_outward,
    "spiral_inward_cw": __rect_append_hamiltonian_path_spiral_inward,
    "spiral_inward_ccw": __rect_append_hamiltonian_path_spiral_inward,
}


def rect_get_hamiltonian_path(rect, start_point, mode="snake_x"):
    path = []
    handler = __RECT_MODE_HANDLERS[mode]
    if mode == "snake_x" or mode == "snake_y":
        route_start = handler(rect, path, start_point)
    else:
        route_start = handler(rect, path, start_point, mode)
    return (path, route_start)


def __rect_get_hamiltonian_cycle_even_w(rect):
    # 在 h x w 矩形格点图上构造哈密顿回路（w 为偶数，且 h,w >= 2）
    # 返回：cycle_points（按回路顺序的点列表，元素为 (y, x)）
    #
    # 回路存在条件：h>=2,w>=2，且至少一边为偶数（本函数处理 w 为偶数的情况）
    y0, x0, h, w = rect
    cycle = []
    cycle.append((y0, x0))

    # 第一列向上走满
    dy = 1
    while dy < h:
        cycle.append((y0 + dy, x0))
        dy += 1

    # 剩余列蛇形走满，但跳过顶行 y0（顶行最后用来闭环）
    dx = 1
    while dx < w:
        if (dx % 2) == 1:
            # 奇数列：从底部进入，向上扫到 y0+1
            cycle.append((y0 + h - 1, x0 + dx))
            dy2 = h - 2
            while dy2 > 0:
                cycle.append((y0 + dy2, x0 + dx))
                dy2 -= 1
        else:
            # 偶数列：从 y0+1 进入，向下扫到底部
            cycle.append((y0 + 1, x0 + dx))
            dy2 = 2
            while dy2 < h:
                cycle.append((y0 + dy2, x0 + dx))
                dy2 += 1
        dx += 1

    # 顶行从右往左走到 x0+1（最后一个点与起点 (y0,x0) 相邻，完成闭环）
    cycle.append((y0, x0 + w - 1))
    dx = w - 2
    while dx > 0:
        cycle.append((y0, x0 + dx))
        dx -= 1

    return cycle


def rect_get_hamiltonian_cycle(rect):
    # 生成矩形格点图的哈密顿回路（Hamiltonian cycle）
    # rect: (y0, x0, h, w)
    # 返回：cycle_points 或 None（当 h,w 都为奇数或维度退化时）
    y0, x0, h, w = rect
    if h < 2 or w < 2:
        return None

    # 哈密顿回路存在条件：至少一边为偶数
    if (w % 2) == 0:
        return __rect_get_hamiltonian_cycle_even_w(rect)

    if (h % 2) == 0:
        # 转置：在 (x0,y0,w,h) 上生成，再映射回 (y,x)
        t_cycle = __rect_get_hamiltonian_cycle_even_w((x0, y0, w, h))
        if t_cycle == None:
            return None
        cycle = []
        for p in t_cycle:
            py, px = p
            cycle.append((px, py))
        return cycle

    return None


def rect_get_hamiltonian_cycle_index(rect):
    # 返回 (cycle_points, index_map, L) 或 (None, None, 0)
    cycle = rect_get_hamiltonian_cycle(rect)
    if cycle == None:
        return None, None, 0

    index_map = {}
    i = 0
    for p in cycle:
        index_map[p] = i
        i += 1

    return cycle, index_map, i


def route_walk_to_point(target_point, blocked_set=None, except_in_blocked=None):
    # 从当前位置沿曼哈顿路径走向 target_point（先 y 后 x），遇阻即停。
    # blocked_set：不可踏入的格子集合；except_in_blocked：即使在其中也允许踏入的格子（如尾尖）。
    # 返回 (final_point, path_points)：最终坐标、以及途经点列表 [起点, ..., 终点]（含起点与终点）。
    current = (get_pos_y(), get_pos_x())
    path_points = [current]
    path = vector_get_path(point_subtract(target_point, current))
    idx = 0
    while idx < len(path):
        d = path[idx]
        step = direction_to_vector2d(d)
        np = point_add(current, step)
        if blocked_set != None:
            if np in blocked_set:
                if except_in_blocked == None or np not in except_in_blocked:
                    return (current, path_points)
        ok = move(d)
        if not ok:
            return (current, path_points)
        current = (get_pos_y(), get_pos_x())
        path_points.append(current)
        idx += 1
    return (current, path_points)


def route_bfs_path(start, target, get_neighbors):
    # BFS 寻路：从 start 到 target，get_neighbors(node) 返回从 node 可走的下一格列表。
    # 返回 [start, ..., target] 或 None（不可达）。
    if start == target:
        return [start]
    visited = {}
    parent = {}
    queue = [start]
    visited[start] = True
    while len(queue) > 0:
        curr = queue.pop(0)
        if curr == target:
            path_back = []
            p = target
            while True:
                path_back.append(p)
                if p == start:
                    break
                p = parent[p]
            path = []
            i = len(path_back) - 1
            while i >= 0:
                path.append(path_back[i])
                i -= 1
            return path
        neighbors = get_neighbors(curr)
        ni = 0
        while ni < len(neighbors):
            n = neighbors[ni]
            if n not in visited:
                visited[n] = True
                parent[n] = curr
                queue.append(n)
            ni += 1
    return None


def route_astar_path(start, target, get_neighbors, heuristic):
    # A* 寻路：f = g + heuristic(node)。优先扩展 f 最小的节点，使搜索尽量朝目标方向走。
    # heuristic(node) 应返回从 node 到 target 的估计代价（如曼哈顿距离）。
    # 返回 [start, ..., target] 或 None。
    if start == target:
        return [start]
    parent = {}
    g = {}
    g[start] = 0
    h0 = heuristic(start)
    open_list = [(h0, 0, start)]
    while len(open_list) > 0:
        best_i = 0
        i = 1
        while i < len(open_list):
            if open_list[i][0] < open_list[best_i][0]:
                best_i = i
            i += 1
        f_curr, g_curr, curr = open_list[best_i]
        open_list.pop(best_i)
        if g[curr] < g_curr:
            continue
        if curr == target:
            path_back = []
            p = target
            while True:
                path_back.append(p)
                if p == start:
                    break
                p = parent[p]
            path = []
            pi = len(path_back) - 1
            while pi >= 0:
                path.append(path_back[pi])
                pi -= 1
            return path
        neighbors = get_neighbors(curr)
        ni = 0
        while ni < len(neighbors):
            n = neighbors[ni]
            g_new = g_curr + 1
            if n not in g:
                g[n] = g_new
                parent[n] = curr
                h_n = heuristic(n)
                open_list.append((g_new + h_n, g_new, n))
            else:
                if g_new < g[n]:
                    g[n] = g_new
                    parent[n] = curr
                    h_n = heuristic(n)
                    open_list.append((g_new + h_n, g_new, n))
            ni += 1
    return None
