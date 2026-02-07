# rect_utils.py
# 矩形基础属性和计算函数
# 性能敏感：避免不必要检查，直接解包操作

def rectangle(y, x, h, w):
	# 创建一个矩形，返回 (y, x, h, w)
	return (y, x, h, w)

def rectangle_height(rect):
	# 获取矩形高度
	return rect[2]

def rectangle_width(rect):
	# 获取矩形宽度
	return rect[3]

def rectangle_area(rect):
	# 计算矩形面积
	y, x, h, w = rect
	return h * w

def rectangle_bottom_left(rect):
	# 获取左下角坐标（原点）
	y, x, h, w = rect
	return (y, x)

def rectangle_top_right(rect):
	# 获取右上角坐标
	y, x, h, w = rect
	return (y + h - 1, x + w - 1)

def rectangle_get_vertices(rect):
	# 获取矩形的四个顶点坐标
	# 坐标系：y向上，x向右
	y, x, h, w = rect
	return [(y, x),  # 左下角
			(y, x + w - 1),  # 右下角
			(y + h - 1, x),  # 左上角
			(y + h - 1, x + w - 1)]  # 右上角

def rectangle_opposite_vertex(rect, vertex):
	# 获取矩形中与给定顶点相对的顶点坐标
	y, x, h, w = rect
	vy, vx = vertex
	return (2 * y + h - 1 - vy, 2 * x + w - 1 - vx)

def rectangle_can_contain(rect, h, w):
	# 判断矩形是否能容纳指定大小的子矩形
	rect_h, rect_w = rect[2], rect[3]
	return rect_h >= h and rect_w >= w

def rectangle_waste_area(rect, h, w):
	# 计算放置指定大小矩形后的面积浪费
	# 前提：rectangle_can_contain(rect, h, w) == True
	y, x, rect_h, rect_w = rect
	return rect_h * rect_w - h * w

def rectangle_contains_point(rect, point):
	# 判断点是否在矩形内
	y, x, h, w = rect
	py, px = point
	return y <= py < y + h and x <= px < x + w

def rectangle_contains_rect(rect, other):
	# 判断矩形是否完全包含另一个矩形
	y1, x1, h1, w1 = rect
	y2, x2, h2, w2 = other
	return (y1 <= y2 and 
			x1 <= x2 and 
			y1 + h1 >= y2 + h2 and 
			x1 + w1 >= x2 + w2)