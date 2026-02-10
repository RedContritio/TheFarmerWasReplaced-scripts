# utils_rect_allocator.py
# 矩形分配器实现

from utils_rect_ex import rectangle_subtract, rectangle_merge_all
from utils_list import list_sort_by_yx
from utils_singleton import singleton_initialize, singleton_get, singleton_destroy

# 全局 rect_allocator 在单例字典中的 key
__SINGLETON_KEY_RECT_ALLOCATOR = "rect_allocator"


def rect_allocator(total_h, total_w):
    # 创建矩形分配器
    allocator = {}

    # 基本属性
    allocator["total_h"] = total_h
    allocator["total_w"] = total_w
    allocator["total_area"] = total_h * total_w

    # 分配状态
    allocator["free_rects"] = []
    allocator["free_rects"].append((0, 0, total_h, total_w))
    allocator["allocated"] = {}
    allocator["next_id"] = 1

    # 缓存
    allocator["free_area_cache"] = total_h * total_w

    # 调试开关（只在分配失败时输出）
    allocator["debug"] = False
    allocator["debug_limit"] = 12

    return allocator


def rect_allocator_enable_debug(allocator, enabled=True, limit=12):
    # 开关调试输出（仅在 alloc 失败时打印）
    allocator["debug"] = enabled
    allocator["debug_limit"] = limit


def __allocator_debug_alloc_fail(
    allocator, req_h, req_w, strategy, did_compact, tried_compact
):
    # 分配失败时的诊断输出（避免在正常路径打印）
    if "debug" not in allocator:
        return
    if not allocator["debug"]:
        return

    stats = rect_allocator_stats(allocator)
    free_rects = allocator["free_rects"]
    allocated = allocator["allocated"]

    # 统计最大空闲矩形（按面积）
    max_free = None
    max_area = 0
    max_h = 0
    max_w = 0
    for r in free_rects:
        rh, rw = r[2], r[3]
        area = rh * rw
        if max_free == None or area > max_area:
            max_free = r
            max_area = area
            max_h = rh
            max_w = rw

    quick_print(
        "[rect_alloc_fail]",
        "req",
        req_h,
        req_w,
        "strategy",
        strategy,
        "did_compact",
        did_compact,
        "tried_compact",
        tried_compact,
        "free_rects",
        len(free_rects),
        "allocated",
        len(allocated),
        "max_free_hw",
        max_h,
        max_w,
        "max_free",
        max_free,
        "stats",
        stats,
    )

    # 打印前 N 个空闲块（帮助判断碎片化）
    limit = allocator["debug_limit"]
    i = 0
    for r in free_rects:
        if i >= limit:
            break
        quick_print("[free]", i, r)
        i += 1

    # 打印前 N 个已分配块（帮助判断是什么占用了大块空间）
    i = 0
    for rid in allocated:
        if i >= limit:
            break
        quick_print("[alloc]", i, rid, allocated[rid])
        i += 1


def __allocator_get_rect_y(rect):
    # 获取矩形的y坐标
    return rect[0]


def __allocator_get_rect_x(rect):
    # 获取矩形的x坐标
    return rect[1]


def __allocator_get_item_y(item):
    # 获取(rect_id, rect)元组的y坐标
    return item[1][0]


def __allocator_get_item_x(item):
    # 获取(rect_id, rect)元组的x坐标
    return item[1][1]


def rect_allocator_stats(allocator):
    # 获取分配器统计信息
    total_h = allocator["total_h"]
    total_w = allocator["total_w"]
    total_area = total_h * total_w

    # 重新计算已分配面积（避免缓存错误）
    allocated_area = 0
    allocated = allocator["allocated"]
    for rect_id in allocated:
        rect = allocated[rect_id]
        h, w = rect[2], rect[3]
        allocated_area += h * w

    free_area = total_area - allocated_area

    # 更新缓存（确保一致性）
    allocator["free_area_cache"] = free_area

    utilization = 0.0
    if total_area > 0:
        utilization = allocated_area * 100.0 / total_area

    largest_free = 0
    free_rects = allocator["free_rects"]
    for rect in free_rects:
        h, w = rect[2], rect[3]
        area = h * w
        if area > largest_free:
            largest_free = area

    stats = {}
    stats["total_area"] = total_area
    stats["allocated_area"] = allocated_area
    stats["free_area"] = free_area
    stats["utilization"] = utilization
    stats["num_allocated"] = len(allocated)
    stats["num_free_rects"] = len(free_rects)
    stats["largest_free_block"] = largest_free

    return stats


