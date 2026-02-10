import pytest
import sys
import os

# 添加父目录到路径以便导入项目代码
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils_pytest import (
    op_add,
    op_sub,
    op_mul,
    op_div,
    op_floordiv,
    op_mod,
    op_pow,
    op_and,
    op_or,
    op_neg,
    op_not,
)
from framework.tick_system import get_tick, reset_tick


class TestArithmeticOperations:
    """测试四则运算的 tick 消耗"""

    @pytest.mark.parametrize(
        "operation,a,b,expected",
        [
            (op_add, 3, 2, 5),
            (op_sub, 5, 3, 2),
            (op_mul, 4, 3, 12),
            (op_div, 10, 2, 5.0),
            (op_floordiv, 10, 3, 3),
            (op_mod, 10, 3, 1),
            (op_pow, 2, 3, 8),
        ],
    )
    def test_binary_arithmetic_consumes_one_tick(self, operation, a, b, expected):
        """测试二元算术运算消耗 1 tick"""
        reset_tick()
        cur = get_tick()

        # 执行运算
        result = operation(a, b)

        # 验证结果正确
        assert result == expected

        # 验证消耗了 1 tick
        assert get_tick() == cur + 1


class TestLogicalOperations:
    """测试逻辑运算的 tick 消耗"""

    @pytest.mark.parametrize(
        "operation,a,b,expected",
        [
            (op_and, True, True, True),
            (op_and, True, False, False),
            (op_and, False, True, False),
            (op_or, True, False, True),
            (op_or, False, False, False),
            (op_or, False, True, True),
        ],
    )
    def test_binary_logical_consumes_one_tick(self, operation, a, b, expected):
        """测试二元逻辑运算消耗 1 tick"""
        reset_tick()
        cur = get_tick()

        # 执行运算
        result = operation(a, b)

        # 验证结果正确
        assert result == expected

        # 验证消耗了 1 tick
        assert get_tick() == cur + 1


class TestUnaryOperations:
    """测试一元运算不消耗 tick"""

    @pytest.mark.parametrize(
        "operation,value,expected",
        [
            (op_neg, 5, -5),
            (op_neg, -3, 3),
            (op_not, True, False),
            (op_not, False, True),
        ],
    )
    def test_unary_operations_consume_no_tick(self, operation, value, expected):
        """测试一元运算（负号、not）不消耗 tick"""
        reset_tick()
        cur = get_tick()

        # 执行运算
        result = operation(value)

        # 验证结果正确
        assert result == expected

        # 验证没有消耗 tick
        assert get_tick() == cur


class TestMultipleOperations:
    """测试多个运算的累积 tick 消耗"""

    def test_multiple_operations_accumulate_ticks(self):
        """测试多个运算会累积 tick"""
        reset_tick()
        cur = get_tick()

        # 执行多个运算
        result1 = op_add(1, 2)  # +1 tick
        result2 = op_mul(result1, 3)  # +1 tick
        result3 = op_sub(result2, 1)  # +1 tick

        # 验证结果正确: (1+2)*3-1 = 8
        assert result3 == 8

        # 验证消耗了 3 ticks
        assert get_tick() == cur + 3

    def test_mixed_operations_with_unary(self):
        """测试混合运算（包含一元运算）的 tick 消耗"""
        reset_tick()
        cur = get_tick()

        # 执行混合运算
        a = op_add(5, 3)  # +1 tick
        b = op_neg(a)  # +0 tick (一元运算)
        c = op_mul(b, 2)  # +1 tick
        d = op_not(False)  # +0 tick (一元运算)
        e = op_and(d, True)  # +1 tick

        # 验证结果
        assert a == 8
        assert b == -8
        assert c == -16
        assert d == True
        assert e == True

        # 验证只消耗了 3 ticks（一元运算不计数）
        assert get_tick() == cur + 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
