# pumpkin_area.py
# 南瓜种植区域

from utils_area import (
	__area_init,
	area_init_attr,
	area_get_attr,
	area_set_attr,
	area_count_blocks,
	area_move_to_nearest_corner,
	area_move_to_point,
	area_process_begin,
	area_process_end,
)
from utils_farming import farming_create_init_hook, farming_plant_if_needed, farming_create_do_harvest
from utils_move import route_move_along_with_hook


def pumpkin_area(size, allocator=None):
	# 创建南瓜区域
	# size: (h, w)
	
	# 使用公共初始化逻辑
	a, rect_id, rect = __area_init('pumpkin', size, allocator)
	if a == None:
		return None

	# 设置南瓜特有属性
	a["entity_type"] = Entities.Pumpkin

	# 设置处理器
	a["area_init"] = __pumpkin_area_init
	a["area_processor"] = __pumpkin_area_process

	# 初始化属性
	area_init_attr(a, "harvestable", False)

	return a


def __pumpkin_area_init(area):
	# 初始化实现
	entity_type = area["entity_type"]

	# 移动到最近顶点
	area_move_to_nearest_corner(area)

	# 使用通用 init hook（最后所有格子都种上南瓜）
	hook = farming_create_init_hook(entity_type)
	route = area["corner_paths"][(get_pos_y(), get_pos_x())]
	route_move_along_with_hook(route, hook, None, True)


def __pumpkin_area_process(area):
	start_tick = area_process_begin(area)
	harvest_dict = area['last_process_harvest']
	do_harvest = farming_create_do_harvest(harvest_dict)

	# 处理实现
	entity_type = area["entity_type"]
	y, x, h, w = area["rect"]

	# 创建局部 pending_check 集合
	pending_check = set()

	# 第一次扫描：移动到左下角
	area_move_to_nearest_corner(area)

	# 遍历整个区域，初始化 pending_check
	def __first_scan_hook(point, arg):
		current_entity = get_entity_type()

		if current_entity == Entities.Dead_Pumpkin:
			# 死南瓜：清理并重新种植，加入 pending_check
			do_harvest(Entities.Dead_Pumpkin)
			farming_plant_if_needed(entity_type)
			pending_check.add(point)
		elif current_entity == entity_type:
			# 是南瓜
			if can_harvest():
				# 成熟南瓜：标记
				area_set_attr(area, "harvestable", point, True)
			else:
				# 未成熟南瓜：加入 pending_check
				pending_check.add(point)
		else:
			# 其他情况：清理并种植，加入 pending_check
			if current_entity != None:
				if can_harvest():
					do_harvest(current_entity)
			farming_plant_if_needed(entity_type)
			pending_check.add(point)

	route = area["corner_paths"][(get_pos_y(), get_pos_x())]
	route_move_along_with_hook(route, __first_scan_hook, None, True)

	# 持续扫描 pending_check 直到全部成熟
	while len(pending_check) > 0:
		# 移动到第一个待检查格子
		first_point = None
		for p in pending_check:
			first_point = p
			break

		if first_point == None:
			break

		# 移动到第一个点
		area_move_to_point(first_point)

		# 遍历 pending_check 中的格子
		checked_points = []

		for point in pending_check:
			# 移动到目标格子
			area_move_to_point(point)

			# 检查当前实体
			current_entity = get_entity_type()

			if current_entity == Entities.Dead_Pumpkin:
				# 死南瓜：清理并重新种植，保留在 pending_check
				do_harvest(Entities.Dead_Pumpkin)
				farming_plant_if_needed(entity_type)
			elif current_entity == entity_type:
				# 是南瓜：检查是否成熟
				if can_harvest():
					area_set_attr(area, "harvestable", point, True)
					checked_points.append(point)
			else:
				# 其他情况：清理并种植，保留在 pending_check
				if current_entity != None:
					if can_harvest():
						do_harvest(current_entity)
				farming_plant_if_needed(entity_type)

		# 从 pending_check 中移除已成熟的格子
		for point in checked_points:
			pending_check.remove(point)

		# 如果没有任何格子成熟，pass 等待一瞬间，等下一轮
		if len(checked_points) == 0:
			pass

	# 如果 pending_check 为空，说明全部成熟，收获并重新种植
	if len(pending_check) == 0:
		do_harvest(entity_type)

		# 立即重新种植下一波
		area_move_to_nearest_corner(area)

		def __replant_hook(point, arg):
			farming_plant_if_needed(entity_type)

		route = area["corner_paths"][(get_pos_y(), get_pos_x())]
		route_move_along_with_hook(route, __replant_hook, None, True)

	area_process_end(area, start_tick)
