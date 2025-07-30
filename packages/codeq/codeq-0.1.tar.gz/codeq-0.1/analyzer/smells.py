import ast

class UnusedCodeAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.imports = set()
        self.used_names = set()
        self.assigned_vars = set()
        self.unused_imports = set()
        self.unused_vars = set()

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.add(alias.asname or alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.imports.add(alias.asname or alias.name)
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.used_names.add(node.id)
        self.generic_visit(node)

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.assigned_vars.add(target.id)
        self.generic_visit(node)

def analyze_unused_code(tree):
    analyzer = UnusedCodeAnalyzer()
    analyzer.visit(tree)
    analyzer.unused_imports = analyzer.imports - analyzer.used_names
    analyzer.unused_vars = analyzer.assigned_vars - analyzer.used_names
    return {
        "unused_imports": list(analyzer.unused_imports),
        "unused_vars": list(analyzer.unused_vars),
    }

def analyze_smells(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        code = f.read()

    smells = {
        "no_docstring_count": 0,
        "long_function_count": 0,
        "bad_variable_names": 0,
    }

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return smells  # Return zeros if file has syntax errors

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if ast.get_docstring(node) is None:
                smells["no_docstring_count"] += 1

        if isinstance(node, ast.FunctionDef):
            if len(node.body) > 20:
                smells["long_function_count"] += 1

        if isinstance(node, ast.Name):
            if len(node.id) == 1 and node.id not in ('i', 'j', 'k', '_'):
                smells["bad_variable_names"] += 1

    # Add unused imports and vars from the unused code analyzer
    unused = analyze_unused_code(tree)
    smells["unused_imports_count"] = len(unused["unused_imports"])
    smells["unused_vars_count"] = len(unused["unused_vars"])

    return smells
