import ast
import sys
import importlib.util
from importlib.machinery import ModuleSpec
from importlib.abc import Loader, MetaPathFinder
from types import ModuleType
from pathlib import Path

_PROJECT_DIR = Path(__file__).parent.parent.parent


def _collect_project_modules():
    """收集项目模块名称（只包含Save0根目录下的.py文件）"""
    # 排除的文件
    EXCLUDED_FILES = {
        "game_builtins.py",  # Game API functions
    }
    # 排除的前缀
    EXCLUDED_PREFIXES = ("test_", "debug_")

    module_names = set()
    for file in _PROJECT_DIR.glob("*.py"):
        if not file.is_file():
            continue
        if file.name.startswith("."):
            continue
        if file.name in EXCLUDED_FILES:
            continue
        if any(file.name.startswith(prefix) for prefix in EXCLUDED_PREFIXES):
            continue
        module_names.add(file.stem)

    return module_names


_PROJECT_MODULE_NAMES = _collect_project_modules()


class TickInjectionTransformer(ast.NodeTransformer):
    """
    AST转换器：为pass语句和逻辑运算符注入tick计数

    注意：算术运算符的tick计数由Number类的运算符重载处理
    """

    def __init__(self):
        super().__init__()
        # 需要计数的逻辑运算符
        self.bool_ops = {ast.And, ast.Or}

    def _create_tick_call(self):
        """创建 _add_ticks(1) 调用节点"""
        return ast.Expr(
            value=ast.Call(
                func=ast.Name(id="_add_ticks", ctx=ast.Load()),
                args=[ast.Constant(value=1)],
                keywords=[],
            )
        )

    def visit_Pass(self, node):
        """为 pass 语句注入 tick 计数"""
        # 返回一个语句列表：先计数，再执行pass
        tick_call = self._create_tick_call()
        return [tick_call, node]

    def visit_BoolOp(self, node):
        """为逻辑运算符 (and/or) 注入 tick 计数"""
        # 先递归处理子节点
        self.generic_visit(node)

        # 检查是否是需要计数的逻辑运算符
        if type(node.op) in self.bool_ops:
            # 使用逗号表达式技巧：(_add_ticks(1), original_expr)[-1]
            tick_call = ast.Call(
                func=ast.Name(id="_add_ticks", ctx=ast.Load()),
                args=[ast.Constant(value=1)],
                keywords=[],
            )
            tuple_node = ast.Tuple(elts=[tick_call, node], ctx=ast.Load())
            result = ast.Subscript(
                value=tuple_node, slice=ast.Constant(value=-1), ctx=ast.Load()
            )
            return result

        return node

    def visit_UnaryOp(self, node):
        """处理一元运算符（不计数，只递归处理）"""
        # 一元负号 (USub) 和 not (Not) 不计数
        # 只递归处理子节点
        self.generic_visit(node)
        return node


class TickInjectionLoader(Loader):
    """自定义加载器：在导入时转换AST"""

    def __init__(self, original_loader):
        self.original_loader = original_loader

    def exec_module(self, module):
        try:
            source = self.original_loader.get_source(module.__name__)
        except (AttributeError, ImportError):
            return self.original_loader.exec_module(module)

        if source is None:
            return self.original_loader.exec_module(module)

        try:
            tree = ast.parse(source, module.__file__)
            transformer = TickInjectionTransformer()
            transformed_tree = transformer.visit(tree)
            ast.fix_missing_locations(transformed_tree)

            # 注入 _add_ticks 和 _tick_and_return 函数到模块命名空间
            if "_add_ticks" not in module.__dict__:
                try:
                    from framework.tick_system import _add_ticks, _tick_and_return

                    module.__dict__["_add_ticks"] = _add_ticks
                    module.__dict__["_tick_and_return"] = _tick_and_return
                except ImportError:
                    pass

            code = compile(transformed_tree, module.__file__, "exec")
            exec(code, module.__dict__)
        except Exception:
            import traceback

            traceback.print_exc()
            return self.original_loader.exec_module(module)

    def create_module(self, spec):
        return None


class TickInjectionFinder(MetaPathFinder):
    """自定义查找器：拦截模块导入"""

    def __init__(self, target_modules):
        self.target_modules = target_modules

    def find_spec(self, fullname, path, target=None):
        if not any(fullname.startswith(prefix) for prefix in self.target_modules):
            return None

        # 不转换自身和tick_system
        if fullname in {"tick_system", "tick_ast_transformer"}:
            return None

        # 查找原始spec - 只使用系统内置的finder，跳过所有自定义MetaPathFinder
        spec = None
        for finder in sys.meta_path:
            if finder is self:
                continue
            # 跳过其他自定义的MetaPathFinder（通过类名判断）
            finder_class_name = finder.__class__.__name__
            if finder_class_name in {"NumberWrappingFinder", "TickInjectionFinder"}:
                continue
            if hasattr(finder, "find_spec"):
                spec = finder.find_spec(fullname, path, target)
                if spec is not None:
                    break

        if spec is None or spec.loader is None:
            return None

        # 只转换Save0根目录下的文件，不转换test/子目录
        if spec.origin:
            module_path = Path(spec.origin)
            if module_path.parent == _PROJECT_DIR:
                print(
                    f"[DEBUG TICK TRANSFORMER] Transforming module: {fullname} at {spec.origin}"
                )
                spec.loader = TickInjectionLoader(spec.loader)
            else:
                print(
                    f"[DEBUG TICK TRANSFORMER] Skipping module: {fullname} at {spec.origin} (not in project root)"
                )

        return spec


def get_project_module_prefixes():
    """获取项目模块前缀列表"""
    return sorted(_PROJECT_MODULE_NAMES)


def install_tick_transformer(target_modules=None):
    """安装tick AST转换器"""
    if target_modules is None:
        target_modules = get_project_module_prefixes()

    finder = TickInjectionFinder(target_modules)
    sys.meta_path.insert(0, finder)

    return finder


def uninstall_tick_transformer(finder):
    """卸载tick AST转换器"""
    if finder in sys.meta_path:
        sys.meta_path.remove(finder)
