# companion_area.py
# 同伴区（多种作物混种，带同伴增益）

from utils_area import (
	area,
	area_move_to_nearest_corner,
	area_move_to_point,
	area_visit_points,
	area_process_begin,
	area_process_end
)
from utils_farming import (
	farming_create_init_hook,
	farming_overwrite_here,
	farming_create_do_harvest
)
from utils_move import route_move_along_with_hook
from utils_rect import rectangle_contains_point
from utils_route import rect_get_hamiltonian_path
from utils_rect_allocator import rect_allocator_instance_get
from utils_rect_allocator import rect_allocator_alloc
from utils_list import list_random_choice

def companion_area(size, entity, allocator=None):
	# 创建同伴区
	# size: (h, w)
	if allocator == None:
		allocator = rect_allocator_instance_get()

	# companion 只支持这四种实体；否则随机选择一种并提示
	allowed = [Entities.Grass, Entities.Bush, Entities.Tree, Entities.Carrot]
	target_entity = entity
	if target_entity not in allowed:
		old = target_entity
		target_entity = list_random_choice(allowed)
		print("companion_area: invalid target_entity", old, "->", target_entity)
	
	# 解析尺寸
	h, w = size
	
	# 分配空间
	alloc = rect_allocator_alloc(allocator, h, w)
	if alloc == None:
		print("companion_area: alloc failed", h, w)
		return None
	rect_id, rect = alloc
	
	# 创建区域对象
	a = area(rect_id, rect)
	a['area_type'] = 'companion'
	a['last_process_tick'] = 0
	a['last_process_harvest'] = {}
	# 目标作物（同伴区的“主作物”）
	a['target_entity'] = target_entity
	a['allocator'] = allocator
	
	# 设置处理器
	a['area_init'] = __companion_area_init
	a['area_processor'] = __companion_area_process
	
	# 创建 entity selector 函数
	def entity_selector(point):
		# 当前实现：全区只种一种主作物
		return a['target_entity']
	
	a['entity_selector'] = entity_selector
	
	return a


def __companion_area_init(area):
	# 初始化：确保全区域都是 target_entity（主作物）
	target_entity = area['target_entity']
	
	# 移动到最近顶点
	area_move_to_nearest_corner(area)
	
	# 使用基于 target_entity 的 init hook
	hook = farming_create_init_hook(target_entity)
	route = area['corner_paths'][(get_pos_y(), get_pos_x())]
	route_move_along_with_hook(route, hook, None, True)


