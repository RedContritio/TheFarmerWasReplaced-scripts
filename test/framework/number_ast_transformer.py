import ast
import sys
import importlib.util
from importlib.machinery import ModuleSpec
from importlib.abc import Loader, MetaPathFinder
from types import ModuleType
from pathlib import Path

_PROJECT_DIR = Path(__file__).parent.parent.parent

# 调试输出控制
_DEBUG_ENABLED = False


def _debug_print(msg):
    """调试输出函数，可通过 _DEBUG_ENABLED 控制是否输出"""
    if _DEBUG_ENABLED:
        print(msg)


def _collect_project_symbols():
    # Files whose functions should not be transformed
    EXCLUDED_FILES = {
        "game_builtins.py",  # Game API functions
        "conftest.py",  # Pytest configuration
        "run_tests.py",  # Test runner
    }
    # Also exclude all test files
    EXCLUDED_PREFIXES = ("test_", "debug_")

    function_names = set()
    module_names = set()
    for file in _PROJECT_DIR.glob("*.py"):
        if not file.is_file():
            continue
        if file.name.startswith("."):
            continue
        module_names.add(file.stem)

        # Skip collecting functions from excluded files
        if file.name in EXCLUDED_FILES:
            continue
        if any(file.name.startswith(prefix) for prefix in EXCLUDED_PREFIXES):
            continue

        try:
            source = file.read_text(encoding="utf-8")
            tree = ast.parse(source, str(file))
            for node in tree.body:
                if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                    function_names.add(node.name)
        except Exception:
            continue
    return function_names, module_names


_PROJECT_FUNCTION_NAMES, _PROJECT_MODULE_NAMES = _collect_project_symbols()


