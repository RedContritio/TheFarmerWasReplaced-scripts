# intercrop_area.py
# 杂种区（多种作物混种）

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

DEFAULT_INTERCROP_ENTITIES = [Entities.Grass, Entities.Tree, Entities.Carrot]

def intercrop_area(size, entities=None, allocator=None):
	# 创建杂种区
	# size: (h, w)
	if allocator == None:
		allocator = rect_allocator_instance_get()
	
	if entities == None:
		entities = DEFAULT_INTERCROP_ENTITIES
	
	# 解析尺寸
	h, w = size
	
	# 分配空间
	rect_id, rect = rect_allocator_alloc(allocator, h, w)
	
	# 创建区域对象
	a = area(rect_id, rect)
	a['entities'] = entities
	a['allocator'] = allocator
	
	# 设置处理器
	a['area_init'] = __intercrop_area_init
	a['area_processor'] = __intercrop_area_process
	
	# 创建 entity selector 函数
	def entity_selector(point):
		y, x = point
		i = (y + x) % len(entities)
		return entities[i]
	
	a['entity_selector'] = entity_selector
	
	return a

def __intercrop_area_init(area):
	# 初始化实现
	# 移动到左下角
	area_move_to_corner(area, 'bottom_left')
	
	# 使用通用 init hook（带 selector）
	hook = farming_create_init_hook_with_selector(area['entity_selector'])
	path = area['corner_paths'][(get_pos_y(), get_pos_x())]
	path_move_along_with_hook(path, hook, None, True)

def __intercrop_area_process(area):
	# 处理实现：立即 harvest + plant
	# 确保在区域内
	area_move_to_corner(area, 'bottom_left')
	
	# 使用通用 intercrop process hook
	hook = farming_create_intercrop_process_hook(area['entity_selector'])
	path = area['corner_paths'][(get_pos_y(), get_pos_x())]
	path_move_along_with_hook(path, hook, None, True)