def __companion_area_process(area):
	start_tick = area_process_begin(area)
	harvest_dict = area['last_process_harvest']
	do_harvest = farming_create_do_harvest(harvest_dict)

	# 处理实现：
	# 术语约定：
	# - target_entity：本区域的“主作物种类”（全区 init 后都种它，收获后也补种它）
	# - master_point：在螺旋遍历中触发 get_companion() 的那个“主点”（角色概念，不等于种类判断）
	# - slave_point：某个 master_point 希望种植增益作物的目标点
	# - master_to_slave：master_point -> (slave_point, plant_type)
	# - slave_to_master：slave_point -> master_point（当前已实际种下的 slave 的反向映射）
	# - slave_pending：slave_point -> (master_point, plant_type)（延后处理：避免在螺旋 hook 中做阻塞/冲突解决）
	#
	# 流程概览：
	# - 螺旋阶段：只记录映射 + 能立即种的就直接种；冲突/占用统一进 pending
	# - pending 阶段：按“南瓜式收敛”逐轮处理，尽量不阻塞整轮遍历
	# - 收尾：清理所有 slave，补种 target_entity
	target_entity = area['target_entity']
	rect = area['rect']
	
	# master -> (slave_point, slave_entity_type)
	master_to_slave = {}
	# slave_point -> master_point
	slave_to_master = {}
	# 当前仍为核心作物 target_entity 的“关键点”集合（仅追踪我们关心的点，保证字典一致性）
	# point -> True
	target_points = {}
	# slave_point -> (master_point, slave_entity_type)
	# 仅当 slave_point 当前是 entity(master) 时才加入，避免在 hook 中等待成熟
	# 每个格子只允许一个 pending（先到先得，不做优先级）
	slave_pending = {}
	
	# 1) 填充 slave：中心向外螺旋，按顺序即时处理
	spiral_route = rect_get_hamiltonian_path(rect, (0, 0), 'spiral_outward_cw')
	def spiral_hook(master_point, arg):
		# 只对“主作物格子”调用 get_companion
		if get_entity_type() != target_entity:
			return
		
		# 记录：该点当前仍是 target_entity
		target_points[master_point] = True
		
		companion = get_companion()
		if companion == None:
			return
		plant_type, pos = companion
		if plant_type == None or pos == None:
			return
		
		# get_companion 返回 (x, y)，内部统一用 (y, x)
		x, y = pos
		slave_point = (y, x)
		
		# 如果不在区域内，跳过
		if not rectangle_contains_point(rect, slave_point):
			return
		
		# 若该点已经有 pending，则不再为它排队（避免排队/优先级问题）
		if slave_point in slave_pending:
			return

		# 保护 master：如果 slave_point 本身是某个 master_point（已登记在 master_to_slave 的 key 中）
		# 则不在这里种植/覆盖（否则会导致“收 master 时站在 slave 上”）
		# 仍然记录当前 master 的映射，但放弃本次 slave 落地（收益损失可接受）
		if slave_point in master_to_slave:
			master_to_slave[master_point] = (slave_point, plant_type)
			return
		
		# 如果 slave 点已被占用：不在 hook 里处理冲突，统一延后到 pending 阶段
		if slave_point in slave_to_master:
			slave_pending[slave_point] = (master_point, plant_type)
			master_to_slave[master_point] = (slave_point, plant_type)
			area_move_to_point(master_point)
			return
		
		# 种植/排队 slave
		area_move_to_point(slave_point)
		# 直接清理/覆盖为 slave（不等待成熟）
		was_target = get_entity_type() == target_entity
		farming_overwrite_here(plant_type, None, False, do_harvest)
		
		# 若覆盖掉的是 target_entity，则它不再是“核心点”
		if was_target and slave_point in target_points:
			target_points.pop(slave_point)
		# 若覆盖掉的是某个已登记的 master_point，则必须同步从 master 字典移除
		if slave_point in master_to_slave:
			master_to_slave.pop(slave_point)
		
		# 记录映射
		master_to_slave[master_point] = (slave_point, plant_type)
		slave_to_master[slave_point] = master_point
		
		# 回到 master 点继续螺旋（保证遍历器的内部坐标不被 detour 破坏）
		area_move_to_point(master_point)
	
	route_move_along_with_hook(spiral_route, spiral_hook, None, True)

	# 2) pending 去冲突（保护 10x master）
	# 若某个 pending 目标点本身也是“已拿到 slave 的 master”，则直接丢弃该 pending（接受损失，减少高价值冲突）
	if slave_pending:
		for sp in list(slave_pending):
			# 如果 sp 是一个 master 且它自己已经有 slave（10x），则保护它，不把它当 slave 点用
			if sp in master_to_slave:
				mp, pt = slave_pending[sp]
				# 撤销 mp 的期望映射（否则会在后续 harvest 阶段反复等待这个 pending）
				if mp in master_to_slave:
					mp_slave = master_to_slave[mp]
					if mp_slave[0] == sp:
						master_to_slave.pop(mp)
				slave_pending.pop(sp)
	
	# 3) 先解决 pending，再收获 master（南瓜式收敛）
	# 新语义：harvest() 可强制移除未成熟作物，因此不需要“等待成熟/多轮收敛”
	# 先把所有 pending 的 slave 都实际种下
	if slave_pending:
		def visit_pending_slave(slave_point):
			master_point, plant_type = slave_pending[slave_point]

			# pending 目标如果是 master_point，直接跳过（保护核心作物）
			if slave_point in master_to_slave:
				return
			
			# 如果该点当前被别人的 slave 占用：尽量先移除/结算对方 master，再覆盖
			if slave_point in slave_to_master:
				master_b = slave_to_master[slave_point]
				# 不在这里等待收获 masterB（master 是核心作物，统一在 master 阶段等待成熟收获）
				# 直接撤销 masterB 的 slave 映射（接受这次增益损失），并释放占用给新的 slave
				if master_b in master_to_slave:
					master_to_slave.pop(master_b)
				slave_to_master.pop(slave_point)
			
			# 覆盖为 slave
			area_move_to_point(slave_point)
			# pending 阶段：如果目标格子是核心作物 target_entity，则等待成熟再 harvest（保护产量）
			farming_overwrite_here(plant_type, target_entity, True, do_harvest)
			
			# pending 覆盖也可能覆盖到已登记 master_point，保持字典一致性
			if slave_point in master_to_slave:
				master_to_slave.pop(slave_point)
			slave_to_master[slave_point] = master_point
		
		area_visit_points(area, slave_pending, visit_pending_slave)
	
	# 然后收获所有 master（等待成熟），并补种 target_entity
	if master_to_slave:
		def visit_master_point(master_point):
			area_move_to_point(master_point)
			current = get_entity_type()
			if current != target_entity:
				# master 点被覆盖成了 slave：按约定应当已从 master_to_slave 移除，这里做兜底恢复
				farming_overwrite_here(target_entity, None, False, do_harvest)
				if master_point in master_to_slave:
					master_to_slave.pop(master_point)
				return
			while not can_harvest():
				pass
			do_harvest(target_entity)
			plant(target_entity)
			target_points[master_point] = True
		
		area_visit_points(area, master_to_slave, visit_master_point)
	
	# 4) 清理所有 slave（不等待成熟），并补种 target_entity
	if slave_to_master:
		def visit_slave(p):
			farming_overwrite_here(target_entity, None, False, do_harvest)

		area_visit_points(area, slave_to_master, visit_slave)

	area_process_end(area, start_tick)
