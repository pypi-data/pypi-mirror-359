import tempfile
import ast
from analyzer.smells import analyze_unused_code

def test_unused_code_detection():
    code = '''
import os
import sys

x = 10
y = 20

print(x)
'''

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()
        filename = f.name

    with open(filename, "r") as f:
        tree = ast.parse(f.read())

    result = analyze_unused_code(tree)
    assert "sys" in result["unused_imports"]
    assert "os" in result["unused_imports"]
    assert "y" in result["unused_vars"]
    assert "x" not in result["unused_vars"]
