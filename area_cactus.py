# cactus_area.py
# 仙人掌种植区域

from utils_area import (
	area,
	area_init_attr,
	area_get_attr,
	area_set_attr,
	area_count_attr,
	area_set_all_attr,
	area_count_blocks,
	area_move_to_corner
)
from utils_farming import (
	farming_create_init_hook,
	farming_create_plant_hook
)
from utils_point import point_subtract
from utils_route import vector_get_path
from utils_move import path_move_along_with_hook, path_move_along
from utils_math import sign
from utils_direction import vector1d_y_to_direction, vector1d_x_to_direction
from utils_rect_allocator import rect_allocator_instance_get
from utils_rect_allocator import rect_allocator_alloc

def cactus_area(size, allocator=None):
	# 创建仙人掌区域
	# size: (h, w)
	if allocator == None:
		allocator = rect_allocator_instance_get()
	
	# 解析尺寸
	h, w = size
	
	# 分配空间
	rect_id, rect = rect_allocator_alloc(allocator, h, w)
	
	# 创建区域对象
	a = area(rect_id, rect)
	a['entity_type'] = Entities.Cactus
	a['allocator'] = allocator
	
	# 设置处理器
	a['area_init'] = __cactus_area_init
	a['area_processor'] = __cactus_area_process
	
	# 初始化属性
	area_init_attr(a, 'harvestable', False)
	area_init_attr(a, 'measure', None)
	
	# measure 分组（用于排序收获）
	a['measure_groups'] = {}
	a['measure_groups'][None] = set()
	
	y, x, h, w = rect
	for dy in range(h):
		for dx in range(w):
			block = (y + dy, x + dx)
			a['measure_groups'][None].add(block)
	
	return a

def __cactus_update_measure(area, block, value):
	# 更新 measure 并维护分组
	old_value = area_get_attr(area, 'measure', block)
	
	if old_value == value:
		return
	
	measure_groups = area['measure_groups']
	measure_groups[old_value].remove(block)
	
	if value not in measure_groups:
		measure_groups[value] = set()
	measure_groups[value].add(block)
	
	area_set_attr(area, 'measure', block, value)

def __cactus_swap_and_move(S_dict, sy, sx, dy, dx):
	# 交换并移动到目标位置
	step_y = sign(dy)
	direction_y = vector1d_y_to_direction(step_y)
	steps_y = abs(dy)
	
	step_x = sign(dx)
	direction_x = vector1d_x_to_direction(step_x)
	steps_x = abs(dx)
	
	for _ in range(steps_y):
		ny = sy + step_y
		nx = sx
		S_dict[(sy, sx)], S_dict[(ny, nx)] = S_dict[(ny, nx)], S_dict[(sy, sx)]
		swap(direction_y)
		move(direction_y)
		
		sy = ny
		sx = nx
	
	for _ in range(steps_x):
		ny = sy
		nx = sx + step_x
		S_dict[(sy, sx)], S_dict[(ny, nx)] = S_dict[(ny, nx)], S_dict[(sy, sx)]
		swap(direction_x)
		move(direction_x)
		
		sy = ny
		sx = nx

def __cactus_area_init(area):
	# 初始化实现
	entity_type = area['entity_type']
	
	# 移动到左下角
	area_move_to_corner(area, 'bottom_left')
	
	# 使用通用 init hook
	hook = farming_create_init_hook(entity_type)
	path = area['corner_paths'][(get_pos_y(), get_pos_x())]
	path_move_along_with_hook(path, hook, None, True)

def __cactus_area_harvest(area):
	# 按 measure 排序，使用 swap 重新排列后统一收获
	measure_groups = area['measure_groups']
	S_dict = {}
	
	y, x, h, w = area['rect']
	i = 0
	j = 0
	
	# 按 measure 从大到小分配目标位置
	for k in range(10):
		if k not in measure_groups:
			continue
		
		blocks = measure_groups[k]
		for block in blocks:
			target_y = y + i
			target_x = x + j
			S_dict[block] = (target_y, target_x)
			
			j += 1
			if j == w:
				j = 0
				i += 1
	
	# 使用 swap 重新排列
	stop_flag = False
	while not stop_flag:
		have_swapped = False
		for source in S_dict:
			sy, sx = source
			ty, tx = S_dict[source]
			dy = ty - sy
			dx = tx - sx
			
			if dy != 0 or dx != 0:
				# 移动到源位置
				current_pos = (get_pos_y(), get_pos_x())
				vec = point_subtract((sy, sx), current_pos)
				path = vector_get_path(vec)
				path_move_along(path)
				
				__cactus_swap_and_move(S_dict, sy, sx, dy, dx)
				have_swapped = True
		
		if not have_swapped:
			stop_flag = True
	
	# 统一收获
	harvest()

def __cactus_area_process(area):
	# 处理实现
	entity_type = area['entity_type']
	total_blocks = area_count_blocks(area)
	harvestable_count = area_count_attr(area, 'harvestable', True)
	unknown_measure_count = area_count_attr(area, 'measure', None)
	
	# 全部成熟且都已测量：开始收获
	if harvestable_count == total_blocks and unknown_measure_count == 0:
		__cactus_area_harvest(area)
		
		# 收获后重置状态
		area_set_all_attr(area, 'harvestable', False)
		
		y, x, h, w = area['rect']
		for dy in range(h):
			for dx in range(w):
				block = (y + dy, x + dx)
				__cactus_update_measure(area, block, None)
		
		# 移动到最近的角落，重新种植
		area_move_to_corner(area, 'bottom_left')
		
		hook = farming_create_plant_hook(entity_type)
		path = area['corner_paths'][(get_pos_y(), get_pos_x())]
		path_move_along_with_hook(path, hook, None, True)
		return
	
	# 生长期：遍历、测量、标记
	area_move_to_corner(area, 'bottom_left')
	
	def __grow_hook(point, arg):
		# 跳过已完成的方块
		if area_get_attr(area, 'harvestable', point):
			if area_get_attr(area, 'measure', point) != None:
				return
		
		# 测量
		__cactus_update_measure(area, point, measure())
		
		# 检查并标记可收获
		if can_harvest():
			area_set_attr(area, 'harvestable', point, True)
	
	path = area['corner_paths'][(get_pos_y(), get_pos_x())]
	path_move_along_with_hook(path, __grow_hook, None, True)
