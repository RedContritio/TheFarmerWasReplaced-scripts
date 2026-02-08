# move_utils.py
# 移动和路径执行工具

from utils_direction import direction_to_vector2d
from utils_point import point_subtract
from utils_route import vector_get_path

def path_move_along(path):
	# 沿路径移动
	for d in path:
		move(d)

def __move_to_point_no_hook(target_point):
	# 无 hook 地移动到目标点
	# 注意：这是“就位移动”，不应触发遍历 hook
	current = (get_pos_y(), get_pos_x())
	vec = point_subtract(target_point, current)
	pre_path = vector_get_path(vec)
	path_move_along(pre_path)

def route_move_along(route):
	# route: (path, start_point)
	path, start_point = route
	__move_to_point_no_hook(start_point)
	path_move_along(path)

def route_move_along_with_hook(route, hook, hook_arg=None, hook_for_start=True):
	# route: (path, start_point)
	# hook 仅在到达 start_point 之后开始触发
	path, start_point = route
	__move_to_point_no_hook(start_point)
	
	y, x = start_point
	if hook_for_start:
		hook((y, x), hook_arg)
	
	for d in path:
		move(d)
		dy, dx = direction_to_vector2d(d)
		y += dy
		x += dx
		hook((y, x), hook_arg)

def path_move_along_with_hook(path, hook, hook_arg=None, hook_for_start=True):
	# 沿路径移动并执行 hook
	# hook 签名：hook(point, hook_arg)
	# point: (y, x) 当前坐标
	
	# 获取起始位置
	y = get_pos_y()
	x = get_pos_x()
	
	# 处理起点
	if hook_for_start:
		hook((y, x), hook_arg)
	
	# 沿路径移动
	for d in path:
		move(d)
		
		# 根据方向更新坐标（避免重复调用 get_pos）
		dy, dx = direction_to_vector2d(d)
		y += dy
		x += dx
		
		hook((y, x), hook_arg)


def path_swap_and_move_with_hook(path, hook, hook_arg=None):
	# 沿路径 swap + move 并执行 hook
	# hook 签名：hook(current_point, direction, next_point, hook_arg)
	# 在每次 swap + move 之前调用 hook
	
	# 获取起始位置
	y = get_pos_y()
	x = get_pos_x()
	
	# 沿路径 swap + move
	for d in path:
		# 计算下一个位置
		dy, dx = direction_to_vector2d(d)
		next_y = y + dy
		next_x = x + dx
		
		# 调用 hook（在 swap 之前）
		hook((y, x), d, (next_y, next_x), hook_arg)
		
		# swap + move
		swap(d)
		move(d)
		
		# 更新坐标
		y = next_y
		x = next_x
