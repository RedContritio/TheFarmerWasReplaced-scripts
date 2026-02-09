"""
Singleton tick system for game time tracking
"""
import inspect
import os
import threading

class TickSystem:
    """单例 tick 系统，确保全局只有一个 tick 计数器"""
    _instance = None
    _tick = 0
    
    # 线程局部变量，用于防止在检查调用栈时触发 tick 计数
    _checking_stack = threading.local()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_tick(cls):
        """获取当前 tick 值"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._tick
    
    @classmethod
    def _should_count_tick(cls):
        """检查调用栈，判断是否应该计数 tick
        只有当调用来自 Save0 根目录的项目代码时才返回 True
        """
        # 防止在检查调用栈时触发 tick 计数（避免无限递归）
        if getattr(cls._checking_stack, 'active', False):
            return False
        
        try:
            cls._checking_stack.active = True
            # 获取调用栈
            stack = inspect.stack()
        
            # 从栈顶往下找（跳过当前函数和 add_ticks）
            for frame_info in stack[2:]:  # 跳过 _should_count_tick 和 add_ticks
                filename = frame_info.filename
                
                # 检查是否是 Save0 根目录下的文件
                if 'Save0' in filename:
                    # 排除 test/ 目录
                    if '/test/' in filename or '\\test\\' in filename:
                        continue
                    
                    # 排除 tick_system.py 本身
                    if 'tick_system.py' in filename:
                        continue
                    
                    # 检查是否直接在 Save0 根目录下（不在子目录中）
                    save0_index = filename.find('Save0')
                    if save0_index != -1:
                        # 获取 Save0 之后的路径部分
                        after_save0 = filename[save0_index + 6:]  # 6 = len('Save0/')
                        # 如果路径中没有更多的目录分隔符（除了文件名本身），说明在根目录
                        path_parts = after_save0.split(os.sep)
                        if len(path_parts) == 1:  # 只有文件名，没有子目录
                            return True
            
            return False
        finally:
            cls._checking_stack.active = False
    
    @classmethod
    def add_ticks(cls, amount):
        """增加 tick 值（仅当调用来自项目代码时）"""
        if cls._instance is None:
            cls._instance = cls()
        
        # 检查调用栈，只有项目代码调用时才计数
        if cls._should_count_tick():
            cls._tick += amount
    
    @classmethod
    def reset(cls):
        """重置 tick 值为 0"""
        if cls._instance is None:
            cls._instance = cls()
        old_tick = cls._tick
        cls._tick = 0
        print(f"[DEBUG] TickSystem.reset(): {old_tick} -> {cls._tick}")
    
    @classmethod
    def tick_and_return(cls, value):
        """增加 1 tick 并返回值（用于下标访问）"""
        cls.add_ticks(1)
        return value

# 全局函数接口
def get_tick():
    """获取当前 tick 值"""
    return TickSystem.get_tick()

def _add_ticks(amount):
    """增加 tick 值"""
    TickSystem.add_ticks(amount)

def _tick_and_return(value):
    """增加 1 tick 并返回值"""
    return TickSystem.tick_and_return(value)

def reset_tick():
    """重置 tick 值"""
    TickSystem.reset()
