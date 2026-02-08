__direction_to_vector2d_cache = {
	North: (1, 0),
	South: (-1, 0),
	East: (0, 1),
	West: (0, -1)
}

__vector2d_to_direction_cache = {
	(1, 0): North,
	(-1, 0): South,
	(0, 1): East,
	(0, -1): West
}

__direction_to_vector1d_cache = {
	North: 1,
	South: -1,
	East: 1,
	West: -1
}

__vector1d_y_to_direction_cache = {
	1: North,
	-1: South,
	0: None
}

__vector1d_x_to_direction_cache = {
	1: East,
	-1: West,
	0: None
}

__direction_negate_cache = {
	North: South,
	South: North,
	East: West,
	West: East
}

Directions = [North, South, West, East]

def direction_negate(direction):
	return __direction_negate_cache[direction]

def direction_to_vector2d(direction):
	return __direction_to_vector2d_cache[direction]

def direction_to_vector1d(direction):
	return __direction_to_vector1d_cache[direction]

def vector1d_x_to_direction(vec):
	return __vector1d_x_to_direction_cache[vec]

def vector1d_y_to_direction(vec):
	return __vector1d_y_to_direction_cache[vec]

def vector_to_direction(vec):
	return __vector2d_to_direction_cache[vec]