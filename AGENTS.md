---
description: 
alwaysApply: true
---

---
description: 
alwaysApply: true
---

## 语言特性总结

### 基本数据结构
- **字典 (dict)**
  - 创建：
    - `{}` 空字典
    - `{k1: v1, k2: v2}` 非空字典
    - `dict(dictionary=None)` 创建副本，只允许传入dict
  - 操作：
    - `len(d)`（1 tick）
    - `d[key]` 获取/设置（1 tick + key大小相关tick，建议使用简单键）
    - `for key in d` 迭代键（循环开始1 tick，迭代无额外tick）
    - `key in d` 检查存在（1 tick + key大小相关tick）
  - 修改：`d[key] = value` 插入/更新，`d.pop(key)` 删除
  - 不支持：`d.values()`，`d.items()`，`d.keys()`

- **集合 (set)**
  - 创建：
    - `set()` 空集合
    - `{a, b, c}` 非空集合
    - `set(collection=None)` 如果为None则是空集合，传入tuple/list/set则基于元素生成集合
  - 操作：
    - `len(s)`（1 tick）
    - `for item in s`（循环开始1 tick，迭代无额外tick）
    - `item in s`（逐个比较，平均O(n)个tick）
  - 修改：`s.add(item)`，`s.remove(item)`

- **列表 (list)**
  - 创建：
    - `[]` 空列表
    - `[a, b, c]` 非空列表
    - `list(collection=None)` 如果为None则是空列表，传入tuple/list/set则基于元素生成列表（同为list时则为副本）
  - 操作：
    - `len(lst)`（1 tick）
    - `lst[i]` 索引访问（1 tick）
    - `item in lst`（逐个比较，平均O(n)个tick）
  - 修改：`lst.append(item)`，`lst.pop()`，`lst.pop(i)`
  - 不支持切片操作

- **元组 (tuple)**
  - 创建：`()` 空元组，`(a,)` 单元素，`(a, b, c)` 多元素
  - 操作：
    - `len(t)`（1 tick）
    - `t[i]` 索引访问（1 tick）
    - `item in t`（逐个比较，平均O(n)个tick）
  - 不可变，支持解包：`a, b = b, a`（每个赋值操作单独计算tick） 

### 数据类型和运算
- **数字类型**
  - 所有数字默认是浮点数
  - 支持运算符（每个1 tick）：`+`, `-`, `*`, `/`, `//`, `%`, `**`
  - 单值负号：`-x`（0 tick）
  - 限制：不支持除以0，不支持inf/nan
  - 不支持连续比较：`a < b < c` 不允许（需拆分为`a < b and b < c`，两个比较各1 tick）

- **布尔运算**
  - 支持：
    - `not x`（0 tick）
    - `x and y`，`x or y`（各1 tick）
  - 比较运算符（各1 tick）：`==`, `!=`, `<`, `<=`, `>`, `>=`
  - 不支持 `is` 和 `is not`，用 `== None`（1 tick）或 `!= None`（1 tick）

### 控制结构
- **条件语句**
  - `if`（分支本身1 tick，不包括条件计算）
  - `elif`（分支本身1 tick，不包括条件计算）
  - `else`（无额外tick）
  - 条件表达式本身的计算消耗tick
  - 不支持三元表达式：`x if cond else y`

- **循环语句**
  - `for`（循环开始1 tick，迭代无额外tick，条件/序列表达式单独计算）
  - `while`（循环开始1 tick，迭代无额外tick，条件表达式单独计算）
  - 控制语句：
    - `continue`（0 tick）
    - `break`（0 tick）
    - `pass`（1 tick，可用于精确延迟）
  - `range` 支持 `range(end)` 和 `range(start, end, step=1)` 两种形式

### 函数定义和调用
- **函数定义**
  - `def func(arg1, arg2, default=value):`（定义本身1 tick）
  - 支持默认参数
  - 必须用 `#` 注释在函数前一行，不支持多行字符串文档

