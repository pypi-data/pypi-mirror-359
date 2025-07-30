from rich.console import Console
from rich.table import Table
import json
import csv

console = Console()

def print_results(results):
    table = Table(title="Code Quality Metrics Summary", show_lines=True)

    table.add_column("File", overflow="fold", style="cyan bold")
    table.add_column("Cyclomatic Avg", justify="right", style="magenta")
    table.add_column("Maintainability", justify="right", style="green")
    table.add_column("No Docstrings", justify="right", style="yellow")
    table.add_column("Long Funcs", justify="right", style="yellow")
    table.add_column("Bad Var Names", justify="right", style="red")
    table.add_column("Unused Imports", justify="right", style="red")
    table.add_column("Unused Vars", justify="right", style="red")

    for r in results:
        table.add_row(
            r["file"],
            f"{r.get('cyclomatic_avg', 0):.2f}",
            f"{r.get('maintainability_index', 0):.2f}",
            str(r.get("no_docstring_count", 0)),
            str(r.get("long_function_count", 0)),
            str(r.get("bad_variable_names", 0)),
            str(r.get("unused_imports_count", 0)),
            str(r.get("unused_vars_count", 0)),
        )

    console.print(table)


def export_results(results, to_json=False, to_csv=False):
    if to_json:
        with open("report.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        console.print("[green]Exported to report.json[/green]")

    if to_csv:
        with open("report.csv", "w", newline="", encoding="utf-8") as f:
            fieldnames = list(results[0].keys()) if results else []
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        console.print("[green]Exported to report.csv[/green]")
