# f0.py
# 测试用例：分配并测试所有区域类型

from utils_rect_allocator import rect_allocator_instance_initialize
from area_pumpkin import pumpkin_area
from area_sunflower import sunflower_area
from area_cactus import cactus_area
from area_intercrop import intercrop_area
from area_companion import companion_area
from area_maze import maze_area

# 初始化全局分配器实例
WORLD_SIZE = get_world_size()
rect_allocator_instance_initialize(WORLD_SIZE)

# 分配并初始化各类区域（使用默认全局分配器实例）
pumpkin = pumpkin_area((6, 6))
sunflower = sunflower_area((6, 6))
cactus = cactus_area((6, 6))
intercrop = intercrop_area((6, 6), [Entities.Carrot, Entities.Grass, Entities.Tree])
companion = companion_area((6, 6), [Entities.Bush, Entities.Carrot])
maze = maze_area((6, 6), 3)

# 初始化所有区域
quick_print("初始化南瓜区域")
pumpkin["area_init"](pumpkin)

# quick_print("初始化向日葵区域")
# sunflower["area_init"](sunflower)

# quick_print("初始化仙人掌区域")
# cactus["area_init"](cactus)

# quick_print("初始化杂种区域")
# intercrop["area_init"](intercrop)

# quick_print("初始化同伴区域")
# companion["area_init"](companion)

# quick_print("初始化迷宫区域")
# maze["area_init"](maze)

quick_print("所有区域初始化完成")

# 测试迷宫区域处理（迷宫会一次性完成所有寻宝）
# quick_print("处理迷宫区域")
# maze["area_processor"](maze)

# 测试其他区域处理循环
quick_print("开始处理循环")

for i in range(3):
	quick_print("=== 循环", i + 1, "===")

	quick_print("处理南瓜区域")
	pumpkin["area_processor"](pumpkin)

	# quick_print("处理向日葵区域")
	# sunflower["area_processor"](sunflower)

	# quick_print("处理仙人掌区域")
	# cactus["area_processor"](cactus)

	# quick_print("处理杂种区域")
	# intercrop["area_processor"](intercrop)

	# quick_print("处理同伴区域")
	# companion["area_processor"](companion)

quick_print("测试完成")
