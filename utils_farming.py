# farming_utils.py
# 农场操作工具（可组合）

from utils_area import area_get_attr, area_set_attr

# ========== 原子操作 ==========


from utils_dict import dict_get

# ========== 通用“覆盖式种植”工具 ==========

def farming_harvest_and_record_current(harvest_dict):
	# 收获并记录当前格子的实体类型
	# harvest_dict: {entity: count}
	entity = get_entity_type()
	if harvest():
		harvest_dict[entity] = dict_get(harvest_dict, entity, 0) + 1
		return True
	return False


def farming_create_do_harvest(harvest_dict=None):
	# 生成一个 do_harvest 回调函数：do_harvest(entity) -> bool
	# - harvest_dict 为 None：忽略 entity，直接调用 harvest()
	# - harvest_dict 为 dict：若 harvest() 成功，则对传入的 entity 计数 +1
	if harvest_dict == None:
		def __do_harvest_no_record(entity):
			return harvest()

		return __do_harvest_no_record

	def __do_harvest_record(entity):
		if harvest():
			harvest_dict[entity] = dict_get(harvest_dict, entity, 0) + 1
			return True
		return False

	return __do_harvest_record


def farming_overwrite_here(target_entity, protect_entity=None, wait_if_protect=False, do_harvest=None):
	# 在当前位置将作物覆盖为 target_entity
	# - 若当前位置是 protect_entity：
	#   - wait_if_protect=True 时会等待成熟再 harvest（保护产量）
	#   - 否则直接 harvest() 强制移除（是否“成功收获”看 can_harvest）
	# - 若当前位置不是 protect_entity：
	#   - 直接 harvest() 强制移除（是否“成功收获”看 can_harvest）
	# do_harvest: 可选回调，用于自定义/统计 harvest 行为
	# 将 do_harvest 的分流放到开头，只判断一次（热路径不重复判断）
	if do_harvest == None:
		do_harvest = farming_create_do_harvest(None)

	current = get_entity_type()

	if protect_entity != None and current == protect_entity:
		if wait_if_protect:
			while not can_harvest():
				pass
		# 强制移除（返回值可用于判断是否真的移除了，但这里我们总是尝试继续 plant）
		do_harvest(current)
		plant(target_entity)
		return True

	# 非 protect：同样强制移除（若本来为空，harvest() 通常会返回 False）
	do_harvest(current)
	plant(target_entity)
	return True


def farming_create_overwrite_hook(target_entity, protect_entity=None, wait_if_protect=False, do_harvest=None):
	# 生成覆盖式种植 hook：hook(point, arg)
	if do_harvest == None:
		do_harvest = farming_create_do_harvest(None)

	def __hook(point, arg):
		farming_overwrite_here(target_entity, protect_entity, wait_if_protect, do_harvest)

	return __hook

def farming_till_ground():
	# 翻地
	if get_ground_type() == Grounds.Grassland:
		till()
		return True
	return False


def farming_clear_entity(target_entity):
	# 清除不匹配的实体
	current = get_entity_type()
	if current != target_entity:
		if current != None:
			if can_harvest():
				harvest()
				return True
	return False


def farming_prepare_ground(entity_type):
	# 准备土地（组合操作）
	farming_till_ground()
	farming_clear_entity(entity_type)


def farming_plant_if_needed(entity_type):
	# 种植（如果需要）
	if get_entity_type() != entity_type:
		if can_harvest():
			harvest()
		plant(entity_type)
		return True
	return False


def farming_harvest_now_if_ready():
	# 立即收获（如果可以）
	if can_harvest():
		harvest()
		return True
	return False


def farming_harvest_and_record(harvest_dict, entity):
	# 收获并记录到字典中
	# harvest_dict: 要更新的字典 {entity: count}
	# entity: 当前格子的实体类型（调用者应该已知）
	# 返回：是否成功收获
	if harvest():
		harvest_dict[entity] = dict_get(harvest_dict, entity, 0) + 1
		return True
	return False


def farming_check_and_mark_harvestable(area, block):
	# 检查并标记可收获
	if can_harvest():
		area_set_attr(area, "harvestable", block, True)
		return True
	return False


# ========== Hook 生成器（提供给各 area 组合使用）==========


def farming_create_init_hook(entity_type):
	# 生成初始化 hook（耕地 + 清除 + 种植）
	def __hook(point, arg):
		farming_till_ground()
		farming_clear_entity(entity_type)
		farming_plant_if_needed(entity_type)

	return __hook


def farming_create_init_hook_with_selector(entity_selector):
	# 生成初始化 hook（使用 selector 函数确定作物类型）
	# entity_selector: function(point) -> entity_type
	def __hook(point, arg):
		entity = entity_selector(point)
		farming_till_ground()
		farming_clear_entity(entity)
		farming_plant_if_needed(entity)

	return __hook


def farming_create_grow_hook(area, entity_type):
	# 生成生长期 hook（只标记可收获，不种植）
	def __hook(point, arg):
		if can_harvest():
			area_set_attr(area, "harvestable", point, True)

	return __hook


def farming_create_plant_hook(entity_type):
	# 生成种植 hook（只种植）
	def __hook(point, arg):
		farming_plant_if_needed(entity_type)

	return __hook


def farming_create_plant_hook_with_selector(entity_selector):
	# 生成种植 hook（使用 selector 函数确定作物类型）
	# entity_selector: function(point) -> entity_type
	def __hook(point, arg):
		entity = entity_selector(point)
		farming_plant_if_needed(entity)

	return __hook


def farming_create_intercrop_process_hook(entity_selector, do_harvest=None):
	# 生成杂种区处理 hook（harvest + plant）
	# entity_selector: function(point) -> entity_type
	if do_harvest == None:
		def __hook_no_harvest_cb(point, arg):
			entity = entity_selector(point)

			# 立即收获
			if can_harvest():
				harvest()

			# 种植
			if get_entity_type() != entity:
				plant(entity)

		return __hook_no_harvest_cb

	def __hook(point, arg):
		entity = entity_selector(point)

		# 立即收获
		if can_harvest():
			do_harvest(get_entity_type())

		# 种植
		if get_entity_type() != entity:
			plant(entity)

	return __hook


# ========== 旧的 Hook 生成器（向后兼容，已废弃）==========


def farming_make_init_hook(entity_type):
	# 生成初始化 hook（已废弃，使用 farming_create_init_hook）
	return farming_create_init_hook(entity_type)


def farming_make_simple_grow_hook(area, entity_type):
	# 生成简单生长 hook（已废弃）
	def __hook(point, arg):
		farming_plant_if_needed(entity_type)
		farming_check_and_mark_harvestable(area, point)

	return __hook


def farming_make_intercrop_hook(area):
	# 生成杂种区 hook（已废弃）
	def __hook(point, arg):
		entity = area_get_attr(area, "entity", point)

		farming_harvest_now_if_ready()

		if get_entity_type() != entity:
			plant(entity)

	return __hook
