import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.json import JSON as RichJSON
from rich import box
from .analysis import PHPProjectAnalyzer, AnalysisResult
import asyncio
import json
from typing import Optional

app = typer.Typer()
console = Console()

def print_vertical_split_tables(result: AnalysisResult, analyzer: PHPProjectAnalyzer) -> None:
    """
    Print two beautified vertical tables for a single project: one for library indicators, one for web app indicators.
    """
    lib_inds = [ind for ind in analyzer.indicators if ind.is_library is True]
    app_inds = [ind for ind in analyzer.indicators if ind.is_library is False]
    def make_table(title, inds, color):
        table = Table(
            title=title,
            show_lines=True,
            box=box.SIMPLE_HEAVY,
            header_style=f"bold {color}",
            row_styles=["none", "dim"],
            title_style=f"bold {color}"
        )
        table.add_column("Indicator", style=f"bold {color}", no_wrap=True)
        table.add_column("Result", justify="center", style="bold")
        table.add_column("Description", style="dim")
        for ind in inds:
            found = any(f.name == ind.name for f in result.indicators_found)
            mark = "[green]✔[/green]" if found else "[red]✖[/red]"
            table.add_row(f"[bold]{ind.name}[/bold]", mark, ind.description)
        return table
    lib_table = make_table(f"Library Indicators for: {result.path}", lib_inds, "green")
    app_table = make_table(f"WebApp Indicators for: {result.path}", app_inds, "magenta")
    console.print(lib_table)
    console.print(app_table)
    # Add summary rows
    summary = Table(box=box.ROUNDED, show_lines=False, expand=False, pad_edge=True)
    summary.add_column("Summary", style="bold yellow", no_wrap=True)
    summary.add_column("Value", style="bold", justify="left")
    summary.add_row("[yellow]Library Score[/yellow]", f"[bold green]{result.library_score:.2f} ({result.normalized_library_score:.1%})[/bold green]")
    summary.add_row("[magenta]WebApp Score[/magenta]", f"[bold magenta]{result.webapp_score:.2f} ({result.normalized_webapp_score:.1%})[/bold magenta]")
    summary.add_row("[cyan]Type[/cyan]", f"[bold cyan]{result.project_type}[/bold cyan]")
    confidence, color = result.get_confidence_level()
    summary.add_row("[bold]Confidence[/bold]", f"[{color} bold]{confidence}[/{color} bold]")
    console.print(summary)
    console.print(Panel(Text("Legend: ✔ = indicator present, ✖ = not present", style="dim"), title="Legend", style="dim"))

@app.command()
def analyze(
    repo_path: str = typer.Argument(..., help="Path to the PHP project repository."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output format: table, json"),
    json_: bool = typer.Option(False, "--json", help="Output as JSON (same as -o json)"),
):
    """
    Analyze a single PHP project to determine if it is a library or a web application.
    Outputs split indicator tables and detection summary as a table or JSON.
    """
    async def _run() -> None:
        analyzer = PHPProjectAnalyzer(repo_path, verbose)
        result = await analyzer.analyze()
        use_json = output == "json" or json_
        if use_json:
            indicator_results = {}
            for ind in analyzer.indicators:
                found = any(f.name == ind.name for f in result.indicators_found)
                indicator_results[ind.name] = found
            output_obj = {
                "path": result.path,
                "project_type": result.project_type,
                "library_score": result.library_score,
                "webapp_score": result.webapp_score,
                "normalized_library_score": result.normalized_library_score,
                "normalized_webapp_score": result.normalized_webapp_score,
                "confidence": result.get_confidence_level()[0],
                "indicators": indicator_results,
            }
            console.print(RichJSON(json.dumps(output_obj, ensure_ascii=False, indent=2)))
        else:
            print_vertical_split_tables(result, analyzer)
    asyncio.run(_run())

if __name__ == "__main__":
    app() 