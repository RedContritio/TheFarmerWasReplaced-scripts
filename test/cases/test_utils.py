import pytest
from utils_point import point, point_add, point_subtract
from utils_rect import rectangle, rectangle_area, rectangle_contains_point
from utils_math import clamp


class TestPoint:
    """测试点相关功能"""
    
    def test_point_creation(self):
        """测试点创建"""
        p = point(10, 20)
        assert p[0] == 10
        assert p[1] == 20
        
    def test_point_equality(self):
        """测试点相等性"""
        p1 = point(10, 20)
        p2 = point(10, 20)
        p3 = point(15, 25)
        
        assert p1 == p2
        assert p1 != p3
        
    def test_point_operations(self):
        """测试点运算"""
        p1 = point(10, 20)
        p2 = point(5, 10)
        
        # 加法
        result = point_add(p1, p2)
        assert result[0] == 15
        assert result[1] == 30
        
        # 减法
        result = point_subtract(p1, p2)
        assert result[0] == 5
        assert result[1] == 10


class TestRectangle:
    """测试矩形相关功能"""
    
    def test_rectangle_creation(self):
        """测试矩形创建"""
        rect = rectangle(10, 20, 30, 40)
        assert rect[0] == 10
        assert rect[1] == 20
        assert rect[2] == 30
        assert rect[3] == 40
        
    def test_rectangle_area(self):
        """测试矩形面积计算"""
        rect = rectangle(0, 0, 10, 20)
        assert rectangle_area(rect) == 200
        
    def test_rectangle_contains(self):
        """测试点是否在矩形内"""
        rect = rectangle(10, 10, 20, 20)
        
        # 内部点
        assert rectangle_contains_point(rect, point(15, 15)) is True
        
        # 边界点
        assert rectangle_contains_point(rect, point(10, 10)) is True
        assert rectangle_contains_point(rect, point(29, 29)) is True
        
        # 外部点
        assert rectangle_contains_point(rect, point(5, 5)) is False
        assert rectangle_contains_point(rect, point(35, 35)) is False


class TestMathUtils:
    """测试数学工具函数"""
    
    def test_clamp(self):
        """测试数值限制函数"""
        assert clamp(5, 0, 10) == 5
        assert clamp(-5, 0, 10) == 0
        assert clamp(15, 0, 10) == 10
        assert clamp(5, 10, 0) == 10  # 标准行为：value > max_value 时返回 max_value


if __name__ == "__main__":
    pytest.main([__file__, "-v"])