- **函数调用**
  - 直接调用：`func(a, b, c)`（0 tick）
  - 函数作为参数传递后调用：`higher_order(func)`（调用时1 tick）
  - 只支持位置参数，不支持关键字参数：`func(arg1=a, arg2=b)`

- **对象语法糖**
  - 对于函数 `f(x, ...)`，可以用 `x.f(...)` 调用（0 tick）
  - 要求：函数名必须是 `<type>_XXX` 格式
  - 只有通过 `from module import func` 导入的函数支持语法糖

### 模块系统
- **导入语句**
  - `import module`（0 tick，但不支持语法糖）
  - `from module import [func1, func2]`（0 tick，支持语法糖）
  - 不支持导入目录
  - 最佳实践：按对象拆分文件（如 `rect_utils`, `list_utils`）

- **模块访问**
  - 使用 `.` 运算符访问导入的模块：`module.func()`（0 tick）

### 字符串和输出
- **字符串限制**
  - 不支持多行字符串（三引号）
  - 不支持字符串拼接或 f-string
  - 注释必须用 `#` 单行注释

- **字符串函数**
  - `str(obj)` 将对象转换为字符串

- **输出**
  - 有 `print` 函数但成本很高（未指定tick，但应避免频繁使用）
  - 有 `quick_print` 内置函数用于简单输出
  - 避免图形化或频繁打印

### 随机数
- **随机函数**
  - `random()` 返回0-1之间的浮点数

### 游戏特性
- **实体**
  - 实体通过 `Entities.XXX` 枚举，特别的，没有实体使用 python 关键字 `None` 表示

### 其他限制
- **缺失特性**
  - 无异常处理（无 try/except/finally）
  - 无装饰器、生成器、yield
  - 无类（class）和面向对象
  - 无 lambda 表达式
  - 无列表推导式、字典推导式
  - 无 `in` 运算符的否定形式 `not in`（但可用 `not (x in s)`，其中`not` 0 tick，`in` 逐个比较tick）

- **内置函数**
  - `len(obj)`（1 tick）
  - `abs(x)` 支持（成本未明确，建议谨慎使用）
  - `max(a, b, c, ...)` 支持任意多位置参数（多个参数涉及多个tick）
  - `min(a, b, c, ...)` 支持任意多位置参数（多个参数涉及多个tick）
  - 游戏内置函数获取坐标时，顺序是 (x, y)，需要合理转换

### 性能优化示例
```python
# 不好：循环内访问索引
for i in range(len(data)):
    value = data[i]  # 1 次索引成本
    if value > threshold:
        process(data[i])  # 1 次索引成本

# 好：提前解包或直接迭代
for value in data:  # 直接获取元素，无索引成本
    if value > threshold:
        process(value)  # 使用已获取的元素

# 不好：多层索引重复访问
x = points[i][0]  # 2 次索引访问
y = points[i][1]  # 2 次索引访问
result = x + y + points[i][0]  # 2 次索引访问

# 好：提前解包元组
point = points[i]  # 1 次索引访问
x, y = point  # 1 次遍历元组
result = x + y + x  # 使用已解包的变量
```

### 编程约定
1. **性能优先**：关键路径内联操作，减少不必要的tick消耗
2. **缓存频繁访问**：列表/元组元素先解包到局部变量
3. **简化字典键**：使用简单类型作为字典/集合键
4. **避免高阶函数**：函数作为参数传递会增加调用成本
5. **合理使用pass**：`pass`有1 tick成本，可用于精确计时但不滥用
6. **注意in操作成本**：列表/集合的`in`操作是O(n)逐个比较

### 已知陷阱
1. 字典没有 `.values()` 和 `.items()` 方法，只能用 `for key in dict`
2. 所有数字运算可能产生浮点误差
3. 合并条件严格可能导致碎片化
4. 缺乏异常处理需要手动检查错误条件
5. 复杂条件表达式会累加多个tick成本
6. 列表/集合的`in`操作是线性时间，避免在大集合中使用
