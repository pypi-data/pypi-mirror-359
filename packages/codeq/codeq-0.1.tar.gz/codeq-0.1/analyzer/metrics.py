from radon.complexity import cc_visit
from radon.metrics import mi_visit

def analyze_metrics(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()

    try:
        complexity_objs = cc_visit(code)
        avg_complexity = (
            sum(c.complexity for c in complexity_objs) / len(complexity_objs)
            if complexity_objs else 0
        )
    except:
        avg_complexity = 0

    try:
        mi_score = mi_visit(code, False)
    except:
        mi_score = 0

    return {
        "cyclomatic_avg": avg_complexity,
        "mi": mi_score
    }
