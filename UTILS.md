# UTILS 工具文件说明

本文档说明所有工具文件的功能和使用方法。

**文件组织规范**：
- `utils_*` - 工具类文件（按功能分类）
- `area_*` - 区域类文件（各种作物/功能区域）
- 这样命名使得文件在目录中自动按类型聚合

## 核心工具

### utils_singleton.py - 通用单例
按 key 保存多个全局实例（内部用字典实现），供各模块按需注册/获取单例。rect_allocator 的全局实例即基于此实现。

**主要功能**：
- `singleton_initialize(key, value)` - 设置指定 key 的单例值并返回
- `singleton_get(key)` - 获取指定 key 的单例值（未初始化时返回 None）
- `singleton_destroy(key)` - 销毁指定 key 的单例，便于重新初始化

### utils_rect_allocator.py - 矩形分配器与全局实例 ⭐
动态矩形空间分配管理器；同时基于 `utils_singleton` 提供全局默认实例。

**分配器功能**：
- `rect_allocator(total_h, total_w)` - 创建分配器
- `rect_allocator_alloc(allocator, h, w)` - 分配矩形
- `rect_allocator_free(allocator, rect_id)` - 释放矩形
- `rect_allocator_stats(allocator)` - 获取统计信息

**全局实例**（内部使用 utils_singleton）：
- `rect_allocator_instance_initialize(world_size)` - 初始化全局分配器实例（程序开始时调用一次）
- `rect_allocator_instance_get()` - 获取全局分配器实例
- `rect_allocator_instance_destroy()` - 销毁全局实例，便于重新初始化

**使用示例**：
```python
# 在程序开始时初始化
rect_allocator_instance_initialize(get_world_size())

# 创建区域时自动使用全局分配器实例
pumpkin = pumpkin_area((6, 6))  # 默认使用全局实例
sunflower = sunflower_area((6, 6))

# 也可以显式传入自定义分配器
custom_allocator = rect_allocator(100, 100)
special_area = pumpkin_area((10, 10), allocator=custom_allocator)
```

### utils_area.py - 区域管理核心
通用区域管理工具，提供区域对象的创建、属性管理、遍历等功能。

**主要功能**：
- `area(rect_id, rect)` - 创建区域对象，预计算四个角的遍历路径
- `area_init_attr(area, attr_name, default_value)` - 初始化属性（带 value_counts 缓存）
- `area_get_attr(area, attr_name, block)` - 获取方块属性
- `area_set_attr(area, attr_name, block, value)` - 设置方块属性（自动更新 value_counts）
- `area_count_attr(area, attr_name, value)` - O(1) 统计特定值的方块数量
- `area_set_all_attr(area, attr_name, value)` - 批量设置属性
- `area_move_to_corner(area, corner)` - 移动到区域的指定角（'bottom_left', 'bottom_right', 'top_left', 'top_right'）
- `area_get_traverse_path(area, start_point)` - 获取遍历路径（优先使用预计算路径）
- `area_traverse_with_hook(area, hook, hook_arg)` - 遍历区域并执行 hook
- `area_contains_point(area, point)` - 检查点是否在区域内
- `area_count_blocks(area)` - 获取方块总数

**性能优化**：
- 预计算四个角到右上角的哈密顿路径（存储在 `area['corner_paths']`）
- 每个属性使用 `value_counts` 缓存，实现 O(1) 计数

### utils_farming.py - 农场操作工具
提供可组合的农场操作和 hook 生成器。

**原子操作**：
- `farming_till_ground()` - 翻地
- `farming_clear_entity(target_entity)` - 清除不匹配的实体
- `farming_plant_if_needed(entity_type)` - 种植（如果需要）
- `farming_harvest_now_if_ready()` - 立即收获（如果可以）
- `farming_check_and_mark_harvestable(area, block)` - 检查并标记可收获

