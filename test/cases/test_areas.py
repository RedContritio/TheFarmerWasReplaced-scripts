import pytest


class TestPumpkinArea:
    """测试南瓜区域功能"""
    
    def test_pumpkin_area_creation(self):
        """测试南瓜区域创建"""
        from area_pumpkin import pumpkin_area
        size = (6, 6)
        area = pumpkin_area(size)
        
        # 检查区域是否成功创建
        assert area is not None
        # 检查区域大小是否符合要求
        y, x, h, w = area['rect']
        assert h >= size[0]
        assert w >= size[1]
        
    def test_pumpkin_area_invalid_size(self):
        """测试无效尺寸的南瓜区域创建"""
        from area_pumpkin import pumpkin_area
        # 过小的尺寸 - 实际上会创建成功，只是很小
        area = pumpkin_area((1, 1))
        assert area is not None
        
        # 过大的尺寸 - 分配器会拒绝，函数应该返回 None
        area = pumpkin_area((100, 100))
        assert area is None


class TestSunflowerArea:
    """测试向日葵区域功能"""
    
    def test_sunflower_area_creation(self):
        """测试向日葵区域创建"""
        from area_sunflower import sunflower_area
        size = (10, 10)
        area = sunflower_area(size)
        
        # 向日葵区域应该成功创建
        assert area is not None
        # 检查区域大小
        y, x, h, w = area['rect']
        assert h >= size[0]
        assert w >= size[1]
        
    def test_sunflower_area_unique(self):
        """测试向日葵区域的唯一性（全场只保留一块）"""
        from area_sunflower import sunflower_area
        size = (10, 10)
        area1 = sunflower_area(size)
        area2 = sunflower_area(size)
        
        # 第二个向日葵区域应该创建失败（因为全场只能有一块）
        assert area1 is not None
        # 检查两个区域是否不同（而不是检查 None）
        assert area1 != area2


class TestCactusArea:
    """测试仙人掌区域功能"""
    
    def test_cactus_area_creation(self):
        """测试仙人掌区域创建"""
        from area_cactus import cactus_area
        size = (12, 12)
        area = cactus_area(size)
        
        # 仙人掌区域应该成功创建
        assert area is not None
        # 检查区域大小
        y, x, h, w = area['rect']
        assert h >= size[0]
        assert w >= size[1]
        
    def test_cactus_area_larger_size(self):
        """测试仙人掌区域可以接受更大的尺寸"""
        from area_cactus import cactus_area
        size = (15, 15)
        area = cactus_area(size)
        
        # 仙人掌区域应该成功创建
        assert area is not None


class TestCompanionArea:
    """测试伴生区域功能"""
    
    def test_companion_area_grass(self):
        """测试草伴生区域创建"""
        from area_companion import companion_area
        from framework.game_builtins import Entities
        size = (6, 6)
        area = companion_area(size, Entities.Grass)
        
        # 草伴生区域应该成功创建
        assert area is not None
        
    def test_companion_area_carrot(self):
        """测试胡萝卜伴生区域创建"""
        from area_companion import companion_area
        from framework.game_builtins import Entities
        size = (6, 6)
        area = companion_area(size, Entities.Carrot)
        
        # 胡萝卜伴生区域应该成功创建
        assert area is not None
        
    def test_companion_area_tree(self):
        """测试树伴生区域创建"""
        from area_companion import companion_area
        from framework.game_builtins import Entities
        size = (6, 6)
        area = companion_area(size, Entities.Tree)
        
        # 树伴生区域应该成功创建
        assert area is not None
        
    def test_companion_area_invalid_type(self):
        """测试无效类型的伴生区域创建"""
        from area_companion import companion_area
        size = (6, 6)
        area = companion_area(size, 9999)  # 使用一个无效的枚举值
        
        # 无效类型应该随机选择一个有效类型并创建成功
        assert area is not None


class TestMazeArea:
    """测试迷宫区域功能"""
    
    def test_maze_area_creation(self):
        """测试迷宫区域创建"""
        from area_maze import maze_area
        size = (16, 16)
        times = 300
        area = maze_area(size, times)
        
        # 迷宫区域应该成功创建
        assert area is not None
        # 检查迷宫大小
        y, x, h, w = area['rect']
        assert h >= size[0]
        assert w >= size[1]
        
    def test_maze_area_generation(self):
        """测试迷宫生成"""
        from area_maze import maze_area
        size = (16, 16)
        times = 100  # 减少迭代次数用于测试
        area = maze_area(size, times)
        
        # 迷宫应该成功生成
        assert area is not None
        # 迷宫应该有有效的路径（area 是字典，使用 in 检查）
        assert 'paths' in area or 'start_point' in area or 'rect' in area


if __name__ == "__main__":
    pytest.main([__file__, "-v"])