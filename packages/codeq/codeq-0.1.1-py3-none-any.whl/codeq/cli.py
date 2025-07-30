import click
from pathlib import Path
import ast
from analyzer.metrics import analyze_metrics
from analyzer.smells import analyze_smells, UnusedCodeAnalyzer
from analyzer.formatter import print_results, export_results
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

console = Console()

def gather_detailed_smells(code):
    tree = ast.parse(code)
    analyzer = UnusedCodeAnalyzer()
    analyzer.visit(tree)

    missing_docstrings = []
    long_functions = []
    bad_variable_names = []

    for node in ast.walk(tree):
        # Check for missing docstrings on functions/classes
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if ast.get_docstring(node) is None:
                missing_docstrings.append(node.name)

        # Long functions (threshold = 20 statements)
        if isinstance(node, ast.FunctionDef):
            if len(node.body) > 20:
                long_functions.append(node.name)

        # Bad variable names (single letter except i,j,k,_)
        if isinstance(node, ast.Name):
            if (
                len(node.id) == 1
                and node.id not in ("i", "j", "k", "_")
                and not node.id.isupper()  # ignore constants
            ):
                bad_variable_names.append(node.id)

    # Deduplicate bad variable names
    bad_variable_names = list(set(bad_variable_names))

    return {
        "unused_imports": list(analyzer.unused_imports),
        "unused_vars": list(analyzer.unused_vars),
        "missing_docstrings": missing_docstrings,
        "long_functions": long_functions,
        "bad_variable_names": bad_variable_names,
    }


def print_detailed_report(file, code, metrics, smells):
    details = gather_detailed_smells(code)

    console.print(Panel.fit(f"[bold underline]Detailed Report for:[/bold underline] {file}", style="cyan"))

    # Summary Metrics Table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Metric")
    table.add_column("Value", justify="right")

    table.add_row("Cyclomatic Complexity Avg", f"{metrics.get('cyclomatic_avg', 0):.2f}")
    table.add_row("Maintainability Index", f"{metrics.get('maintainability_index', 0):.2f}")
    table.add_row("No Docstrings Count", str(smells.get("no_docstring_count", 0)))
    table.add_row("Long Functions Count", str(smells.get("long_function_count", 0)))
    table.add_row("Bad Variable Names Count", str(smells.get("bad_variable_names", 0)))
    table.add_row("Unused Imports Count", str(len(details["unused_imports"])))
    table.add_row("Unused Variables Count", str(len(details["unused_vars"])))

    console.print(table)

    # Detailed lists with colors
    def print_list(title, items, style="white"):
        console.print(f"\n[bold]{title}[/bold]:")
        if items:
            for item in items:
                console.print(f"  • [bold {style}]{item}[/bold {style}]")
        else:
            console.print("  None")

    print_list("Unused Imports", details["unused_imports"], style="red")
    print_list("Unused Variables", details["unused_vars"], style="red")
    print_list("Functions/Classes Missing Docstrings", details["missing_docstrings"], style="yellow")
    print_list("Long Functions (>20 lines)", details["long_functions"], style="yellow")
    print_list("Bad Variable Names (single-letter except i,j,k,_)", details["bad_variable_names"], style="yellow")


@click.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--json", "json_out", is_flag=True, help="Export report as JSON")
@click.option("--csv", "csv_out", is_flag=True, help="Export report as CSV")
@click.option(
    "--details", is_flag=True, help="Show detailed info for one file (only works with a single file path)"
)
def analyze(path, json_out, csv_out, details):
    """Analyze Python code quality metrics in PATH recursively."""
    path = Path(path)

    if path.is_file():
        py_files = [path]
    else:
        py_files = list(path.rglob("*.py"))

    if details and len(py_files) != 1:
        console.print("[red]Error: --details flag works only with a single file path[/red]")
        return

    results = []
    for file in py_files:
        metrics = analyze_metrics(file)
        smells = analyze_smells(file)
        
        from analyzer.smells import UnusedCodeAnalyzer
        import ast

        code = file.read_text(encoding="utf-8")
        tree = ast.parse(code)
        analyzer = UnusedCodeAnalyzer()
        analyzer.visit(tree)

        results.append({
            "file": str(file),
            **metrics,
            **smells,
            "unused_imports_count": len(analyzer.unused_imports),
            "unused_vars_count": len(analyzer.unused_vars),
        })

    if details:
        file = py_files[0]
        code = file.read_text(encoding="utf-8")
        metrics = results[0]
        smells = results[0]

        print_detailed_report(file, code, metrics, smells)

    else:
        # Print summary table for all files
        print_results(results)
        export_results(results, json_out, csv_out)


if __name__ == "__main__":
    analyze()
