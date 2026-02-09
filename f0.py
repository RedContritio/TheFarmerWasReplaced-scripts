# f0.py
# 多区域多无人机：给每个区域生成一架无人机（maze 只生成一架且出生点在矩形外）

from utils_rect_allocator import rect_allocator_instance_initialize, rect_allocator_instance_get, rect_allocator_enable_debug
from utils_drone import spawn_area_drone, spawn_maze_drone, area_step, run_maze_inline
from area_pumpkin import pumpkin_area
from area_sunflower import sunflower_area
from area_cactus import cactus_area
from area_companion import companion_area
from area_maze import maze_area

# 初始化全局分配器实例
WORLD_SIZE = get_world_size()
rect_allocator_instance_initialize(WORLD_SIZE)
rect_allocator_enable_debug(rect_allocator_instance_get(), True, 12)

# 按需求的默认配置
PUMPKIN_SIZE = (6, 6)
SUNFLOWER_SIZE = (10, 10)   # 全场只保留一块 sunflower 区域
CACTUS_SIZE = (12, 12)    # 仙人掌收益 ~ n^2，适当放大
COMPANION_SIZE = (6, 6)   # companion_area 至少 5x5
MAZE_SIZE = (16, 16)
MAZE_TIMES = 300

#
# 分配顺序很关键：maze 需要 16x16 的“完整正方形”，
# 如果先分配 cactus 等大矩形，容易碎片化导致 16x16 放不下。
# 因此这里先分配 maze（但仍最后才生成/运行 maze 无人机）。
#

# 先分配 maze（只分配矩形，不会立刻“产生迷宫”）
maze = maze_area(MAZE_SIZE, MAZE_TIMES)

# 分配其它区域（intercrop 已不再使用）
areas = []

cactus = cactus_area(CACTUS_SIZE)
if cactus != None:
	areas.append(cactus)

comp_carrot = companion_area((10, 10), Entities.Carrot)
if comp_carrot != None:
	areas.append(comp_carrot)

pumpkin = pumpkin_area(PUMPKIN_SIZE)
if pumpkin != None:
	areas.append(pumpkin)

sunflower = sunflower_area(SUNFLOWER_SIZE)
if sunflower != None:
	areas.append(sunflower)

# 只需要 grass / carrot / tree 三种 companion 区
comp_grass = companion_area(COMPANION_SIZE, Entities.Grass)
if comp_grass != None:
	areas.append(comp_grass)

comp_grass = companion_area(COMPANION_SIZE, Entities.Grass)
if comp_grass != None:
	areas.append(comp_grass)

comp_carrot = companion_area(COMPANION_SIZE, Entities.Carrot)
if comp_carrot != None:
	areas.append(comp_carrot)

comp_carrot = companion_area(COMPANION_SIZE, Entities.Carrot)
if comp_carrot != None:
	areas.append(comp_carrot)

comp_tree = companion_area(COMPANION_SIZE, Entities.Tree)
if comp_tree != None:
	areas.append(comp_tree)

# 为普通区域生成无人机（失败则主线程兜底）
fallback_areas = []
fallback_count = 0
for a in areas:
	drone = spawn_area_drone(a)
	if drone == None:
		fallback_areas.append(a)
		fallback_count += 1

# maze 最后生成无人机（保证生成位置在 maze 矩形外）
maze_drone = None
if maze != None:
	maze_drone = spawn_maze_drone(maze)
	if maze_drone == None:
		run_maze_inline(maze)
		maze = maze_area(MAZE_SIZE, MAZE_TIMES)
		if maze != None:
			maze_drone = spawn_maze_drone(maze)
			if maze_drone == None:
				run_maze_inline(maze)
				maze = None

fallback_i = 0
while True:
	if fallback_count > 0:
		if fallback_i >= fallback_count:
			fallback_i = 0
		area_step(fallback_areas[fallback_i], False)
		fallback_i += 1

	if maze_drone != None:
		if has_finished(maze_drone):
			wait_for(maze_drone)
			maze = maze_area(MAZE_SIZE, MAZE_TIMES)
			if maze != None:
				maze_drone = spawn_maze_drone(maze)
				if maze_drone == None:
					run_maze_inline(maze)
					maze = None
					maze_drone = None
			else:
				maze_drone = None

	do_a_flip()
