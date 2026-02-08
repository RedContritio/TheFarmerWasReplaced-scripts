# area_utils.py
# 通用区域管理工具

from utils_rect import rectangle_contains_point
from utils_route import rect_get_hamiltonian_path, vector_get_path
from utils_move import route_move_along_with_hook, route_move_along, path_move_along
from utils_point import point_subtract
from utils_list import list_sort_by_yx

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
	y, x, h, w = rect
	a['corner_paths'] = {}
	
	# 左下角 (y, x)
	a['corner_paths'][(y, x)] = rect_get_hamiltonian_path(rect, (y, x), 'snake_y')
	
	# 右下角 (y, x + w - 1)
	a['corner_paths'][(y, x + w - 1)] = rect_get_hamiltonian_path(rect, (y, x + w - 1), 'snake_y')
	
	# 左上角 (y + h - 1, x)
	a['corner_paths'][(y + h - 1, x)] = rect_get_hamiltonian_path(rect, (y + h - 1, x), 'snake_y')
	
	# 右上角 (y + h - 1, x + w - 1)
	a['corner_paths'][(y + h - 1, x + w - 1)] = rect_get_hamiltonian_path(rect, (y + h - 1, x + w - 1), 'snake_y')
	
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
	
	# 如果不是四个角，动态计算遍历路径
	rect = area['rect']
	route = rect_get_hamiltonian_path(rect, start_point, 'snake_y')
	return route

def area_traverse_with_hook(area, hook, hook_arg=None):
	# 遍历区域并执行 hook
	# 假设当前已在区域内
	current_pos = (get_pos_y(), get_pos_x())
	route = area_get_traverse_path(area, current_pos)
	route_move_along_with_hook(route, hook, hook_arg, True)

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


def area_move_to_nearest_corner(area):
	# 移动到区域的最近角落
	# 返回：目标角落坐标
	y, x, h, w = area['rect']
	current_y = get_pos_y()
	current_x = get_pos_x()
	
	# 四个角的坐标
	corners = [
		(y, x),
		(y, x + w - 1),
		(y + h - 1, x),
		(y + h - 1, x + w - 1)
	]
	
	# 找最近的角（曼哈顿距离）
	min_dist = None
	nearest_corner = None
	
	for corner in corners:
		cy, cx = corner
		dist = abs(current_y - cy) + abs(current_x - cx)
		if min_dist == None or dist < min_dist:
			min_dist = dist
			nearest_corner = corner
	
	# 移动到最近角落
	vec = point_subtract(nearest_corner, (current_y, current_x))
	path = vector_get_path(vec)
	path_move_along(path)
	
	return nearest_corner

def area_ensure_in_area(area):
	# 确保当前位置在区域内，如果不在则移动到左下角
	current = (get_pos_y(), get_pos_x())
	if not area_contains_point(area, current):
		area_move_to_nearest_corner(area)


def area_wait_until_all_satisfy(area, attr_name, target_value, process_hook, hook_arg=None):
	# 等待所有格子都满足某个条件
	# process_hook: hook(point, pending_check, arg)
	#   hook 负责处理 point 让其满足条件
	#   如果处理过程中导致其他格子不满足，应添加到 pending_check
	total_blocks = area_count_blocks(area)
	threshold = total_blocks // 3
	
	# 初始化 pending_check：收集所有不满足的点
	pending_check = set()
	y, x, h, w = area['rect']
	for dy in range(h):
		for dx in range(w):
			block = (y + dy, x + dx)
			if area_get_attr(area, attr_name, block) != target_value:
				pending_check.add(block)
	
	while len(pending_check) > 0:
		if len(pending_check) > threshold:
			# 策略1：蛇形遍历
			area_move_to_nearest_corner(area)
			
			def wrapper_hook(point, arg):
				# 只处理 pending_check 中的点
				if point in pending_check:
					process_hook(point, pending_check, arg)
					# hook 执行后检查是否满足
					if area_get_attr(area, attr_name, point) == target_value:
						if point in pending_check:
							pending_check.remove(point)
			
			route = area['corner_paths'][(get_pos_y(), get_pos_x())]
			route_move_along_with_hook(route, wrapper_hook, hook_arg, True)
		else:
			# 策略2：逐点访问
			pending_list = list(pending_check)
			
			def get_y(p):
				return p[0]
			
			def get_x(p):
				return p[1]
			
			list_sort_by_yx(pending_list, get_y, get_x)
			
			for point in pending_list:
				# 检查点是否还在 pending_check 中
				if point not in pending_check:
					continue
				
				py, px = point
				current_pos = (get_pos_y(), get_pos_x())
				vec = point_subtract((py, px), current_pos)
				path = vector_get_path(vec)
				path_move_along(path)
				
				# 处理这个点
				process_hook(point, pending_check, hook_arg)
				
				# 检查是否满足
				if area_get_attr(area, attr_name, point) == target_value:
					if point in pending_check:
						pending_check.remove(point)


def area_move_to_point(target_point):
	# 移动到指定点（不触发遍历 hook）
	current = (get_pos_y(), get_pos_x())
	vec = point_subtract(target_point, current)
	path = vector_get_path(vec)
	path_move_along(path)


def area_visit_points(area, points_dict, visit_func):
	# 访问 points_dict 的所有点：
	# - 点数量 > 1/4 区域面积：蛇形遍历全区域（只命中 points_dict 时 visit）
	# - 否则：按 (y,x) 排序逐点访问
	# points_dict 可为 dict 或 set，推荐 dict（in 成本更低）
	point_count = len(points_dict)
	if point_count == 0:
		return

	total = area_count_blocks(area)
	threshold = total // 4

	if point_count > threshold:
		# 从最近顶点开始，减少无谓走位（area 之间不相交时更划算）
		area_move_to_nearest_corner(area)
		route = area['corner_paths'][(get_pos_y(), get_pos_x())]

		def hook(point, arg):
			if point in points_dict:
				visit_func(point)

		route_move_along_with_hook(route, hook, None, True)
		return

	points = []
	for p in points_dict:
		points.append(p)

	def get_y(p):
		return p[0]

	def get_x(p):
		return p[1]

	points = list_sort_by_yx(points, get_y, get_x)
	for p in points:
		area_move_to_point(p)
		visit_func(p)


def area_process_begin(area):
	# 每次 area_processor 开头调用
	# 初始化/重置过程指标
	area['last_process_harvest'] = {}
	return get_tick_count()


def area_process_end(area, start_tick):
	# 每次 area_processor 结束（包括早退）调用
	end_tick = get_tick_count()
	delta = end_tick - start_tick
	area['last_process_tick'] = delta
	area_type = 'unknown'
	if 'area_type' in area:
		area_type = area['area_type']
	quick_print('[area]', area_type, 'id', area['rect_id'],
				'tick', delta, 'harvest', area['last_process_harvest'])

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
