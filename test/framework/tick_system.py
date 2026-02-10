"""
Singleton tick system for game time tracking
"""
import inspect
import threading

class TickSystem:
    """单例 tick 系统，确保全局只有一个 tick 计数器"""
    _instance = None
    _tick = 0
    
    # 线程局部变量，用于防止在检查调用栈时触发 tick 计数
    _checking_stack = threading.local()
    
    # 模块白名单：只有这些模块的调用才会计数 tick
    # 包含 Save0 根目录下的所有项目代码模块
    _module_whitelist = {
        # 主程序
        'main',
        # 临时验证文件
        'f0', 'f1', 'f2', 'f3', 'f4',
        # 区域模块
        'area_cactus',
        'area_companion',
        'area_dinosaur',
        'area_intercrop',
        'area_maze',
        'area_pumpkin',
        'area_sunflower',
        # 工具模块
        'utils_area',
        'utils_dict',
        'utils_direction',
        'utils_drone',
        'utils_farming',
        'utils_list',
        'utils_math',
        'utils_maze',
        'utils_move',
        'utils_point',
        'utils_pytest',
        'utils_rect',
        'utils_rect_allocator',
        'utils_rect_ex',
        'utils_route',
        'utils_singleton',
        'utils_user',
    }
    
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
        只有当调用来自白名单模块时才返回 True
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
                # 获取模块名（从 frame 的 globals 中获取 __name__）
                module_name = frame_info.frame.f_globals.get('__name__', '')
                
                # 检查是否在白名单中
                if module_name in cls._module_whitelist:
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
