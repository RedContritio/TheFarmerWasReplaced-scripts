from utils_rect_allocator import rect_allocator_instance_initialize, rect_allocator_instance_get, rect_allocator_enable_debug
from utils_drone import spawn_area_drone, spawn_maze_drone, area_step, run_maze_inline
from area_pumpkin import pumpkin_area
from area_sunflower import sunflower_area
from area_cactus import cactus_area
from area_companion import companion_area
from area_maze import maze_area

# 多区域多无人机版本
# 约束（按你的描述）：
# - pumpkin：每块 6x6
# - sunflower：全场只保留一块（按 measure 顺序收获 = 高收益）
# - cactus：面积可适当更大
# - intercrop：不再使用
# - companion：只用 grass/carrot/tree，且至少 5x5
# - maze：生成后禁止飞入/飞出，因此只生成 1 架无人机，且生成时必须在 maze 矩形外

WORLD_SIZE = get_world_size()
rect_allocator_instance_initialize(WORLD_SIZE)
rect_allocator_enable_debug(rect_allocator_instance_get(), True, 12)

PUMPKIN_SIZE = (6, 6)
SUNFLOWER_SIZE = (10, 10)
CACTUS_SIZE = (12, 12)
COMPANION_SIZE = (6, 6)
MAZE_SIZE = (16, 16)
MAZE_TIMES = 300

#
# 分配顺序很关键：maze 需要 16x16 的“完整正方形”，
# 如果先分配 cactus 等大矩形，容易碎片化导致 16x16 放不下。
# 因此这里先分配 maze（但仍最后才生成/运行 maze 无人机）。
#

# 先分配 maze（只分配矩形，不会立刻“产生迷宫”）
maze = maze_area(MAZE_SIZE, MAZE_TIMES)

# 分配其它区域
areas = []

pumpkin = pumpkin_area(PUMPKIN_SIZE)
if pumpkin != None:
	areas.append(pumpkin)

sunflower = sunflower_area(SUNFLOWER_SIZE)
if sunflower != None:
	areas.append(sunflower)

cactus = cactus_area(CACTUS_SIZE)
if cactus != None:
	areas.append(cactus)

# 仅保留 grass / carrot / tree 三种 companion 区
comp_grass = companion_area(COMPANION_SIZE, Entities.Grass)
if comp_grass != None:
	areas.append(comp_grass)

comp_carrot = companion_area(COMPANION_SIZE, Entities.Carrot)
if comp_carrot != None:
	areas.append(comp_carrot)

comp_tree = companion_area(COMPANION_SIZE, Entities.Tree)
if comp_tree != None:
	areas.append(comp_tree)

# 先给普通区域生成无人机（能生成就交给无人机；失败则主线程兜底做）
fallback_areas = []
fallback_count = 0
for a in areas:
	drone = spawn_area_drone(a)
	if drone == None:
		fallback_areas.append(a)
		fallback_count += 1

# 最后生成 maze 无人机（生成点保持在 maze 矩形外）
maze_drone = None
if maze != None:
	maze_drone = spawn_maze_drone(maze)
	if maze_drone == None:
		# 没有无人机能力：主线程直接跑完一次 maze
		run_maze_inline(maze)
		# 约定：迷宫完成后再生成一个迷宫（同样不做错误检查）
		maze = maze_area(MAZE_SIZE, MAZE_TIMES)
		if maze != None:
			maze_drone = spawn_maze_drone(maze)
			if maze_drone == None:
				run_maze_inline(maze)
				maze = None

# 主线程：
# - 兜底执行所有 spawn 失败的区域（轮询）
# - 检测 maze_drone 完成后，自动再开下一局 maze
fallback_i = 0
while True:
	# 兜底区域轮询执行（每个循环只处理一个区域，避免单区域占满）
	if fallback_count > 0:
		if fallback_i >= fallback_count:
			fallback_i = 0
		area_step(fallback_areas[fallback_i], False)
		fallback_i += 1

	# maze 完成检测：完成就回收并再生成一个新的 maze
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
