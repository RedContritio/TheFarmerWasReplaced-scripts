import ast
import sys
import importlib.util
from importlib.machinery import ModuleSpec
from importlib.abc import Loader, MetaPathFinder
from types import ModuleType
from pathlib import Path


_PROJECT_DIR = Path(__file__).parent.parent


def _collect_project_symbols():
    # Files whose functions should not be transformed
    EXCLUDED_FILES = {
        'game_builtins.py',  # Game API functions
        'conftest.py',        # Pytest configuration
        'run_tests.py',       # Test runner
    }
    # Also exclude all test files
    EXCLUDED_PREFIXES = ('test_', 'debug_')
    
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
    def __init__(self, function_names, module_names):
        super().__init__()
        self.function_names = function_names
        self.module_names = module_names

    def visit_Constant(self, node):
        if isinstance(node.value, (int, float)):
            return ast.Call(
                func=ast.Name(id='Number', ctx=ast.Load()),
                args=[node],
                keywords=[]
            )
        return node

    def visit_Num(self, node):
        return ast.Call(
            func=ast.Name(id='Number', ctx=ast.Load()),
            args=[node],
            keywords=[]
        )


    def visit_Call(self, node):
        self.generic_visit(node)
        if isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
            if func_name in self.function_names:
                value = node.func.value
                if isinstance(value, ast.Name) and value.id in self.module_names:
                    return node
                return ast.Call(
                    func=ast.Name(id=func_name, ctx=ast.Load()),
                    args=[value] + node.args,
                    keywords=node.keywords
                )
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
            transformer = SyntaxSugarTransformer(_PROJECT_FUNCTION_NAMES, _PROJECT_MODULE_NAMES)
            transformed_tree = transformer.visit(tree)
            ast.fix_missing_locations(transformed_tree)

            # Inject Number class into module namespace
            # Use lazy import to avoid circular dependency issues
            if 'Number' not in module.__dict__:
                try:
                    from number_wrapper import Number
                    module.Number = Number
                except ImportError:
                    # If number_wrapper is not available, skip injection
                    pass

            code = compile(transformed_tree, module.__file__, 'exec')
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
        if not any(fullname.startswith(prefix) for prefix in self.target_modules):
            return None

        if fullname in {'number_wrapper', 'number_ast_transformer'}:
            return None
        
        # Find the spec first to check the file path
        spec = None
        for finder in sys.meta_path:
            if finder is self:
                continue
            if hasattr(finder, 'find_spec'):
                spec = finder.find_spec(fullname, path, target)
                if spec is not None:
                    break
        
        if spec is None or spec.loader is None:
            return None
        
        # Check if the module file is in the project directory (Save0)
        # Only transform files directly in Save0, not in subdirectories like test/
        if spec.origin:
            module_path = Path(spec.origin)
            # Only transform if the file is directly in _PROJECT_DIR (Save0)
            # and not in any subdirectory
            if module_path.parent == _PROJECT_DIR:
                print(f"[DEBUG TRANSFORMER] Transforming module: {fullname} at {spec.origin}")
                spec.loader = NumberWrappingLoader(spec.loader)
            else:
                print(f"[DEBUG TRANSFORMER] Skipping module: {fullname} at {spec.origin} (not in project root)")
        
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
