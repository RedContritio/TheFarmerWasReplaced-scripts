# from area_companion import alloc_companion_area
# from area_pumpkin import alloc_pumpkin_area
# from area_sunflower import alloc_sunflower_area
from area_intercrop import alloc_intercrop_area
# from area_cactus import alloc_cactus_area
# from area_maze import alloc_maze_area
# from utils_move import move_to

# area_ids = []
# area_ids.append(alloc_sunflower_area((0, 0, 6, 6)))
# area_ids.append(alloc_pumpkin_area((0, 6, 6, 6)))
# #area_ids.append(alloc_cactus_area((6, 0, 6, 6)))
# area_ids.append(alloc_companion_area((6, 6, 6, 6),
#     [Entities.Grass, Entities.Tree, Entities.Carrot]))

# while True:
#     for ai in area_ids:
#         process_area(ai)

G = {}
G["half_world_size"] = get_world_size() / 2
G["world_size"] = get_world_size()

clear()

areas = []
# areas.append(alloc_pumpkin_area(0, 0, 6, 6))
areas.append(alloc_intercrop_area(0, 6, 6, 6))
# areas.append(alloc_intercrop_area(0, 12, 6, 5))
# areas.append(alloc_intercrop_area(0, 17, 6, 5))
# areas.append(alloc_sunflower_area(6, 0, 6, 6))
# areas.append(alloc_maze_area(6, 6, 16, 16, 300))
# areas.append(alloc_cactus_area(12, 0, 10, 6))

for a in areas:

	def process_area_loop():
		processor = a["processor"]
		while True:
			processor(a)
			do_a_flip()

	spawn_drone(process_area_loop)

while True:
	do_a_flip()