class SyntaxSugarTransformer(ast.NodeTransformer):
    """
    统一的AST转换器：同时处理数值包装和tick注入

    功能：
    1. 将数值字面量包装为 Number 类型
    2. 为 pass 语句注入 tick 计数
    3. 为二元算术运算符 (+, -, *, /, //, %, **) 注入 tick 计数
    4. 为逻辑运算符 (and/or) 注入 tick 计数
    5. 为索引操作 [] 注入 tick 计数
    6. 为打包操作（元组创建）注入 tick 计数
    7. 为解包操作注入 tick 计数
    8. 为项目函数调用注入 tick 计数

    注意：tick 计数统一由 AST 转换器处理，而不是由 Number 类的运算符重载处理
    """

    def __init__(self, function_names, module_names):
        super().__init__()
        self.function_names = function_names
        self.module_names = module_names
        self.bool_ops = {ast.And, ast.Or}
        # 需要注入 tick 的二元运算符
        self.bin_ops = {
            ast.Add,
            ast.Sub,
            ast.Mult,
            ast.Div,
            ast.FloorDiv,
            ast.Mod,
            ast.Pow,
        }
        # 用于跟踪当前是否在 return 语句中
        self.in_return = False

    def visit_Constant(self, node):
        """将数值常量包装为 Number 类型"""
        if isinstance(node.value, (int, float)):
            _debug_print(f"[DEBUG TRANSFORMER] Wrapping constant: {node.value}")
            return ast.Call(
                func=ast.Name(id="Number", ctx=ast.Load()), args=[node], keywords=[]
            )
        return node

    def visit_Num(self, node):
        """将数值字面量包装为 Number 类型（兼容旧版本Python）"""
        return ast.Call(
            func=ast.Name(id="Number", ctx=ast.Load()), args=[node], keywords=[]
        )

    def visit_Return(self, node):
        """处理 return 语句，标记进入 return 上下文"""
        old_in_return = self.in_return
        self.in_return = True
        node = self.generic_visit(node)
        self.in_return = old_in_return
        return node

    def visit_Call(self, node):
        """处理方法调用的语法糖 - 将所有 a.f(...) 转换为 f(a, ...)，并为项目函数注入 tick"""
        # 先检查是否需要转换方法调用（在递归之前）
        if isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
            value = node.func.value

            # 调试：显示value的类型和转换前的代码
            value_type = type(value).__name__
            try:
                import astor

                before_code = astor.to_source(node).strip()
                _debug_print(f"[DEBUG TRANSFORMER] Before: {before_code}")
            except:
                pass

            if isinstance(value, ast.Call) and isinstance(value.func, ast.Attribute):
                _debug_print(
                    f"[DEBUG TRANSFORMER] Chain detected: ?.{value.func.attr}().{func_name}(...)"
                )
            else:
                _debug_print(
                    f"[DEBUG TRANSFORMER] Converting method call: {value_type}.{func_name}(...) -> {func_name}({value_type}, ...)"
                )

            # 无条件转换为函数调用形式
            new_call = ast.Call(
                func=ast.Name(id=func_name, ctx=ast.Load()),
                args=[value] + node.args,
                keywords=node.keywords,
            )
            # 复制位置信息
            ast.copy_location(new_call, node)
            # 然后递归处理转换后的节点（这样会继续处理内层的链式调用）
            new_call = self.generic_visit(new_call)
            ast.fix_missing_locations(new_call)
            # 调试：显示转换后的代码
            try:
                import astor

                after_code = astor.to_source(new_call).strip()
                _debug_print(f"[DEBUG TRANSFORMER] After: {after_code}")
            except:
                pass

            # 为项目函数调用注入 tick
            if func_name in self.function_names:
                _debug_print(
                    f"[DEBUG TRANSFORMER] Injecting tick for function call: {func_name}"
                )
                tick_call = ast.Call(
                    func=ast.Name(id="_add_ticks", ctx=ast.Load()),
                    args=[ast.Constant(value=1)],
                    keywords=[],
                )
                tuple_node = ast.Tuple(elts=[tick_call, new_call], ctx=ast.Load())
                result = ast.Subscript(
                    value=tuple_node, slice=ast.Constant(value=-1), ctx=ast.Load()
                )
                return result

            return new_call

        # 如果不是方法调用，检查是否是项目函数调用
        node = self.generic_visit(node)

        # 为项目函数调用注入 tick
        if isinstance(node.func, ast.Name) and node.func.id in self.function_names:
            _debug_print(
                f"[DEBUG TRANSFORMER] Injecting tick for function call: {node.func.id}"
            )
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

    def visit_Pass(self, node):
        """为 pass 语句注入 tick 计数"""
        tick_call = ast.Expr(
            value=ast.Call(
                func=ast.Name(id="_add_ticks", ctx=ast.Load()),
                args=[ast.Constant(value=1)],
                keywords=[],
            )
        )
        return [tick_call, node]

    def visit_BinOp(self, node):
        """为二元算术运算符注入 tick 计数"""
        # 先递归处理子节点
        self.generic_visit(node)

        # 检查是否是需要计数的二元运算符
        if type(node.op) in self.bin_ops:
            _debug_print(
                f"[DEBUG TRANSFORMER] Injecting tick for BinOp: {type(node.op).__name__}"
            )
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

    def visit_BoolOp(self, node):
        """为逻辑运算符 (and/or) 注入 tick 计数"""
        # 先递归处理子节点
        self.generic_visit(node)

        # 检查是否是需要计数的逻辑运算符
        if type(node.op) in self.bool_ops:
            _debug_print(
                f"[DEBUG TRANSFORMER] Injecting tick for BoolOp: {type(node.op).__name__}"
            )
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

    def visit_Compare(self, node):
        """为比较操作注入 tick 计数"""
        # 先递归处理子节点
        self.generic_visit(node)

        _debug_print(f"[DEBUG TRANSFORMER] Injecting tick for Compare")
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

    def visit_Subscript(self, node):
        """为索引操作 [] 注入 tick 计数"""
        # 先递归处理子节点
        self.generic_visit(node)

        # 只在 Load 上下文中注入 tick（读取时），不在 Store 上下文中注入（赋值目标时）
        if not isinstance(node.ctx, ast.Load):
            return node

        _debug_print(f"[DEBUG TRANSFORMER] Injecting tick for Subscript")
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

    def visit_Tuple(self, node):
        """为打包操作（元组创建）注入 tick 计数"""
        # 先递归处理子节点
        self.generic_visit(node)

        # 只在 Load 上下文中计数（即创建元组时）
        # 不在 Store 上下文中计数（那是解包的目标）
        # 单元素元组不计数（通常是语法糖的一部分）
        # 在 return 语句中的元组不计数（那只是语法结构）
        if isinstance(node.ctx, ast.Load) and len(node.elts) > 1 and not self.in_return:
            # 检查父节点，避免对内部使用的元组计数
            # 这里我们通过检查是否所有元素都是简单值来判断
            # 如果元组包含 Call 节点且是 _add_ticks，则跳过（这是我们自己注入的）
            if any(
                isinstance(elt, ast.Call)
                and isinstance(elt.func, ast.Name)
                and elt.func.id == "_add_ticks"
                for elt in node.elts
            ):
                return node

            _debug_print(f"[DEBUG TRANSFORMER] Injecting tick for Tuple packing")
            # 使用逗号表达式技巧：(_add_ticks(1), original_expr)[-1]
            tick_call = ast.Call(
                func=ast.Name(id="_add_ticks", ctx=ast.Load()),
                args=[ast.Constant(value=1)],
                keywords=[],
            )
            wrapper_tuple = ast.Tuple(elts=[tick_call, node], ctx=ast.Load())
            result = ast.Subscript(
                value=wrapper_tuple, slice=ast.Constant(value=-1), ctx=ast.Load()
            )
            return result

        return node

    def visit_Assign(self, node):
        """为解包操作注入 tick 计数"""
        # 先递归处理子节点
        self.generic_visit(node)

        # 检查是否是解包赋值（左侧是元组或列表）
        for target in node.targets:
            if isinstance(target, (ast.Tuple, ast.List)) and len(target.elts) > 1:
                _debug_print(f"[DEBUG TRANSFORMER] Injecting tick for unpacking")
                # 在赋值语句前添加 tick 计数
                tick_call = ast.Expr(
                    value=ast.Call(
                        func=ast.Name(id="_add_ticks", ctx=ast.Load()),
                        args=[ast.Constant(value=1)],
                        keywords=[],
                    )
                )
                return [tick_call, node]

        return node


