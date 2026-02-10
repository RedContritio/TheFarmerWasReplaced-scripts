# utils_drone.py
# 按区域生成无人机的工具

from utils_area import area_move_to_point


def __point_in_rect(rect, point):
    # rect: (y, x, h, w), point: (y, x)
    ry, rx, rh, rw = rect
    py, px = point
    return ry <= py and py < ry + rh and rx <= px and px < rx + rw


def __pick_point_outside_rect(rect):
    # 在世界范围内挑一个“矩形外”的点（不做严格错误检查）
    world_size = get_world_size()
    y, x, h, w = rect

    candidates = [
        (y - 1, x),
        (y + h, x),
        (y, x - 1),
        (y, x + w),
        (y - 1, x - 1),
        (y - 1, x + w),
        (y + h, x - 1),
        (y + h, x + w),
    ]

    for p in candidates:
        py, px = p
        if py < 0 or px < 0:
            continue
        if py >= world_size or px >= world_size:
            continue
        if not __point_in_rect(rect, p):
            return p

    # 兜底：世界原点（可能在矩形内，但按“先不做错误检查”处理）
    return (0, 0)


def area_ensure_inited(area):
    # 主线程兜底执行时：确保 init 仅执行一次
    if "_inited" in area:
        if area["_inited"]:
            return
    area["area_init"](area)
    area["_inited"] = True


def area_step(area, do_flip=True):
    # 主线程兜底执行时：执行一次 area_processor
    # do_flip=True 时，末尾会 do_a_flip()（与无人机循环一致）
    area_ensure_inited(area)
    area["area_processor"](area)
    if do_flip:
        do_a_flip()


def spawn_area_drone(area, spawn_point=None, do_init=True):
    # 为一个普通区域生成无人机
    # 约定：spawn_drone 会在当前坐标生成无人机
    rect = area["rect"]
    y, x, h, w = rect

    if spawn_point == None:
        spawn_point = (y, x)  # 默认左下角（在矩形内）

    # 先把“生成位置”走到位，再 spawn
    area_move_to_point(spawn_point)

    def __area_loop(a=area, init_flag=do_init):
        if init_flag:
            a["area_init"](a)
        while True:
            a["area_processor"](a)
            do_a_flip()

    return spawn_drone(__area_loop)


def spawn_maze_drone(maze_area):
    # maze 特殊：生成时保持在 maze 矩形外
    rect = maze_area["rect"]
    outside = __pick_point_outside_rect(rect)

    # maze 任务是“有限的”：完成后无人机应当结束，便于 has_finished() 检测
    area_move_to_point(outside)

    def __maze_job(a=maze_area):
        a["area_init"](a)
        # 给 init 一个时间片（更稳）
        do_a_flip()
        # maze_area_process 内部会一直跑到 a['times'] 归零（或早退）
        a["area_processor"](a)
        do_a_flip()

    return spawn_drone(__maze_job)


def run_maze_inline(maze_area):
    # spawn_drone 失败时：主线程直接执行一次完整 maze 任务
    maze_area["area_init"](maze_area)
    do_a_flip()
    maze_area["area_processor"](maze_area)
    do_a_flip()
