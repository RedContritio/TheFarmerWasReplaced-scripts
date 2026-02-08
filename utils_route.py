from utils_direction import (
	vector_to_direction,
	vector1d_y_to_direction,
	vector1d_x_to_direction,
	direction_negate
)
from utils_math import sign
from utils_list import list_foreach
from utils_dict import dict_foreach
from utils_rect import (
	rectangle_opposite_vertex,
	rectangle_center,
	rectangle_nearest_vertex
)
from utils_point import point_subtract


# 螺旋方向向量：(outward/inward, clockwise/counterclockwise) -> [(dy, dx), ...]
__SPIRAL_DIRECTION_VECTORS = {
	("outward", "clockwise"): [(0, 1), (-1, 0), (0, -1), (1, 0)],
	("outward", "counterclockwise"): [(0, -1), (-1, 0), (0, 1), (1, 0)],
	("inward", "clockwise"): [(0, 1), (1, 0), (0, -1), (-1, 0)],
	("inward", "counterclockwise"): [(1, 0), (0, 1), (-1, 0), (0, -1)]
}

#
# 内旋螺旋的步数规律：
# - 每一圈 4 段，除了最后一段为了“进入内圈”少走 1 步（即 -2），其余都是边长 -1
# - 具体用 w 还是 h 取决于该段方向是横向还是纵向（不能简单随方向序列旋转公式）

def __vectors_to_directions(vecs):
	return list_foreach(vecs, vector_to_direction)

# 将方向向量转换为方向枚举
__SPIRAL_DIRECTIONS = dict_foreach(__SPIRAL_DIRECTION_VECTORS, __vectors_to_directions)


def __vector1d_y_append_path_helper(dy, path):
	direction = dy.sign().vector1d_y_to_direction()
	for _ in range(abs(dy)):
		path.append(direction)
	return path


def __vector1d_x_append_path_helper(dx, path):
	direction = dx.sign().vector1d_x_to_direction()
	for _ in range(abs(dx)):
		path.append(direction)
	return path


def __vector2d_append_path_helper(vec, path):
	__vector1d_y_append_path_helper(vec[0], path)
	__vector1d_x_append_path_helper(vec[1], path)
	return path


def vector_get_path(vec):
	path = []
	__vector2d_append_path_helper(vec, path)
	return path


def __rect_append_hamiltonian_path_snake_x(rect, path, start_point):
	path_start = rectangle_nearest_vertex(rect, start_point)
	opposite = rectangle_opposite_vertex(rect, path_start)
	vec = point_subtract(opposite, path_start)
	
	y, x = vec
	dy = y.sign().vector1d_y_to_direction()
	dx = x.sign().vector1d_x_to_direction()
	x_abs = abs(x)
	
	for _ in range(x_abs):
		path.append(dx)
	for _ in range(abs(y)):
		path.append(dy)
		dx = dx.direction_negate()
		for _ in range(x_abs):
			path.append(dx)
	
	return path_start


def __rect_append_hamiltonian_path_snake_y(rect, path, start_point):
	path_start = rectangle_nearest_vertex(rect, start_point)
	opposite = rectangle_opposite_vertex(rect, path_start)
	vec = point_subtract(opposite, path_start)
	
	y, x = vec
	dy = y.sign().vector1d_y_to_direction()
	dx = x.sign().vector1d_x_to_direction()
	y_abs = abs(y)
	
	for _ in range(y_abs):
		path.append(dy)
	for _ in range(abs(x)):
		path.append(dx)
		dy = dy.direction_negate()
		for _ in range(y_abs):
			path.append(dy)
	
	return path_start


def __rect_spiral_peel_segments(rect, start_corner, mode_key):
	# 生成“外层剥洋葱”的 inward 螺旋段列表：[(direction, count), ...]
	# 只生成段（不是逐步路径），段数约 O(h+w)，性能更好
	y, x, h, w = rect
	min_y = y
	max_y = y + h - 1
	min_x = x
	max_x = x + w - 1
	
	py, px = start_corner
	vecs = __SPIRAL_DIRECTION_VECTORS[("inward", mode_key)]
	dirs = __SPIRAL_DIRECTIONS[("inward", mode_key)]
	
	# 旋转方向序列：确保第一步不会立刻越界（退化尺寸也更稳）
	rot = 0
	for r in range(4):
		dy, dx = vecs[r]
		ny = py + dy
		nx = px + dx
		if min_y <= ny and ny <= max_y and min_x <= nx and nx <= max_x:
			rot = r
			break
	
	rot_vecs = []
	rot_dirs = []
	for i in range(4):
		rot_vecs.append(vecs[(i + rot) % 4])
		rot_dirs.append(dirs[(i + rot) % 4])
	
	segments = []
	while min_x <= max_x and min_y <= max_y:
		for i in range(4):
			dy, dx = rot_vecs[i]
			d = rot_dirs[i]
			
			if dy == 0 and dx == 1:
				cnt = max_x - px
			elif dy == 0 and dx == -1:
				cnt = px - min_x
			elif dy == 1 and dx == 0:
				cnt = max_y - py
			else:
				cnt = py - min_y
			
			if cnt > 0:
				segments.append((d, cnt))
				py = py + dy * cnt
				px = px + dx * cnt
			
			# 走完一条边后收缩边界
			if dy == 0:
				if py == min_y:
					min_y = min_y + 1
				else:
					max_y = max_y - 1
			else:
				if px == min_x:
					min_x = min_x + 1
				else:
					max_x = max_x - 1
			
			if not (min_x <= max_x and min_y <= max_y):
				break
	
	return segments, (py, px)