class NumberWrappingLoader(Loader):
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
            transformer = SyntaxSugarTransformer(
                _PROJECT_FUNCTION_NAMES, _PROJECT_MODULE_NAMES
            )
            transformed_tree = transformer.visit(tree)
            ast.fix_missing_locations(transformed_tree)

            # Inject Number class and _add_ticks into module namespace
            # Use lazy import to avoid circular dependency issues
            if "Number" not in module.__dict__:
                try:
                    from number_wrapper import Number

                    module.Number = Number
                except ImportError:
                    # If number_wrapper is not available, skip injection
                    pass

            if "_add_ticks" not in module.__dict__:
                try:
                    from framework.tick_system import _add_ticks

                    module.__dict__["_add_ticks"] = _add_ticks
                except ImportError:
                    # If tick_system is not available, skip injection
                    pass

            code = compile(transformed_tree, module.__file__, "exec")
            exec(code, module.__dict__)
        except Exception:
            import traceback

            traceback.print_exc()
            return self.original_loader.exec_module(module)

    def create_module(self, spec):
        return None


class NumberWrappingFinder(MetaPathFinder):
    def __init__(self, target_modules):
        self.target_modules = target_modules

    def find_spec(self, fullname, path, target=None):
        _debug_print(f"[DEBUG FINDER] find_spec called for: {fullname}")
        if not any(fullname.startswith(prefix) for prefix in self.target_modules):
            _debug_print(f"[DEBUG FINDER] Skipping {fullname}: not in target_modules")
            return None

        if fullname in {
            "number_wrapper",
            "number_ast_transformer",
            "framework.number_wrapper",
            "framework.number_ast_transformer",
            "framework.tick_system",
            "framework.game_builtins",
        }:
            _debug_print(f"[DEBUG FINDER] Skipping {fullname}: excluded module")
            return None

        # Find the spec first to check the file path
        spec = None
        for finder in sys.meta_path:
            if finder is self:
                continue
            if hasattr(finder, "find_spec"):
                spec = finder.find_spec(fullname, path, target)
                if spec is not None:
                    break

        if spec is None or spec.loader is None:
            _debug_print(f"[DEBUG FINDER] No spec found for {fullname}")
            return None

        # Check if the module file is in the project directory (Save0) or its subdirectories
        if spec.origin:
            module_path = Path(spec.origin)
            _debug_print(
                f"[DEBUG FINDER] Module path: {module_path}, parent: {module_path.parent}, _PROJECT_DIR: {_PROJECT_DIR}"
            )
            # Transform if the file is in _PROJECT_DIR or any of its subdirectories
            try:
                # Check if module_path is relative to _PROJECT_DIR
                module_path.relative_to(_PROJECT_DIR)
                _debug_print(
                    f"[DEBUG TRANSFORMER] Transforming module: {fullname} at {spec.origin}"
                )
                spec.loader = NumberWrappingLoader(spec.loader)
            except ValueError:
                # module_path is not relative to _PROJECT_DIR
                _debug_print(
                    f"[DEBUG TRANSFORMER] Skipping module: {fullname} at {spec.origin} (not in project directory)"
                )

        return spec


def get_project_module_prefixes():
    return sorted(_PROJECT_MODULE_NAMES)


def install_number_wrapper(target_modules=None):
    if target_modules is None:
        target_modules = get_project_module_prefixes()

    finder = NumberWrappingFinder(target_modules)
    sys.meta_path.insert(0, finder)

    return finder


def uninstall_number_wrapper(finder):
    if finder in sys.meta_path:
        sys.meta_path.remove(finder)
