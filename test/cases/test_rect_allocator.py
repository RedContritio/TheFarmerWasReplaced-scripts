import pytest
from utils_rect_allocator import (
    rect_allocator,
    rect_allocator_alloc,
    rect_allocator_free,
)
from utils_rect_ex import rectangle_subtract


class TestRectangleSubtract:
    """测试矩形减法功能"""

    def test_rectangle_subtract_simple(self):
        """测试简单情况：大矩形中挖小矩形"""
        rect = (0, 0, 10, 10)
        used = (2, 2, 3, 3)
        result = rectangle_subtract(rect, used)

        assert result is not None
        assert len(result) > 0
        # 验证剩余区域应该包含原矩形减去使用区域的部分

    def test_rectangle_subtract_complete_overlap(self):
        """测试完全重叠情况"""
        rect = (0, 0, 10, 10)
        used = (0, 0, 10, 10)
        result = rectangle_subtract(rect, used)

        # 完全重叠时应该返回空列表或None
        assert result == [] or result is None

    def test_rectangle_subtract_no_overlap(self):
        """测试不相交情况"""
        rect = (0, 0, 10, 10)
        used = (15, 15, 5, 5)
        result = rectangle_subtract(rect, used)

        # 不相交时应该返回原矩形
        assert result == [rect] or result == rect


class TestRectAllocator:
    """测试矩形分配器功能"""

    def test_allocator_initialization(self):
        """测试分配器初始化"""
        allocator = rect_allocator(22, 22)
        assert allocator is not None
        assert "free_rects" in allocator

    def test_allocator_step_by_step(self):
        """测试逐步分配功能"""
        allocator = rect_allocator(22, 22)

        # 分配第一个矩形
        rect1 = rect_allocator_alloc(allocator, 5, 5)
        assert rect1 is not None
        rect_id1, rect1_coords = rect1
        assert rect_id1 is not None
        assert rect1_coords is not None

        # 分配第二个矩形
        rect2 = rect_allocator_alloc(allocator, 3, 8)
        assert rect2 is not None

        # 分配第三个矩形
        rect3 = rect_allocator_alloc(allocator, 7, 4)
        assert rect3 is not None

        # 分配第四个矩形
        rect4 = rect_allocator_alloc(allocator, 6, 6)
        assert rect4 is not None

    def test_allocator_free(self):
        """测试释放分配的内存"""
        allocator = rect_allocator(22, 22)

        # 分配一个矩形
        rect = rect_allocator_alloc(allocator, 5, 5)
        assert rect is not None
        rect_id, rect_coords = rect

        # 释放该矩形
        result = rect_allocator_free(allocator, rect_id)
        # 使用 == True 而不是 is True，因为 Number 包装后的值不是同一个对象
        assert result == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
