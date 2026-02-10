import pytest
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from framework.tick_system import get_tick, reset_tick, _add_ticks


class TestTickSystem:
    """测试 tick system 的基本功能"""

    def test_reset_tick(self):
        """测试重置 tick 功能"""
        reset_tick()
        assert get_tick() == 0

    def test_add_ticks_from_test_should_not_count(self):
        """测试从测试代码调用 _add_ticks 不应该增加 tick"""
        reset_tick()
        cur = get_tick()

        # 从测试代码调用 _add_ticks，不应该增加 tick
        _add_ticks(5)

        assert get_tick() == cur  # tick 应该保持不变

    def test_get_tick_basic(self):
        """测试基本的 get_tick 功能"""
        reset_tick()
        tick1 = get_tick()
        tick2 = get_tick()

        # 多次调用 get_tick 应该返回相同的值
        assert tick1 == tick2 == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
