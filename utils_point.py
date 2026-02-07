
def point(y, x):
	return (y, x)

def vector(y, x):
	return (y, x)

def vector_len(vec):
	return abs(vec[0]) + abs(vec[1])

# 在环面矩形计算 vec 的最短位移（输入必须在世界范围内）
def vector_warp(vec, world_size):
	y, x = vec
	half_world_size = world_size / 2
	
	if y > half_world_size:
		y -= world_size
	elif y < -half_world_size:
		y += world_size
	
	if x > half_world_size:
		x -= world_size
	elif x < -half_world_size:
		x += world_size
	
	return (y, x)

def point_add(current, delta):
	return (current[0] + delta[0], current[1] + delta[1])

def vector_add(current, delta):
	return (current[0] + delta[0], current[1] + delta[1])

def vector_negate(current):
	return (-current[0], -current[1])

def point_subtract(current, base):
	return (current[0] - base[0], current[1] - base[1])

def vector_subtract(current, base):
	return (current[0] - base[0], current[1] - base[1])

def vector_to_direction(vec):
	return __point_to_direction_cache[vec]
