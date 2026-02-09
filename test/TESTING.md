# 测试指南

本项目现在支持使用pytest进行自动化测试。以下是测试配置和使用说明。

## 测试环境配置

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 测试文件结构
```
项目根目录/
├── tests/                    # 测试目录
│   ├── test_rect_allocator.py  # 矩形分配器测试
│   ├── test_utils.py           # 工具函数测试
│   └── test_areas.py           # 区域模块测试
├── pytest.ini                 # pytest配置文件
├── requirements.txt          # 测试依赖
└── run_tests.py              # 测试运行脚本
```

## 运行测试

### 方法1：使用测试运行脚本（推荐）
```bash
# 运行所有测试
python run_tests.py

# 运行特定测试文件
python run_tests.py test_utils.py

# 运行特定测试函数
python run_tests.py -k test_point

# 查看帮助
python run_tests.py --help
```

### 方法2：直接使用pytest命令
```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_utils.py

# 运行特定测试函数
pytest -k "test_point"

# 详细输出
pytest -v

# 生成覆盖率报告
pytest --cov=. --cov-report=html
```

## 测试配置说明

### pytest.ini配置
```ini
[tool:pytest]
testpaths = tests                    # 测试目录
python_files = test_*.py            # 测试文件命名规则
python_classes = Test*              # 测试类命名规则
python_functions = test_*           # 测试函数命名规则
addopts = -v --tb=short --cov=. --cov-report=html --cov-report=term-missing
filterwarnings = ignore::DeprecationWarning
```

### 覆盖率报告
测试运行后会生成覆盖率报告：
- 终端显示：缺失的代码行
- HTML报告：详细的可视化覆盖率分析（在htmlcov目录）

## 编写新测试

### 测试文件命名规则
- 文件名：`test_*.py`
- 测试类：`Test*`
- 测试函数：`test_*`

### 示例测试结构
```python
import pytest
from your_module import your_function

class TestYourFunction:
    """测试your_function功能"""
    
    def test_your_function_basic(self):
        """测试基本功能"""
        result = your_function(input_value)
        assert result == expected_value
    
    def test_your_function_edge_case(self):
        """测试边界情况"""
        result = your_function(edge_case_input)
        assert result is not None
```

### 常用断言方法
```python
assert result == expected          # 相等断言
assert result is not None          # 非空断言
assert len(result) > 0            # 长度断言
assert isinstance(result, type)   # 类型断言
assert value in collection        # 包含断言
```

## 测试最佳实践

1. **每个测试一个功能点**：一个测试函数只测试一个具体功能
2. **使用描述性名称**：测试函数名应清晰描述测试内容
3. **包含边界测试**：测试正常情况、边界情况和异常情况
4. **保持测试独立**：测试之间不应有依赖关系
5. **快速执行**：测试应该快速运行，避免耗时操作

## 现有测试覆盖范围

### 矩形分配器测试 (`test_rect_allocator.py`)
- 矩形减法功能
- 分配器初始化
- 逐步分配测试
- 内存释放测试

### 工具函数测试 (`test_utils.py`)
- 点对象功能
- 矩形对象功能
- 列表工具函数
- 数学工具函数

### 区域模块测试 (`test_areas.py`)
- 南瓜区域功能
- 向日葵区域功能
- 仙人掌区域功能
- 伴生区域功能
- 迷宫区域功能

## 故障排除

### 常见问题
1. **ImportError**: 确保所有被测试的模块都能正确导入
2. **AssertionError**: 检查测试逻辑和预期结果
3. **ModuleNotFoundError**: 检查Python路径和模块导入

### 调试技巧
```bash
# 详细调试输出
pytest -v -s

# 只运行失败的测试
pytest --lf

# 显示详细的错误信息
pytest --tb=long
```

## 持续集成建议

建议在CI/CD流程中加入测试：
```yaml
# GitHub Actions示例
- name: 运行测试
  run: pytest

- name: 检查覆盖率
  run: pytest --cov=. --cov-fail-under=80
```

通过这套测试框架，您可以确保代码质量，并在开发过程中快速发现和修复问题。