**Hook 生成器**：
- `farming_create_init_hook(entity_type)` - 初始化 hook（耕地 + 清除 + 种植）
- `farming_create_init_hook_with_selector(entity_selector)` - 初始化 hook（使用 selector 函数）
- `farming_create_grow_hook(area, entity_type)` - 生长期 hook（只标记可收获）
- `farming_create_plant_hook(entity_type)` - 种植 hook（只种植）
- `farming_create_plant_hook_with_selector(entity_selector)` - 种植 hook（使用 selector）
- `farming_create_intercrop_process_hook(entity_selector)` - 杂种区处理 hook（harvest + plant）

## 几何和空间工具

### utils_rect.py - 矩形基础操作
矩形的基本属性和计算函数（性能敏感）。

**主要功能**：
- `rectangle(y, x, h, w)` - 创建矩形
- `rectangle_bottom_left(rect)` - 获取左下角坐标（原点）
- `rectangle_top_right(rect)` - 获取右上角坐标
- `rectangle_get_vertices(rect)` - 获取四个顶点
- `rectangle_contains_point(rect, point)` - 判断点是否在矩形内
- `rectangle_area(rect)` - 计算面积

**坐标系**：y 向上，x 向右，`(y, x)` 是左下角原点

### utils_rect_ex.py - 矩形扩展操作
矩形的复杂操作和逻辑（带完整边界检查）。

**主要功能**：
- `rectangles_intersect(rect1, rect2)` - 判断是否相交
- `rectangles_adjacent(rect1, rect2)` - 判断是否相邻
- `rectangle_merge(rect1, rect2)` - 合并相邻矩形
- `rectangle_subtract(rect, used_rect)` - 减去已用区域
- `rectangle_find_placement(rect, h, w, strategy)` - 寻找放置位置
- `rectangle_merge_all(rects)` - 合并所有相邻矩形

### utils_point.py - 点和向量操作
点、向量的创建和计算。

**主要功能**：
- `point(y, x)` / `vector(y, x)` - 创建点/向量
- `vector_len(vec)` - 曼哈顿距离（|dy| + |dx|）
- `point_add(current, delta)` - 点加法
- `point_subtract(current, base)` - 点减法
- `vector_negate(current)` - 向量取反
- `vector_warp(vec, world_size)` - 环面最短位移

## 移动和路径工具

### utils_move.py - 移动工具
路径执行和带 hook 的移动。

**主要功能**：
- `path_move_along(path)` - 沿路径移动
- `path_move_along_with_hook(path, hook, hook_arg, hook_for_start)` - 沿路径移动并执行 hook
  - hook 签名：`hook(point, hook_arg)`
  - 内部维护坐标，避免重复调用 `get_pos_y/x`

### utils_route.py - 路径规划
向量路径和哈密顿路径生成。

**主要功能**：
- `vector_get_path(vec)` - 获取简单路径（先 y 后 x）
- `vector_get_hamiltonian_path(vec, mode)` - 获取哈密顿路径（蛇形遍历）
  - `mode='snake_x'` - 横向蛇形
  - `mode='snake_y'` - 纵向蛇形

### utils_direction.py - 方向工具
方向和向量的转换（使用缓存优化）。

**主要功能**：
- `direction_to_vector2d(direction)` - 方向 → 2D 向量
- `direction_to_vector1d(direction)` - 方向 → 1D 值
- `vector1d_y_to_direction(vec)` - y 方向值 → 方向（支持 -1, 0, 1）
- `vector1d_x_to_direction(vec)` - x 方向值 → 方向（支持 -1, 0, 1）
- `direction_negate(direction)` - 方向取反

## 迷宫专用工具

### utils_maze.py - 迷宫工具
迷宫探索和路径规划的专用函数。

**主要功能**：
- `maze_get_next_position(point, direction)` - 获取下一个位置
- `maze_manhattan_distance(p1, p2)` - 曼哈顿距离
- `maze_update_wall_pairly(area, point, direction, move_attr)` - 成对更新墙属性
- `maze_get_path(node_len_dir_from, sy, sx, ty, tx)` - 还原路径
- `maze_search(area, sy, sx, ty, tx, embodied, explore_all, use_dfs)` - BFS/DFS 探索

## 基础工具

### utils_math.py - 数学工具
数学辅助函数。

**主要功能**：
- `sign(x)` - 返回数字的符号（-1, 0, 1）

### utils_dict.py - 字典工具
字典操作辅助函数。

