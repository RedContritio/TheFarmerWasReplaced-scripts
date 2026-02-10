# test_debug.py
# 调试版本

from utils_rect_allocator import rect_allocator
from utils_rect_allocator import rect_allocator_stats
from utils_rect_allocator import rect_allocator_alloc
from utils_rect_allocator import rect_allocator_free
from utils_rect_ex import rectangle_subtract


def test_rectangle_subtract():
    quick_print("=== 测试 rectangle_subtract ===")

    # 测试1: 简单情况
    rect = (0, 0, 10, 10)
    used = (2, 2, 3, 3)
    result = rectangle_subtract(rect, used)
    quick_print("测试1 - 大矩形中挖小矩形:")
    quick_print("  原矩形:", rect)
    quick_print("  使用区域:", used)
    quick_print("  剩余矩形:", result)

    # 测试2: 完全包含
    rect = (0, 0, 10, 10)
    used = (0, 0, 10, 10)
    result = rectangle_subtract(rect, used)
    quick_print("\n测试2 - 完全使用:")
    quick_print("  原矩形:", rect)
    quick_print("  使用区域:", used)
    quick_print("  剩余矩形:", result)

    # 测试3: 不相交
    rect = (0, 0, 10, 10)
    used = (15, 15, 5, 5)
    result = rectangle_subtract(rect, used)
    quick_print("\n测试3 - 不相交:")
    quick_print("  原矩形:", rect)
    quick_print("  使用区域:", used)
    quick_print("  剩余矩形:", result)

    return True


def test_allocator_step_by_step():
    quick_print("\n=== 逐步测试分配器 ===")

    allocator = rect_allocator(22, 22)

    quick_print("初始空闲矩形:", allocator["free_rects"])

    # 分配第一个矩形
    rect1 = allocator.rect_allocator_alloc(5, 5)
    if rect1 != None:
        rect_id1, rect1_coords = rect1
        quick_print("\n分配矩形1 (5x5):")
        quick_print("  ID:", rect_id1, "位置:", rect1_coords)
        quick_print("  空闲矩形:", allocator["free_rects"])

    # 分配第二个矩形
    rect2 = allocator.rect_allocator_alloc(3, 8)
    if rect2 != None:
        rect_id2, rect2_coords = rect2
        quick_print("\n分配矩形2 (3x8):")
        quick_print("  ID:", rect_id2, "位置:", rect2_coords)
        quick_print("  空闲矩形:", allocator["free_rects"])

    # 分配第三个矩形
    rect3 = allocator.rect_allocator_alloc(7, 4)
    if rect3 != None:
        rect_id3, rect3_coords = rect3
        quick_print("\n分配矩形3 (7x4):")
        quick_print("  ID:", rect_id3, "位置:", rect3_coords)
        quick_print("  空闲矩形:", allocator["free_rects"])

    # 分配第四个矩形
    rect4 = allocator.rect_allocator_alloc(6, 6)
    if rect4 != None:
        rect_id4, rect4_coords = rect4
        quick_print("\n分配矩形4 (6x6):")
        quick_print("  ID:", rect_id4, "位置:", rect4_coords)
        quick_print("  空闲矩形:", allocator["free_rects"])

    return True


# 运行测试
test_rectangle_subtract()
test_allocator_step_by_step()