def __rect_append_hamiltonian_path_spiral_outward(rect, path, start_point, mode):
	# outward：走到中心后，严格不重复走满整个 rect（Hamiltonian path）
	# 性能敏感：用“段”反向输出，不构造整条 inward 路径
	y, x, h, w = rect
	ideal_center = rectangle_center(rect)
	
	# 退化为 1D：直接线性走满（从中心向一侧，再反向扫另一侧）
	if h == 1:
		# 1xN 线性图无法从中心作为 Hamiltonian 起点而不重复
		# 这里选择从左端点开始扫满
		for _ in range(w - 1):
			path.append(East)
		return (y, x)
	if w == 1:
		# Nx1 线性图无法从中心作为 Hamiltonian 起点而不重复
		# 这里选择从下端点开始扫满
		for _ in range(h - 1):
			path.append(North)
		return (y, x)
	
	# outward 的旋向与 inward 反转后的旋向相反：outward_cw = reverse(inward_ccw)
	if mode == "spiral_outward_cw":
		inward_mode_key = "counterclockwise"
	else:
		inward_mode_key = "clockwise"
	
	# 选择一个边界起点，使剥洋葱 inward 的终点刚好落在 center
	corners = [
		(y, x),
		(y, x + w - 1),
		(y + h - 1, x),
		(y + h - 1, x + w - 1)
	]
	chosen_segments = None
	chosen_end = corners[0]
	best_dist = 999999
	for corner in corners:
		segs, end_point = __rect_spiral_peel_segments(rect, corner, inward_mode_key)
		dy = end_point[0] - ideal_center[0]
		dx = end_point[1] - ideal_center[1]
		dist = abs(dy) + abs(dx)
		if dist < best_dist:
			best_dist = dist
			chosen_segments = segs
			chosen_end = end_point
			if dist == 0:
				break
	
	# 若没有段（极端退化尺寸已在上面 return），则结束
	if chosen_segments == None:
		return ideal_center
	
	# 反向输出 outward：段逆序 + 方向取反
	seg_len = len(chosen_segments)
	for i in range(seg_len - 1, -1, -1):
		d, cnt = chosen_segments[i]
		nd = d.direction_negate()
		for _ in range(cnt):
			path.append(nd)
	
	return chosen_end


def __spiral_inward_rotation_offset(vy, vx):
	# 根据起点角到对角的方向，得到首边方向在 [东,北,西,南] 中的偏移
	sy = sign(vy)
	sx = sign(vx)
	if sy > 0:
		if sx > 0:
			return 0
		else:
			return 1
	elif sy < 0:
		if sx < 0:
			return 2
		else:
			return 3
	else:
		if sx > 0:
			return 0
		else:
			return 1


def __rect_append_hamiltonian_path_spiral_inward(rect, path, start_point, mode):
	path_start = rectangle_nearest_vertex(rect, start_point)
	opposite = rectangle_opposite_vertex(rect, path_start)
	vec = point_subtract(opposite, path_start)
	
	y, x, h, w = rect
	vy, vx = vec
	
	clockwise = mode == "spiral_inward_cw"
	if clockwise:
		mode_key = "clockwise"
	else:
		mode_key = "counterclockwise"
	base_dirs = __SPIRAL_DIRECTIONS[("inward", mode_key)]
	rot = __spiral_inward_rotation_offset(vy, vx)
	dirs = []
	vecs = __SPIRAL_DIRECTION_VECTORS[("inward", mode_key)]
	rot_vecs = []
	for i in range(4):
		dirs.append(base_dirs[(i + rot) % 4])
		rot_vecs.append(vecs[(i + rot) % 4])
	
	# 直接用“剥洋葱”方式在边界内走满：对任意长方形都正确且不需要特殊补丁
	min_y = y
	max_y = y + h - 1
	min_x = x
	max_x = x + w - 1
	py, px = path_start
	
	while min_x <= max_x and min_y <= max_y:
		for i in range(4):
			dy, dx = rot_vecs[i]
			d = dirs[i]
			
			if dy == 0 and dx == 1:
				cnt = max_x - px
			elif dy == 0 and dx == -1:
				cnt = px - min_x
			elif dy == 1 and dx == 0:
				cnt = max_y - py
			else:
				cnt = py - min_y
			
			for _ in range(cnt):
				path.append(d)
			
			py = py + dy * cnt
			px = px + dx * cnt
			
			# 收缩刚走过的那条边
			if dy == 0:
				if py == min_y:
					min_y = min_y + 1
				else:
					max_y = max_y - 1
			else:
				if px == min_x:
					min_x = min_x + 1
				else:
					max_x = max_x - 1
			
			if not (min_x <= max_x and min_y <= max_y):
				break
	
	return path_start


__RECT_MODE_HANDLERS = {
	"snake_x": __rect_append_hamiltonian_path_snake_x,
	"snake_y": __rect_append_hamiltonian_path_snake_y,
	"spiral_outward_cw": __rect_append_hamiltonian_path_spiral_outward,
	"spiral_outward_ccw": __rect_append_hamiltonian_path_spiral_outward,
	"spiral_inward_cw": __rect_append_hamiltonian_path_spiral_inward,
	"spiral_inward_ccw": __rect_append_hamiltonian_path_spiral_inward
}


def rect_get_hamiltonian_path(rect, start_point, mode="snake_x"):
	path = []
	handler = __RECT_MODE_HANDLERS[mode]
	if mode == "snake_x" or mode == "snake_y":
		route_start = handler(rect, path, start_point)
	else:
		route_start = handler(rect, path, start_point, mode)
	return (path, route_start)
