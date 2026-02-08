# sunflower_area.py
# 向日葵种植区域

from utils_area import (
	area,
	area_init_attr,
	area_get_attr,
	area_set_attr,
	area_count_attr,
	area_set_all_attr,
	area_count_blocks,
	area_move_to_nearest_corner,
	area_move_to_point,
	area_process_begin,
	area_process_end
)
from utils_farming import (
	farming_create_init_hook,
	farming_create_plant_hook,
	farming_create_do_harvest
)
from utils_move import route_move_along_with_hook
from utils_rect_allocator import rect_allocator_instance_get
from utils_rect_allocator import rect_allocator_alloc

def sunflower_area(size, allocator=None):
	# 创建向日葵区域
	# size: (h, w)
	if allocator == None:
		allocator = rect_allocator_instance_get()
	
	# 解析尺寸
	h, w = size
	
	# 分配空间
	rect_id, rect = rect_allocator_alloc(allocator, h, w)
	
	# 创建区域对象
	a = area(rect_id, rect)
	a['area_type'] = 'sunflower'
	a['last_process_tick'] = 0
	a['last_process_harvest'] = {}
	a['entity_type'] = Entities.Sunflower
	a['allocator'] = allocator
	
	# 设置处理器
	a['area_init'] = __sunflower_area_init
	a['area_processor'] = __sunflower_area_process
	
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

def __sunflower_update_measure(area, block, value):
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

def __sunflower_area_init(area):
	# 初始化实现
	entity_type = area['entity_type']
	
	# 移动到最近顶点
	area_move_to_nearest_corner(area)
	
	# 使用通用 init hook，并在种植后立刻测量（measure 在下次种植前不变）
	base_hook = farming_create_init_hook(entity_type)
	def hook(point, arg):
		base_hook(point, arg)
		__sunflower_update_measure(area, point, measure())
	route = area['corner_paths'][(get_pos_y(), get_pos_x())]
	route_move_along_with_hook(route, hook, None, True)

def __sunflower_area_harvest(area, do_harvest):
	# 按 measure 从大到小排序收获
	measure_groups = area['measure_groups']
	
	# 找最大 measure
	max_measure = 0
	for m in measure_groups:
		if m == None:
			continue
		if len(measure_groups[m]) == 0:
			continue
		if m > max_measure:
			max_measure = m
	
	# 从大到小收获
	m = max_measure
	while m >= 0:
		if m not in measure_groups:
			m -= 1
			continue
		
		blocks = measure_groups[m]
		for block in blocks:
			# 移动到目标方块
			area_move_to_point(block)
			do_harvest(Entities.Sunflower)
		
		m -= 1

def __sunflower_area_process(area):
	start_tick = area_process_begin(area)
	harvest_dict = area['last_process_harvest']
	do_harvest = farming_create_do_harvest(harvest_dict)

	# 处理实现
	entity_type = area['entity_type']
	total_blocks = area_count_blocks(area)

	# 单次 process：等待全成熟 -> 完整收获一次 -> 重播种并立刻测量 -> 返回（回到初始状态）
	while True:
		unknown_measure_count = area_count_attr(area, 'measure', None)
		if unknown_measure_count > 0:
			# 缺少测量值：补测（plant 后 measure 立即可用）
			area_move_to_nearest_corner(area)
			def __measure_only_hook(point, arg):
				if area_get_attr(area, 'measure', point) == None:
					__sunflower_update_measure(area, point, measure())
			route = area['corner_paths'][(get_pos_y(), get_pos_x())]
			route_move_along_with_hook(route, __measure_only_hook, None, True)

		harvestable_count = area_count_attr(area, 'harvestable', True)
		if harvestable_count < total_blocks:
			# 生长期：只标记成熟（measure 已稳定，不重复测量）
			progress = {}
			progress['v'] = False
			area_move_to_nearest_corner(area)
			def __mark_hook(point, arg):
				if not area_get_attr(area, 'harvestable', point):
					if can_harvest():
						area_set_attr(area, 'harvestable', point, True)
						progress['v'] = True
			route = area['corner_paths'][(get_pos_y(), get_pos_x())]
			route_move_along_with_hook(route, __mark_hook, None, True)
			if not progress['v']:
				pass
			continue

		# 全部成熟：按 measure 收获一次
		__sunflower_area_harvest(area, do_harvest)

		# 重置 harvestable
		area_set_all_attr(area, 'harvestable', False)

		# 重置 measure + 分组
		area_set_all_attr(area, 'measure', None)
		measure_groups = {}
		measure_groups[None] = set()
		area['measure_groups'] = measure_groups
		y, x, h, w = area['rect']
		for dy in range(h):
			for dx in range(w):
				measure_groups[None].add((y + dy, x + dx))

		# 重新种植并立刻测量
		area_move_to_nearest_corner(area)
		base_hook = farming_create_plant_hook(entity_type)
		def __replant_and_measure(point, arg):
			base_hook(point, arg)
			__sunflower_update_measure(area, point, measure())
		route = area['corner_paths'][(get_pos_y(), get_pos_x())]
		route_move_along_with_hook(route, __replant_and_measure, None, True)
		break

	area_process_end(area, start_tick)
