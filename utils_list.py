# list_utils.py
# 列表相关工具函数
# 性能优化版本

def __list_insertion_sort(lst, left, right, less_func):
	# 插入排序，适合小规模数据
	i = left + 1
	while i <= right:
		j = i
		while j > left and less_func(lst[j], lst[j - 1]):
			# 交换
			lst[j], lst[j - 1] = lst[j - 1], lst[j]
			j -= 1
		i += 1

def __list_partition(lst, left, right, less_func):
	# 快速排序的分区函数
	pivot_index = (left + right) // 2
	pivot = lst[pivot_index]
	
	# 交换 pivot 到最右边
	lst[pivot_index], lst[right] = lst[right], lst[pivot_index]
	
	store_index = left
	i = left
	while i < right:
		if less_func(lst[i], pivot):
			lst[i], lst[store_index] = lst[store_index], lst[i]
			store_index += 1
		i += 1
	
	# 把 pivot 放回正确位置
	lst[store_index], lst[right] = lst[right], lst[store_index]
	return store_index

def __list_quick_sort_impl(lst, left, right, less_func):
	# 快速排序实现，递归版本
	# 小规模数据切换到插入排序
	if right - left < 16:  # 阈值设为16
		__list_insertion_sort(lst, left, right, less_func)
		return
	
	if left < right:
		pivot_index = __list_partition(lst, left, right, less_func)
		__list_quick_sort_impl(lst, left, pivot_index - 1, less_func)
		__list_quick_sort_impl(lst, pivot_index + 1, right, less_func)

def __list_sort_small(lst, less_func):
	# 小列表排序（完全使用插入排序）
	n = len(lst)
	if n <= 1:
		return
	
	# 插入排序
	i = 1
	while i < n:
		j = i
		while j > 0 and less_func(lst[j], lst[j - 1]):
			# 交换
			lst[j], lst[j - 1] = lst[j - 1], lst[j]
			j -= 1
		i += 1

def list_sort_by(lst, less_func):
	# 对列表排序，less_func(a, b) 返回 True 表示 a 应该在 b 前面
	if len(lst) <= 1:
		# 创建副本返回
		result = []
		for item in lst:
			result.append(item)
		return result
	
	# 创建副本
	result = []
	for item in lst:
		result.append(item)
	
	# 根据列表长度选择合适的排序算法
	n = len(result)
	if n < 20:  # 小列表完全使用插入排序
		__list_sort_small(result, less_func)
	else:  # 大列表使用优化快速排序
		__list_quick_sort_impl(result, 0, n - 1, less_func)
	
	return result

def list_sort_by_key(lst, key_func, reverse=False):
	# 按key函数排序
	def less_func(a, b):
		key_a = key_func(a)
		key_b = key_func(b)
		if reverse:
			return key_a > key_b
		else:
			return key_a < key_b
	
	return list_sort_by(lst, less_func)

def list_sort_by_yx(lst, get_y_func, get_x_func):
	# 按y坐标主序，x坐标次序排序
	def less_func(a, b):
		y_a = get_y_func(a)
		y_b = get_y_func(b)
		if y_a != y_b:
			return y_a < y_b
		
		x_a = get_x_func(a)
		x_b = get_x_func(b)
		return x_a < x_b
	
	return list_sort_by(lst, less_func)

def list_filter(lst, filter_func):
	# 过滤列表元素
	result = []
	for item in lst:
		if filter_func(item):
			result.append(item)
	return result

def list_find_index(lst, match_func):
	# 查找第一个匹配元素的索引
	for i in range(len(lst)):
		if match_func(lst[i]):
			return i
	return -1

def list_remove_first(lst, match_func):
	# 移除第一个匹配的元素
	for i in range(len(lst)):
		if match_func(lst[i]):
			lst.pop(i)
			return True
	return False

def list_binary_search(lst, key_func, target_key):
	# 在已排序列表中二分查找
	left = 0
	right = len(lst) - 1
	
	while left <= right:
		mid = (left + right) // 2
		mid_key = key_func(lst[mid])
		
		if mid_key == target_key:
			return mid
		elif mid_key < target_key:
			left = mid + 1
		else:
			right = mid - 1
	
	return -1

def list_insert_sorted(lst, item, less_func):
	# 在已排序列表中插入元素，保持有序
	# 返回插入位置
	n = len(lst)
	
	if n == 0:
		lst.append(item)
		return 0
	
	# 二分查找插入位置
	left = 0
	right = n - 1
	pos = n  # 默认插入到最后
	
	while left <= right:
		mid = (left + right) // 2
		if less_func(item, lst[mid]):
			pos = mid
			right = mid - 1
		else:
			left = mid + 1
	
	# 在pos位置插入
	if pos == n:
		lst.append(item)
	else:
		# 需要手动插入
		lst.append(None)  # 先扩展列表
		i = n
		while i > pos:
			lst[i] = lst[i - 1]
			i -= 1
		lst[pos] = item
	
	return pos