# pyright: ignore

from utils_direction import direction_to_vector2d, vector_to_direction
from utils_route import route_astar_path

#
# 恐龙区域（排他：覆盖整个世界）
# - 戴上 Hats.Dinosaur_Hat 后脚下生成苹果；在苹果上 measure() 得下一个苹果 (x,y)
# - 离开苹果格时吃掉并增长尾巴；尾巴铺满全图后 move() 失败，换帽子收骨头
#
# 策略：每吃到一个苹果后用 A*（曼哈顿启发）算一条到下一个苹果的路径；为免局部最优，限定走向：
# 奇数行只能向右、偶数行只能向左；奇数列只能向下、偶数列只能向上。每步沿路径走一格。
#


def __dir_between(a, b):
	ay, ax = a
	by, bx = b
	return vector_to_direction((by - ay, bx - ax))


def __in_bounds(p, world_size):
	y, x = p
	return 0 <= y and y < world_size and 0 <= x and x < world_size


def __measure_next_apple_point():
	m = measure()
	next_x = m[0]  # type: ignore[index]
	next_y = m[1]  # type: ignore[index]
	return (next_y, next_x)


def dinosaur_run(world_size=None):
	if world_size == None:
		world_size = get_world_size()

	change_hat(Hats.Dinosaur_Hat)

	st = {}
	st["head"] = (get_pos_y(), get_pos_x())
	st["grow_next_move"] = False
	st["apples_eaten"] = 0

	snake = [st["head"]]
	occ = {st["head"]: True}
	body_set = set()
	body_set.add(st["head"])
	st["snake_len"] = 1

	apple_target = __measure_next_apple_point()
	st["grow_next_move"] = True

	def get_neighbors(node):
		# 严格奇偶规则：奇数行只能向右，偶数行只能向左；奇数列只能向下，偶数列只能向上。
		# 不增长时允许下一步是尾尖。
		y, x = node
		out = []
		tail = snake[0]
		allow_tail = not st["grow_next_move"]

		def add(np):
			if __in_bounds(np, world_size):
				if np not in body_set or (allow_tail and np == tail):
					out.append(np)

		if (y % 2) == 1:
			add((y, x + 1))
		else:
			add((y, x - 1))
		if (x % 2) == 1:
			add((y + 1, x))
		else:
			add((y - 1, x))
		return out

	def __try_step(d):
		if d == None:
			return False
		dy, dx = direction_to_vector2d(d)
		head = st["head"]
		ny = head[0] + dy
		nx = head[1] + dx
		np = (ny, nx)
		if not __in_bounds(np, world_size):
			return False
		if np in occ:
			if not st["grow_next_move"]:
				tail = snake[0]
				if np != tail:
					return False
			else:
				return False
		ok = move(d)
		if not ok:
			return False
		if st["grow_next_move"]:
			st["grow_next_move"] = False
			st["apples_eaten"] += 1
			st["snake_len"] += 1
		else:
			old_tail = snake[0]
			snake.pop(0)
			if old_tail in occ:
				occ.pop(old_tail)
			if old_tail in body_set:
				body_set.remove(old_tail)
		snake.append(np)
		occ[np] = True
		body_set.add(np)
		st["head"] = np
		return True

	# 开局若在边界则先走到不碰边的一格，避免奇偶规则在边界无邻居
	if world_size >= 3:
		while True:
			cy = get_pos_y()
			cx = get_pos_x()
			if cy >= 1 and cy <= world_size - 2 and cx >= 1 and cx <= world_size - 2:
				break
			d = None
			if cy < 1:
				d = vector_to_direction((1, 0))
			elif cy > world_size - 2:
				d = vector_to_direction((-1, 0))
			elif cx < 1:
				d = vector_to_direction((0, 1))
			elif cx > world_size - 2:
				d = vector_to_direction((0, -1))
			if d == None:
				break
			if not __try_step(d):
				break

	while True:
		head = st["head"]
		if head == apple_target:
			apple_target = __measure_next_apple_point()
			st["grow_next_move"] = True
			continue

		def heuristic(node):
			return abs(apple_target[0] - node[0]) + abs(apple_target[1] - node[1])
		path = route_astar_path(head, apple_target, get_neighbors, heuristic)
		if path == None:
			break
		n_pts = len(path)
		if n_pts < 2:  # type: ignore[operator]
			continue
		completed = True
		i = 1
		while i < n_pts:  # type: ignore[operator]
			d = __dir_between(path[i - 1], path[i])
			if not __try_step(d):
				completed = False
				break
			i += 1
		if not completed:
			break

	change_hat(Hats.Straw_Hat)
	tail_len = st["snake_len"] - 1
	quick_print(
		"[dinosaur] eaten", st["apples_eaten"], "tail", tail_len, "bones", tail_len**2
	)
	return True


# 注意：本文件是模块（供 `f*.py` / `main.py` 调用），不要在 import 时自动执行。
