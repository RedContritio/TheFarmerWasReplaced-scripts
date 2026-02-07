# move_utils.py
# 移动和路径执行工具

from utils_direction import direction_to_vector2d

def path_move_along(path):
	# 沿路径移动
	for d in path:
		move(d)

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
