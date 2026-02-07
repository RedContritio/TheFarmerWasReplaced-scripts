# companion_area.py
# 同伴区（多种作物混种，带同伴增益）

from utils_area import (
	area,
	area_init_attr,
	area_move_to_corner
)
from utils_farming import (
	farming_create_init_hook_with_selector,
	farming_create_intercrop_process_hook
)
from utils_move import path_move_along_with_hook
from utils_rect_allocator import rect_allocator_instance_get
from utils_rect_allocator import rect_allocator_alloc

def companion_area(size, entities, allocator=None):
	# 创建同伴区
	# size: (h, w)
	if allocator == None:
		allocator = rect_allocator_instance_get()
	
	# 解析尺寸
	h, w = size
	
	# 分配空间
	rect_id, rect = rect_allocator_alloc(allocator, h, w)
	
	# 创建区域对象
	a = area(rect_id, rect)
	a['entities'] = entities
	a['allocator'] = allocator
	
	# 设置处理器
	a['area_init'] = __companion_area_init
	a['area_processor'] = __companion_area_process
	
	# 创建 entity selector 函数
	def entity_selector(point):
		y, x = point
		i = (y + x) % len(entities)
		return entities[i]
	
	a['entity_selector'] = entity_selector
	
	return a


def __companion_area_init(area):
	# 初始化实现（与 intercrop_area 相同）
	entity_selector = area['entity_selector']
	
	# 移动到左下角
	area_move_to_corner(area, 'bottom_left')
	
	# 使用基于 selector 的 init hook
	hook = farming_create_init_hook_with_selector(entity_selector)
	path = area['corner_paths'][(get_pos_y(), get_pos_x())]
	path_move_along_with_hook(path, hook, None, True)


def __companion_area_process(area):
	# 处理实现（与 intercrop_area 相同）
	entity_selector = area['entity_selector']
	
	# 移动到左下角
	area_move_to_corner(area, 'bottom_left')
	
	# 使用基于 selector 的 intercrop process hook
	hook = farming_create_intercrop_process_hook(entity_selector)
	path = area['corner_paths'][(get_pos_y(), get_pos_x())]
	path_move_along_with_hook(path, hook, None, True)
