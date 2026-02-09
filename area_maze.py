# maze_area.py
# 迷宫区域

from utils_area import (
	__area_init,
	area_init_attr,
	area_get_attr,
	area_set_attr,
	area_move_to_point,
	area_process_begin,
	area_process_end
)
from utils_maze import (
	DIRECTIONS,
	maze_get_next_position,
	maze_manhattan_distance,
	maze_update_wall_pairly,
	maze_get_path,
	maze_search
)
from utils_point import point_subtract
from utils_route import vector_get_path
from utils_move import path_move_along
from utils_direction import direction_negate
from utils_farming import farming_create_do_harvest

def maze_area(size, times, allocator=None):
	# 创建迷宫区域
	# size: (h, w) - 迷宫必须是正方形
	
	# 解析尺寸（迷宫必须是正方形，取较小值）
	h, w = size
	h = min(h, w)
	w = h
	
	# 使用公共初始化逻辑
	a, rect_id, rect = __area_init('maze', (h, w), allocator)
	if a == None:
		return None
	
	y, x, h, w = rect
	
	# 迷宫特有属性
	a['center'] = (y + (h + 1) // 2, x + (w + 1) // 2)
	a['cost'] = h * 2 ** (num_unlocked(Unlocks.Mazes) - 1)
	a['times'] = times
	
	# 设置处理器
	a['area_init'] = __maze_area_init
	a['area_processor'] = __maze_area_process
	
	# 初始化持久化属性（四个方向的墙/路信息）
	for d in DIRECTIONS:
		area_init_attr(a, d, None)
	
	return a

def __init_round_temp_attrs(area):
	# 初始化临时属性（每轮重置）
	area_init_attr(area, 'probed_this_round', False)
	for d in DIRECTIONS:
		attr_name = 'forbidden_heuristic_' + str(d)
		area_init_attr(area, attr_name, False)

def __try_shortcut(area, start_point, target_point):
	# 启发式直线探索
	best_dir = None
	best_dist = None
	
	# 选择离目标最近的方向
	for d in DIRECTIONS:
		next_point = maze_get_next_position(start_point, d)
		dist = maze_manhattan_distance(next_point, target_point)
		if best_dist == None or dist < best_dist:
			best_dist = dist
			best_dir = d
	
	if best_dir == None:
		return False, [], None
	
	# 沿 best_dir 走直线
	curr_dist = maze_manhattan_distance(start_point, target_point)
	walked = []
	
	while True:
		curr_pos = (get_pos_y(), get_pos_x())
		attr = area_get_attr(area, best_dir, curr_pos)
		
		if attr == None:
			# 未知边，探测
			move_result = can_move(best_dir)
			maze_update_wall_pairly(area, curr_pos, best_dir, move_result)
			
			if move_result:
				# 发现新路
				return True, None, best_dir
			
			# 遇墙，需回退
			return False, walked, best_dir
		
		if attr == True:
			# 可走，检查距离是否回升
			next_point = maze_get_next_position(curr_pos, best_dir)
			new_dist = maze_manhattan_distance(next_point, target_point)
			
			if new_dist >= curr_dist:
				# 距离回升，需回退
				return False, walked, best_dir
			
			# 继续走
			move(best_dir)
			walked.append(best_dir)
			curr_dist = new_dist
		else:
			# 墙，停止并回退
			return False, walked, best_dir

def __move_in_maze_with_heuristic(area, path, sy, sx, ty, tx):
	# 边走边启发式优化
	if path == None:
		return False
	
	curr_point = (sy, sx)
	target_point = (ty, tx)
	path_index = 0
	
	while path_index < len(path):
		pd = path[path_index]
		
		# 检查下一个点是否远离目标
		next_point = maze_get_next_position(curr_point, pd)
		if maze_manhattan_distance(next_point, target_point) > maze_manhattan_distance(curr_point, target_point):
			# 计算最优启发方向
			best_dir = None
			best_dist = None
			
			for d in DIRECTIONS:
				test_point = maze_get_next_position(curr_point, d)
				dist = maze_manhattan_distance(test_point, target_point)
				if best_dist == None or dist < best_dist:
					best_dist = dist
					best_dir = d
			
			# 检查该格子是否禁止该方向的启发
			attr_name = 'forbidden_heuristic_' + str(best_dir)
			is_forbidden = area_get_attr(area, attr_name, curr_point)
			
			if not is_forbidden:
				# 尝试启发式直线探索
				found_new, backtrack, tried_dir = __try_shortcut(area, curr_point, target_point)
				
				# 标记该格子禁止该方向
				tried_attr_name = 'forbidden_heuristic_' + str(tried_dir)
				area_set_attr(area, tried_attr_name, curr_point, True)
				
				if found_new:
					# 发现新路，重新 BFS 寻路
					tree = maze_search(area, get_pos_y(), get_pos_x(), ty, tx, False, False, False)
					new_path = maze_get_path(tree, get_pos_y(), get_pos_x(), ty, tx)
					
					if new_path != None:
						path = new_path
						path_index = 0
						curr_point = (get_pos_y(), get_pos_x())
						continue
				else:
					# 未发现新路，回退到起点
					if backtrack != None:
						for i in range(len(backtrack)):
							back_dir = backtrack[len(backtrack) - 1 - i]
							reverse_dir = direction_negate(back_dir)
							move(reverse_dir)
					
					curr_point = (get_pos_y(), get_pos_x())
		
		# 正常走这一步
		if can_move(pd) == False:
			return False
		
		move(pd)
		
		# 传播禁止方向到下一个格子
		next_point = maze_get_next_position(curr_point, pd)
		
		for d in DIRECTIONS:
			attr_name = 'forbidden_heuristic_' + str(d)
			is_forbidden = area_get_attr(area, attr_name, curr_point)
			
			# 如果禁止，且移动方向与 d 相反，则传播
			if is_forbidden and direction_negate(d) == pd:
				area_set_attr(area, attr_name, next_point, True)
		
		curr_point = (get_pos_y(), get_pos_x())
		path_index += 1
	
	return True

def __maze_area_init(area):
	# 迷宫初始化：移动到中心并创建迷宫
	center = area['center']
	cost = area['cost']
	
	# 检查是否有足够的材料
	if num_items(Items.Weird_Substance) < cost:
		return
	
	# 移动到中心
	current_pos = (get_pos_y(), get_pos_x())
	vec = point_subtract(center, current_pos)
	path = vector_get_path(vec)
	path_move_along(path)
	
	# 创建迷宫
	entity_type = get_entity_type()
	if entity_type != Entities.Hedge and entity_type != Entities.Treasure:
		plant(Entities.Bush)
		use_item(Items.Weird_Substance, cost)

def __maze_area_process(area):
	start_tick = area_process_begin(area)
	harvest_dict = area['last_process_harvest']
	do_harvest = farming_create_do_harvest(harvest_dict)

	# 处理迷宫区域
	if area['times'] <= 0:
		area_process_end(area, start_tick)
		return
	
	# 检查是否已经是迷宫
	entity_type = get_entity_type()
	if entity_type != Entities.Hedge and entity_type != Entities.Treasure:
		# 还未创建迷宫，需要先 init
		area_process_end(area, start_tick)
		return
	
	# 第一轮：全图探索建模
	__init_round_temp_attrs(area)
	tx, ty = measure()
	
	quick_print('迷宫建模中')
	start_tick = get_tick_count()
	
	# DFS + embodied 全图探索
	maze_search(area, get_pos_y(), get_pos_x(), ty, tx, True, True, True)
	
	init_tick = get_tick_count() - start_tick
	quick_print('迷宫建模花了', init_tick, 'ticks')
	
	# 循环寻宝
	while area['times'] > 0:
		__init_round_temp_attrs(area)
		tx, ty = measure()
		
		# 非具身 BFS 寻路
		quick_print('开始规划路径')
		plan_start_tick = get_tick_count()
		
		tree = maze_search(area, get_pos_y(), get_pos_x(), ty, tx, False, False, False)
		path = maze_get_path(tree, get_pos_y(), get_pos_x(), ty, tx)
		
		plan_tick = get_tick_count() - plan_start_tick
		quick_print('规划路径花了', plan_tick, 'ticks')
		
		if path == None:
			area_process_end(area, start_tick)
			return
		
		# 边走边启发式优化
		quick_print('启发式前往宝箱')
		move_start_tick = get_tick_count()
		
		ok = __move_in_maze_with_heuristic(area, path, get_pos_y(), get_pos_x(), ty, tx)
		
		move_tick = get_tick_count() - move_start_tick
		quick_print('寻路移动花了', move_tick, 'ticks')
		
		if not ok:
			area_process_end(area, start_tick)
			return
		
		if get_entity_type() != Entities.Treasure:
			area_process_end(area, start_tick)
			return
		
		# 找到宝箱
		area['times'] -= 1
		quick_print('还需要找', area['times'], '次宝箱')
		
		if area['times'] == 0:
			do_harvest(Entities.Treasure)
			area_process_end(area, start_tick)
		else:
			use_item(Items.Weird_Substance, area['cost'])
			
			# 重置墙的状态（墙可能被拆）
			y, x, h, w = area['rect']
			for dy in range(h):
				for dx in range(w):
					block = (y + dy, x + dx)
					for d in DIRECTIONS:
						if area_get_attr(area, d, block) == False:
							area_set_attr(area, d, block, None)

	# 理论上不会走到这里（times==0 会在上面 end），但保持一致
	area_process_end(area, start_tick)
