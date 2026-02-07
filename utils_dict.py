# dict_utils.py
# 字典工具函数

def dict_get(d, key, default=None):
	# 安全获取字典值，如果key不存在则返回default
	if key not in d:
		return default
	return d[key]
