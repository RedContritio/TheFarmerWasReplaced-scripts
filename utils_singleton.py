# utils_singleton.py
# 通用单例：按 key 保存多个全局实例，供各模块按需使用

__store = {}

def singleton_initialize(key, value):
	# 设置指定 key 的单例值并返回
	__store[key] = value
	return value

def singleton_get(key):
	# 获取指定 key 的单例值（未初始化时返回 None）
	if key not in __store:
		return None
	return __store[key]

def singleton_destroy(key):
	# 销毁指定 key 的单例，便于重新初始化
	if key in __store:
		__store.pop(key)
