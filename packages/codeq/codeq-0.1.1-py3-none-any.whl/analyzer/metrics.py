from radon.complexity import cc_visit
from radon.metrics import mi_visit

def analyze_metrics(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    # Cyclomatic Complexity average
    blocks = cc_visit(code)
    if blocks:
        avg_cyclomatic = sum(b.complexity for b in blocks) / len(blocks)
    else:
        avg_cyclomatic = 0.0

    # Maintainability Index
    try:
        maintainability_index = mi_visit(code, True)  # True = return float instead of grade
    except Exception as e:
        print(f"Failed to get MI for {file_path}: {e}")
        maintainability_index = 0.0

    return {
        "cyclomatic_avg": avg_cyclomatic,
        "maintainability_index": maintainability_index,
    }
