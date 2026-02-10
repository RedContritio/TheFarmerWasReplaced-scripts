# intercrop_area.py
# 杂种区（多种作物混种）

from utils_area import (
    __area_init,
    area_init_attr,
    area_move_to_nearest_corner,
    area_process_begin,
    area_process_end,
)
from utils_farming import (
    farming_create_init_hook_with_selector,
    farming_create_intercrop_process_hook,
    farming_create_do_harvest,
)
from utils_move import route_move_along_with_hook

DEFAULT_INTERCROP_ENTITIES = [Entities.Grass, Entities.Tree, Entities.Carrot]


def intercrop_area(size, entities=None, allocator=None):
    # 创建杂种区
    # size: (h, w)

    if entities == None:
        entities = DEFAULT_INTERCROP_ENTITIES

    # 使用公共初始化逻辑
    a, rect_id, rect = __area_init("intercrop", size, allocator)
    if a == None:
        return None

    # 设置杂种区特有属性
    a["entities"] = entities

    # 设置处理器
    a["area_init"] = __intercrop_area_init
    a["area_processor"] = __intercrop_area_process

    # 创建 entity selector 函数
    def entity_selector(point):
        y, x = point
        i = (y + x) % len(entities)
        return entities[i]

    a["entity_selector"] = entity_selector

    return a


def __intercrop_area_init(area):
    # 初始化实现
    # 移动到最近顶点
    area_move_to_nearest_corner(area)

    # 使用通用 init hook（带 selector）
    hook = farming_create_init_hook_with_selector(area["entity_selector"])
    route = area["corner_paths"][(get_pos_y(), get_pos_x())]
    route_move_along_with_hook(route, hook, None, True)


def __intercrop_area_process(area):
    start_tick = area_process_begin(area)
    harvest_dict = area["last_process_harvest"]
    do_harvest = farming_create_do_harvest(harvest_dict)

    # 处理实现：立即 harvest + plant
    # 确保在区域内
    area_move_to_nearest_corner(area)

    # 使用通用 intercrop process hook
    hook = farming_create_intercrop_process_hook(area["entity_selector"], do_harvest)
    route = area["corner_paths"][(get_pos_y(), get_pos_x())]
    route_move_along_with_hook(route, hook, None, True)
    area_process_end(area, start_tick)
