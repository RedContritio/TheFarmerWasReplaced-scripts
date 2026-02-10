from utils_math import sign

def op_pass():
    # pass语句，消耗 1 tick
    pass

# 四则运算测试函数
def op_add(a, b):
    # 加法运算，消耗 1 tick
    return a + b

def op_sub(a, b):
    # 减法运算，消耗 1 tick
    return a - b

def op_mul(a, b):
    # 乘法运算，消耗 1 tick
    return a * b

def op_div(a, b):
    # 除法运算，消耗 1 tick
    return a / b

def op_floordiv(a, b):
    # 整除运算，消耗 1 tick
    return a // b

def op_mod(a, b):
    # 取模运算，消耗 1 tick
    return a % b

def op_pow(a, b):
    # 幂运算，消耗 1 tick
    return a ** b

# 逻辑运算测试函数
def op_and(a, b):
    # 逻辑与运算，消耗 1 tick
    return a and b

def op_or(a, b):
    # 逻辑或运算，消耗 1 tick
    return a or b

# 一元运算测试函数（不消耗 tick）
def op_neg(a):
    # 一元负号，不消耗 tick
    return -a

def op_not(a):
    # 逻辑非，不消耗 tick
    return not a

# 索引、打包、解包测试函数
def op_subscript(lst, idx):
    # 索引操作，消耗 1 tick
    return lst[idx]

def op_pack(a, b):
    # 打包操作，消耗 1 tick
    result = (a, b)
    return result

def op_unpack(t):
    # 解包操作，消耗 1 tick
    a, b = t
    return a, b

# 链式调用测试函数
def op_chain_call(a):
    # 链式调用测试：a.abs().sign()，应该消耗 2 tick
    return a.abs().sign()