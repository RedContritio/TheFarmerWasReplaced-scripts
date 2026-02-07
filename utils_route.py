from utils_direction import (
	vector1d_y_to_direction,
	vector1d_x_to_direction,
	direction_negate,
)
from utils_math import sign


def __vector1d_y_append_path_helper(dy, path):
	dir = dy.sign().vector1d_y_to_direction()
	for _ in range(abs(dy)):
		path.append(dir)
	return path


def __vector1d_x_append_path_helper(dx, path):
	dir = dx.sign().vector1d_x_to_direction()
	for _ in range(abs(dx)):
		path.append(dir)
	return path


def __vector2d_append_path_helper(vec, path):
	__vector1d_y_append_path_helper(vec[0], path)
	__vector1d_x_append_path_helper(vec[1], path)
	return path


def vector_get_path(vec):
	path = []
	__vector2d_append_path_helper(vec, path)
	return path


def __vector_get_hamiltonian_path_snake_x(vec, path):
	y, x = vec
	dy = y.sign().vector1d_y_to_direction()
	dx = x.sign().vector1d_x_to_direction()
	x_abs = abs(x)

	for j in range(x_abs):
		path.append(dx)

	for i in range(abs(y)):
		path.append(dy)
		dx = dx.direction_negate()

		for j in range(x_abs):
			path.append(dx)

	return path


def __vector_get_hamiltonian_path_snake_y(vec, path):
	y, x = vec
	dy = y.sign().vector1d_y_to_direction()
	dx = x.sign().vector1d_x_to_direction()
	y_abs = abs(y)

	for i in range(y_abs):
		path.append(dy)

	for j in range(abs(x)):
		path.append(dx)
		dy = dy.direction_negate()

		for i in range(y_abs):
			path.append(dy)

	return path


# vec 构成的矩阵中的哈密顿路径
def vector_get_hamiltonian_path(vec, mode="snake_x"):
	y, x = vec
	path = []

	if y == 0:
		__vector1d_x_append_path_helper(x, path)
		return path
	if x == 0:
		__vector1d_y_append_path_helper(y, path)
		return path

	if mode == "snake_x":
		return __vector_get_hamiltonian_path_snake_x(vec, path)
	elif mode == "snake_y":
		return __vector_get_hamiltonian_path_snake_y(vec, path)
	else:
		return __vector_get_hamiltonian_path_snake_x(vec, path)