def rect_allocator_alloc(allocator, h, w, strategy="best_area_fit", _did_compact=False):
    # 分配指定大小的矩形
    free_rects = allocator["free_rects"]
    free_count = len(free_rects)

    # 1. 快速扫描找到最佳匹配
    best_rect = None
    best_score = 0
    best_index = -1

    i = 0
    while i < free_count:
        rect = free_rects[i]
        rect_h, rect_w = rect[2], rect[3]

        # 快速检查是否能容纳
        if rect_h >= h and rect_w >= w:
            # 计算分数
            if strategy == "best_area_fit":
                score = rect_h * rect_w - h * w
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
                best_rect = rect
                best_index = i
                break

            if best_rect == None:
                best_rect = rect
                best_score = score
                best_index = i
            else:
                if score < best_score:
                    best_rect = rect
                    best_score = score
                    best_index = i

        i += 1

    if best_rect == None:
        # 尝试整理空间
        compacted = rect_allocator_compact(allocator)
        if compacted:
            # 整理后重试
            return rect_allocator_alloc(allocator, h, w, strategy, True)

        # compact 后仍失败（或 compact 无法移动），输出诊断
        __allocator_debug_alloc_fail(allocator, h, w, strategy, _did_compact, True)
        return None

    # 2. 从空闲列表中移除选中的矩形
    free_rects.pop(best_index)

    # 3. 分配矩形
    rect_id = allocator["next_id"]
    allocator["next_id"] += 1

    best_y, best_x, best_h, best_w = best_rect
    allocated_rect = (best_y, best_x, h, w)
    allocator["allocated"][rect_id] = allocated_rect

    # 4. 切割剩余空间
    remaining = rectangle_subtract(best_rect, allocated_rect)

    # 5. 添加剩余矩形到空闲列表（不更新缓存，最后统一计算）
    for rect in remaining:
        free_rects.append(rect)

    return (rect_id, allocated_rect)


def rect_allocator_free(allocator, rect_id):
    # 释放已分配的矩形
    allocated = allocator["allocated"]

    if rect_id not in allocated:
        return False

    # 获取要释放的矩形
    rect = allocated[rect_id]

    # 从已分配列表中移除
    allocated.pop(rect_id)

    # 添加到空闲列表
    free_rects = allocator["free_rects"]
    free_rects.append(rect)

    # 立即合并相邻的空闲矩形
    new_free_rects = rectangle_merge_all(free_rects)
    allocator["free_rects"] = new_free_rects

    return True


def __allocator_check_position_occupied(y, x, h, w, occupied):
    # 检查位置是否被占用
    for dy in range(h):
        dy_pos = y + dy
        for dx in range(w):
            if (dy_pos, x + dx) in occupied:
                return True
    return False


def __allocator_find_compact_position(allocator, orig_y, orig_x, h, w, occupied):
    # 为矩形寻找最紧凑的位置
    total_h = allocator["total_h"]
    total_w = allocator["total_w"]

    # 先尝试原位置
    if not __allocator_check_position_occupied(orig_y, orig_x, h, w, occupied):
        return orig_y, orig_x

    # 扫描寻找第一个可用位置
    max_y = total_h - h + 1
    max_x = total_w - w + 1

    for y in range(max_y):
        for x in range(max_x):
            if not __allocator_check_position_occupied(y, x, h, w, occupied):
                return y, x

    # 找不到合适位置，返回原位置
    return orig_y, orig_x


