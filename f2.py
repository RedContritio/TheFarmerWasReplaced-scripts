from utils_route import rect_get_hamiltonian_path
from utils_move import route_move_along_with_hook
from utils_user import move_to

move_to(5, 5)
# 以当前位置为左下角，10*10 的矩形
cy = get_pos_y()
cx = get_pos_x()

def f(p, ha):
	till()

rect = (cy, cx, 10, 10)
route = rect_get_hamiltonian_path(rect, (cy, cx), "spiral_inward_cw")

route_move_along_with_hook(route, f)
