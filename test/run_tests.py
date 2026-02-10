#!/usr/bin/env python3
"""
测试运行脚本
用于运行项目的pytest测试套件
"""

import subprocess
import sys
import os
from pathlib import Path
import pytest

# 将父目录添加到 Python 路径，以便测试能够导入主目录的模块
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Define game built-in constants for testing environment
# These constants are available globally in the game but need to be defined for Python tests
# Install number wrapper for automatic Number class wrapping
# Transform area_, utils_, and test_ modules
# This also handles tick injection for pass statements and logical operators
from framework.number_ast_transformer import install_number_wrapper
install_number_wrapper(target_modules=['area_', 'utils_', 'cases.test_'])

# Setup game built-in environment
from framework.game_builtins import setup_game_builtins, get_world_size
setup_game_builtins()

# Initialize rect allocator for testing
from utils_rect_allocator import rect_allocator_instance_initialize
rect_allocator_instance_initialize(get_world_size())

def run_tests():
    """运行pytest测试套件"""
    
    # 检查是否安装了pytest
    try:
        import pytest
    except ImportError:
        print("错误：未安装pytest，请先安装依赖：")
        print("pip install -r requirements.txt")
        return 1
    
    # 运行pytest测试
    print("运行pytest测试套件...")
    print("=" * 60)
    
    # 设置pytest参数
    pytest_args = [
        "-v",           # 详细输出
        "--tb=short",   # 简短的错误回溯
        "--cov=.",     # 覆盖率分析
        "--cov-report=term-missing",  # 显示缺失的覆盖率
        "."             # 当前目录（测试目录）
    ]
    
    # 运行pytest
    result = pytest.main(pytest_args)
    
    print("=" * 60)
    
    if result == 0:
        print("✅ 所有测试通过！")
    else:
        print("❌ 有测试失败，请检查错误信息")
    
    return result

def run_specific_test(test_file=None, test_function=None):
    """运行特定的测试文件或函数"""
    
    pytest_args = ["-v"]
    
    if test_file:
        pytest_args.append(test_file)
    
    if test_function:
        pytest_args.append(f"-k {test_function}")
    
    return pytest.main(pytest_args)

if __name__ == "__main__":
    # 解析命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("""
测试运行脚本用法：

python run_tests.py                    # 运行所有测试
python run_tests.py <test_file>        # 运行特定测试文件
python run_tests.py -k <test_name>    # 运行特定测试函数

示例：
python run_tests.py                    # 运行所有测试
python run_tests.py test_utils.py      # 运行工具测试
python run_tests.py -k test_point      # 运行点相关的测试

注意：需要在 test/ 目录下运行此脚本
""")
            sys.exit(0)
        elif sys.argv[1] == "-k" and len(sys.argv) > 2:
            result = run_specific_test(test_function=sys.argv[2])
        else:
            result = run_specific_test(test_file=sys.argv[1])
    else:
        result = run_tests()
    
    sys.exit(result)