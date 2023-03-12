import ast
import builtins

TRUSTED_MODULES = ['math', 'numpy', 'pandas', 'datetime', 're', 'itertools', 'collections', 'random', 'string']  # add more as needed
DANGEROUS_FUNCS = ['eval', 'exec', 'compile', 'open', 'input', 'setattr', 'getattr', '__import__']

class DangerousCodeDetector(ast.NodeVisitor):
    def __init__(self):
        self.imports = []
        self.eval_exec = False
        self.is_dangerous = False
        self.reason = None

    def visit_Import(self, node):
        self.imports += [alias.name for alias in node.names]
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        self.imports.append(node.module)
        self.generic_visit(node)

    def visit_Call(self, node):
        func = self._get_func(node)
        if func in DANGEROUS_FUNCS:
            self.eval_exec = True
        self.generic_visit(node)

    def _get_func(self, node):
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            return node.func.attr
        else:
            return None

    def check(self, code):
        if len(code) > 4000:
            self.is_dangerous = True
            self.reason = "Code is too long"
            return False, self.reason

        tree = ast.parse(code)
        self.visit(tree)

        if self.eval_exec:
            self.is_dangerous = True
            self.reason = "Eval or exec statement detected"
            return False, self.reason

        for module in self.imports:
            if module in builtins.__dict__ or module in TRUSTED_MODULES:
                continue
            self.is_dangerous = True
            self.reason = "Import of potentially harmful module '{}' detected".format(module)
            return False, self.reason

        return True, None




d = DangerousCodeDetector()

string = """def add(a, b):
    return a + b

result = add(1, 2)
print(result)"""

print(d.check(string))
