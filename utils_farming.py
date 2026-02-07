# farming_utils.py
# 农场操作工具（可组合）

from utils_area import area_get_attr, area_set_attr

# ========== 原子操作 ==========


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
		plant(entity_type)
		return True
	return False


def farming_harvest_now_if_ready():
	# 立即收获（如果可以）
	if can_harvest():
		harvest()
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


def farming_create_intercrop_process_hook(entity_selector):
	# 生成杂种区处理 hook（harvest + plant）
	# entity_selector: function(point) -> entity_type
	def __hook(point, arg):
		entity = entity_selector(point)

		# 立即收获
		if can_harvest():
			harvest()

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
