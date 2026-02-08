# dict_utils.py
# 字典工具函数

def dict_get(d, key, default=None):
	# 安全获取字典值，如果key不存在则返回default
	if key in d:
		return d[key]
	return default

def dict_foreach(d, func):
	# 对字典每个值应用函数，返回新字典（键不变）
	result = {}
	for key in d:
		result[key] = func(d[key])
	return result
