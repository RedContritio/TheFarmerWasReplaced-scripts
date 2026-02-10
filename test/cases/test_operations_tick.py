import pytest
import sys
import os

# 添加父目录到路径以便导入项目代码
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils_pytest import op_pass
from framework.tick_system import get_tick, reset_tick


class TestPassOperation:
    """测试 pass 操作的 tick 消耗"""

    def test_pass_consumes_one_tick(self):
        """测试 pass 操作消耗 1 tick"""
        # 重置 tick 计数器
        reset_tick()

        # 记录当前 tick
        cur = get_tick()

        # 调用 op_pass()，它内部有一个 pass 语句
        op_pass()

        # 验证消耗了 1 tick
        assert get_tick() == cur + 1

        # 执行一个 pass 操作（在测试代码中，不应该增加 tick）
        pass

        # 验证 tick 没有变化（因为测试代码不计入 tick）
        assert get_tick() == cur + 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