**主要功能**：
- `dict_get(d, key, default)` - 安全获取字典值

### utils_list.py - 列表工具
列表操作和排序函数。

**主要功能**：
- `list_sort_by_yx(items, get_y, get_x)` - 按 (y, x) 坐标排序

## 作物区域 ✅

### area_pumpkin.py - 南瓜种植区
- 工厂函数：`pumpkin_area(size, allocator=None)`，size 为 `(h, w)`
- 自动从全局分配器分配空间
- 全部成熟时在当前位置统一收获
- 收获后重新种植

### area_sunflower.py - 向日葵种植区
- 工厂函数：`sunflower_area(size, allocator=None)`，size 为 `(h, w)`
- 自动从全局分配器分配空间
- 按 measure 值从大到小排序收获
- 收获后重新种植

### area_cactus.py - 仙人掌种植区
- 工厂函数：`cactus_area(size, allocator=None)`，size 为 `(h, w)`
- 自动从全局分配器分配空间
- 使用 swap 排序后统一收获
- 收获后重新种植

### area_intercrop.py - 杂种区
- 工厂函数：`intercrop_area(size, entities=None, allocator=None)`，size 为 `(h, w)`
- 自动从全局分配器分配空间
- 使用 entity_selector 函数动态确定作物类型
- 每轮立即 harvest + plant

### area_companion.py - 同伴区
- 工厂函数：`companion_area(size, entities, allocator=None)`，size 为 `(h, w)`
- 自动从全局分配器分配空间
- 与 intercrop_area 逻辑相同，用于带同伴增益的混种

### area_maze.py - 迷宫区域
- 工厂函数：`maze_area(size, times, allocator=None)`，size 为 `(h, w)`
- 自动从全局分配器分配空间（迷宫必须是正方形，会取 min(h, w)）
- 全图探索建模（DFS + embodied）
- 启发式优化路径

## 使用模式

### 标准区域创建流程
```python
# 1. 初始化全局分配器实例
rect_allocator_instance_initialize(get_world_size())

# 2. 创建区域（自动分配空间）
pumpkin = pumpkin_area((6, 6))  # 6x6 南瓜区
sunflower = sunflower_area((8, 8))   # 8x8 向日葵区
intercrop = intercrop_area((4, 8), [Entities.Grass, Entities.Tree])

# 3. 初始化区域
pumpkin['area_init'](pumpkin)

# 4. 处理区域
pumpkin['area_processor'](pumpkin)
```

### 自定义分配器
```python
# 创建独立分配器
custom_allocator = rect_allocator(100, 100)

# 使用自定义分配器
special_area = pumpkin_area((10, 10), allocator=custom_allocator)
```

## 已删除的废弃文件 🗑️

以下文件已被重构替代并删除：

- ~~`area_data.py`~~ - 被 `utils_area.py` 替代
- ~~`area_block_attr.py`~~ - 属性管理集成到 `utils_area.py`
- ~~`plant_utils.py`~~ - 被 `utils_farming.py` 替代
- ~~`plant_manager.py`~~ - 旧架构文件，已不再使用

## 性能优化要点

1. **全局分配器实例**：避免传递分配器参数，简化代码
2. **预计算路径**：四个角的遍历路径在创建 area 时预计算
3. **value_counts 缓存**：属性统计 O(1) 时间复杂度
4. **Hook 坐标追踪**：`path_move_along_with_hook` 内部维护坐标，减少 API 调用
5. **方向缓存**：`utils_direction` 使用字典缓存避免重复计算
6. **空间局部性**：使用蛇形遍历减少移动成本

## 命名规范

- **工具文件**：`utils_<type>.py` 格式（如 `utils_rect.py`, `utils_point.py`）
- **区域文件**：`area_<type>.py` 格式（如 `area_pumpkin.py`, `area_maze.py`）
- **函数名**：`<type>_<action>` 格式，支持语法糖 `obj.action()`
- **内部函数**：使用 `__` 前缀（如 `__hook`, `__grow_hook`）
- **工厂函数**：`<type>_area(size, ..., allocator=None)`，size 必须是 `(h, w)` 元组
