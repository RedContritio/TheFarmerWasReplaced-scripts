# area_utils.py
# 通用区域管理工具

from utils_rect import rectangle_contains_point
from utils_route import vector_get_hamiltonian_path, vector_get_path
from utils_move import path_move_along_with_hook, path_move_along
from utils_point import point_subtract

def area(rect_id, rect):
	# 创建通用区域对象
	a = {}
	a['rect_id'] = rect_id
	a['rect'] = rect
	a['attrs'] = {}
	
	# 处理器函数（由具体实现设置）
	a['area_init'] = None
	a['area_processor'] = None
	
	# 预计算四个角的遍历路径（优化性能）
	# 坐标系：y向上，x向右，所以 (y, x) 是左下角
	y, x, h, w = rect
	a['corner_paths'] = {}
	
	# 左下角 (y, x) - 原点
	vec = (h - 1, w - 1)
	a['corner_paths'][(y, x)] = vector_get_hamiltonian_path(vec, 'snake_y')
	
	# 右下角 (y, x + w - 1)
	vec = (h - 1, -(w - 1))
	a['corner_paths'][(y, x + w - 1)] = vector_get_hamiltonian_path(vec, 'snake_y')
	
	# 左上角 (y + h - 1, x)
	vec = (-(h - 1), w - 1)
	a['corner_paths'][(y + h - 1, x)] = vector_get_hamiltonian_path(vec, 'snake_y')
	
	# 右上角 (y + h - 1, x + w - 1)
	vec = (-(h - 1), -(w - 1))
	a['corner_paths'][(y + h - 1, x + w - 1)] = vector_get_hamiltonian_path(vec, 'snake_y')
	
	return a

def area_init_attr(area, attr_name, default_value=None):
	# 初始化属性
	y, x, h, w = area['rect']
	
	# 属性数据字典
	attr_dict = {}
	
	# value_counts 缓存（优化 count 操作）
	value_counts = {}
	block_count = h * w
	value_counts[default_value] = block_count
	
	for dy in range(h):
		for dx in range(w):
			block = (y + dy, x + dx)
			attr_dict[block] = default_value
	
	# 存储属性字典和缓存
	area['attrs'][attr_name] = {
		'data': attr_dict,
		'value_counts': value_counts
	}

def area_get_attr(area, attr_name, block):
	# 获取方块属性
	return area['attrs'][attr_name]['data'][block]

def area_set_attr(area, attr_name, block, value):
	# 设置方块属性（并更新 value_counts）
	attr_info = area['attrs'][attr_name]
	attr_dict = attr_info['data']
	value_counts = attr_info['value_counts']
	
	old_value = attr_dict[block]
	
	if old_value == value:
		return
	
	# 更新 value_counts
	value_counts[old_value] -= 1
	if value not in value_counts:
		value_counts[value] = 0
	value_counts[value] += 1
	
	# 更新属性值
	attr_dict[block] = value

def area_count_attr(area, attr_name, value):
	# 统计特定值的方块数量（O(1) 时间复杂度）
	value_counts = area['attrs'][attr_name]['value_counts']
	if value not in value_counts:
		return 0
	return value_counts[value]

def area_set_all_attr(area, attr_name, value):
	# 批量设置属性（并更新 value_counts）
	attr_info = area['attrs'][attr_name]
	attr_dict = attr_info['data']
	
	y, x, h, w = area['rect']
	block_count = h * w
	
	# 重置 value_counts（重新创建字典）
	attr_info['value_counts'] = {}
	attr_info['value_counts'][value] = block_count
	
	# 批量设置
	for dy in range(h):
		for dx in range(w):
			block = (y + dy, x + dx)
			attr_dict[block] = value

def area_get_traverse_path(area, start_point):
	# 获取从当前位置开始的遍历路径
	# 优先使用预计算的四个角路径
	if start_point in area['corner_paths']:
		return area['corner_paths'][start_point]
	
	# 如果不是四个角，动态计算到右上角的路径
	y, x, h, w = area['rect']
	sy, sx = start_point
	
	top_right_y = y + h - 1
	top_right_x = x + w - 1
	vec = (top_right_y - sy, top_right_x - sx)
	
	path = vector_get_hamiltonian_path(vec, 'snake_y')
	return path

def area_traverse_with_hook(area, hook, hook_arg=None):
	# 遍历区域并执行 hook
	# 假设当前已在区域内
	current_pos = (get_pos_y(), get_pos_x())
	path = area_get_traverse_path(area, current_pos)
	
	path_move_along_with_hook(path, hook, hook_arg, True)

def area_count_blocks(area):
	# 获取方块总数
	y, x, h, w = area['rect']
	return h * w

def area_contains_point(area, point):
	# 检查点是否在区域内（仅在需要时使用）
	return rectangle_contains_point(area['rect'], point)

def area_move_to_corner(area, corner='bottom_left'):
	# 移动到区域的指定角
	# 坐标系：y向上，x向右
	# corner: 'bottom_left', 'bottom_right', 'top_left', 'top_right'
	y, x, h, w = area['rect']
	
	if corner == 'bottom_left':
		target = (y, x)
	elif corner == 'bottom_right':
		target = (y, x + w - 1)
	elif corner == 'top_left':
		target = (y + h - 1, x)
	elif corner == 'top_right':
		target = (y + h - 1, x + w - 1)
	else:
		target = (y, x)
	
	current = (get_pos_y(), get_pos_x())
	vec = point_subtract(target, current)
	path = vector_get_path(vec)
	path_move_along(path)
	
	return target

def area_ensure_in_area(area):
	# 确保当前位置在区域内，如果不在则移动到左下角
	current = (get_pos_y(), get_pos_x())
	if not area_contains_point(area, current):
		area_move_to_corner(area, 'bottom_left')

# ========== 公共接口（分发机制）==========

def area_init(area):
	# 初始化区域（分发到具体实现）
	init_func = area['area_init']
	if init_func != None:
		init_func(area)

def area_process(area):
	# 处理区域（分发到具体实现）
	processor = area['area_processor']
	if processor != None:
		processor(area)
