"""
测试 tick AST 转换器是否正确工作
验证运算符和pass语句的tick计数是否自动注入
"""

import sys
import os
import pytest

# 导入tick系统
from framework.tick_system import get_tick, reset_tick


class TestTickTransformer:
    """测试tick AST转换器"""

    def test_tick_system_available(self):
        """验证tick系统是否可用"""
        reset_tick()
        assert get_tick() == 0

    def test_pass_consumes_one_tick(self):
        """测试pass语句消耗1 tick"""
        import utils_pytest

        reset_tick()
        cur = get_tick()
        utils_pytest.op_pass()
        assert get_tick() == cur + 1

    @pytest.mark.parametrize(
        "operation,a,b,expected_ticks",
        [
            ("add", 3, 5, 1),
            ("sub", 10, 3, 1),
            ("mul", 4, 7, 1),
            ("div", 20, 4, 1),
            ("floordiv", 17, 5, 1),
            ("mod", 17, 5, 1),
            ("pow", 2, 10, 1),
        ],
    )
    def test_arithmetic_operations(self, operation, a, b, expected_ticks):
        """测试四则运算消耗1 tick"""
        import utils_pytest

        reset_tick()
        cur = get_tick()

        func = getattr(utils_pytest, f"op_{operation}")
        result = func(a, b)

        assert get_tick() == cur + expected_ticks

    @pytest.mark.parametrize(
        "operation,a,b,expected_ticks",
        [
            ("and", True, True, 1),
            ("and", True, False, 1),
            ("or", False, True, 1),
            ("or", False, False, 1),
        ],
    )
    def test_logical_operations(self, operation, a, b, expected_ticks):
        """测试逻辑运算消耗1 tick"""
        import utils_pytest

        reset_tick()
        cur = get_tick()

        func = getattr(utils_pytest, f"op_{operation}")
        result = func(a, b)

        assert get_tick() == cur + expected_ticks

    @pytest.mark.parametrize(
        "operation,a,expected_ticks",
        [
            ("neg", 5, 0),
            ("neg", -3, 0),
            ("not", True, 0),
            ("not", False, 0),
        ],
    )
    def test_unary_operations_no_tick(self, operation, a, expected_ticks):
        """测试一元运算不消耗tick"""
        import utils_pytest

        reset_tick()
        cur = get_tick()

        func = getattr(utils_pytest, f"op_{operation}")
        result = func(a)

        assert get_tick() == cur + expected_ticks

    def test_multiple_operations_accumulate(self):
        """测试多个操作的tick累积"""
        import utils_pytest

        reset_tick()
        cur = get_tick()

        # 执行多个操作
        utils_pytest.op_add(1, 2)  # +1 tick
        utils_pytest.op_mul(3, 4)  # +1 tick
        utils_pytest.op_and(True, False)  # +1 tick
        utils_pytest.op_pass()  # +1 tick

        assert get_tick() == cur + 4

    def test_nested_operations(self):
        """测试嵌套运算的tick累积"""
        import utils_pytest

        reset_tick()
        cur = get_tick()

        # 嵌套运算：(a + b) * (c - d)
        # 应该消耗3个tick：1个加法 + 1个减法 + 1个乘法
        result = utils_pytest.op_mul(
            utils_pytest.op_add(1, 2), utils_pytest.op_sub(5, 3)
        )

        assert get_tick() == cur + 3

    def test_subscript_operation(self):
        """测试索引操作消耗1 tick"""
        import utils_pytest

        reset_tick()
        cur = get_tick()

        result = utils_pytest.op_subscript([1, 2, 3], 0)

        assert get_tick() == cur + 1
        assert result == 1

    def test_pack_operation(self):
        """测试打包操作消耗1 tick"""
        import utils_pytest

        reset_tick()
        cur = get_tick()

        result = utils_pytest.op_pack(1, 2)

        assert get_tick() == cur + 1
        assert result == (1, 2)

    def test_unpack_operation(self):
        """测试解包操作消耗1 tick"""
        import utils_pytest

        reset_tick()
        cur = get_tick()

        result = utils_pytest.op_unpack((3, 4))

        assert get_tick() == cur + 1
        assert result == (3, 4)

    def test_chain_call_operation(self):
        """测试链式调用：a.abs().sign() 应该消耗2 tick"""
        import utils_pytest

        reset_tick()
        cur = get_tick()

        result = utils_pytest.op_chain_call(-5)

        # abs() 消耗1 tick，sign() 消耗1 tick，共2 tick
        assert get_tick() == cur + 2
        assert result == 1  # abs(-5) = 5, sign(5) = 1