def __allocator_recalculate_free_rects(allocator, occupied):
    # 根据占用集合重新计算空闲区域
    total_h = allocator["total_h"]
    total_w = allocator["total_w"]

    free_rects = []
    visited = {}

    y = 0
    while y < total_h:
        x = 0
        while x < total_w:
            key = (y, x)
            if key in visited:
                x += 1
                continue
            if key in occupied:
                x += 1
                continue

            # 找到空闲区域的起始点
            w_extend = 1
            while x + w_extend < total_w:
                test_key = (y, x + w_extend)
                if test_key in visited:
                    break
                if test_key in occupied:
                    break
                w_extend += 1

            h_extend = 1
            can_extend = True
            while y + h_extend < total_h and can_extend:
                dy = y + h_extend
                dx_idx = 0
                while dx_idx < w_extend:
                    test_key = (dy, x + dx_idx)
                    if test_key in visited:
                        can_extend = False
                        break
                    if test_key in occupied:
                        can_extend = False
                        break
                    dx_idx += 1
                if can_extend:
                    h_extend += 1

            dy_idx = 0
            while dy_idx < h_extend:
                dx_idx = 0
                while dx_idx < w_extend:
                    visited[(y + dy_idx, x + dx_idx)] = True
                    dx_idx += 1
                dy_idx += 1

            free_rects.append((y, x, h_extend, w_extend))
            x += w_extend

        y += 1

    allocator["free_rects"] = free_rects


def rect_allocator_compact(allocator):
    # 空间整理：移动已分配的矩形以减少碎片
    allocated = allocator["allocated"]
    allocated_count = len(allocated)

    if allocated_count == 0:
        return True

    # 收集所有已分配的矩形
    allocated_items = []
    for rect_id in allocated:
        rect = allocated[rect_id]
        allocated_items.append((rect_id, rect))

    # 按y,x排序
    if allocated_count > 1:
        allocated_items = list_sort_by_yx(
            allocated_items, __allocator_get_item_y, __allocator_get_item_x
        )

    occupied = {}
    moved = False

    i = 0
    while i < len(allocated_items):
        rect_id, rect = allocated_items[i]
        y, x, h, w = rect

        new_y, new_x = __allocator_find_compact_position(
            allocator, y, x, h, w, occupied
        )

        if new_y != y or new_x != x:
            allocated[rect_id] = (new_y, new_x, h, w)
            moved = True

        for dy in range(h):
            dy_pos = new_y + dy
            for dx in range(w):
                occupied[(dy_pos, new_x + dx)] = True

        i += 1

    if moved:
        __allocator_recalculate_free_rects(allocator, occupied)
        return True

    return False


def rect_allocator_clear(allocator):
    # 清空分配器
    total_h = allocator["total_h"]
    total_w = allocator["total_w"]
    total_area = total_h * total_w

    allocator["free_rects"] = []
    allocator["free_rects"].append((0, 0, total_h, total_w))
    allocator["allocated"] = {}
    allocator["next_id"] = 1
    allocator["free_area_cache"] = total_area


def rect_allocator_get_free_rects(allocator):
    # 获取空闲矩形列表（副本）
    free_rects = allocator["free_rects"]

    result = []
    for rect in free_rects:
        result.append(rect)
    return result


def rect_allocator_get_allocated(allocator):
    # 获取已分配矩形字典（副本）
    result = {}
    allocated = allocator["allocated"]
    for rect_id in allocated:
        result[rect_id] = allocated[rect_id]
    return result


def rect_allocator_can_alloc(allocator, h, w):
    # 快速检查是否能分配指定大小的矩形
    free_rects = allocator["free_rects"]
    for rect in free_rects:
        if rect[2] >= h and rect[3] >= w:
            return True

    return False


# 全局 rect_allocator 单例（使用 utils_singleton）


def rect_allocator_instance_initialize(world_size):
    # 初始化全局分配器实例（程序开始时调用一次）
    return singleton_initialize(
        __SINGLETON_KEY_RECT_ALLOCATOR, rect_allocator(world_size, world_size)
    )


def rect_allocator_instance_get():
    # 获取全局分配器实例
    return singleton_get(__SINGLETON_KEY_RECT_ALLOCATOR)


def rect_allocator_instance_destroy():
    # 销毁全局分配器实例，便于重新初始化
    singleton_destroy(__SINGLETON_KEY_RECT_ALLOCATOR)
