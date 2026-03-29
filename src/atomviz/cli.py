from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from atomviz.examples import gaas_zincblende, nacl_rocksalt, silicon_diamond
from atomviz.render_html import render_interactive
from atomviz.render_svg import render_unit_cell_svg

app = typer.Typer(help="Crystal structure visualisation tool")
console = Console()

STRUCTURES = {
    "silicon": silicon_diamond,
    "gaas": gaas_zincblende,
    "nacl": nacl_rocksalt,
}


@app.command()
def render(
    structure: str = typer.Option("silicon", help="Structure name (silicon, gaas, nacl)"),
    output: Path = typer.Option("cell.svg", help="Output file path (.svg or .html)"),
    theta: float = typer.Option(0.5, help="Rotation angle theta (radians)"),
    phi: float = typer.Option(0.5, help="Rotation angle phi (radians)"),
    width: int = typer.Option(500, help="Image width in pixels"),
    height: int = typer.Option(500, help="Image height in pixels"),
    interactive: Optional[bool] = typer.Option(None, help="Force interactive HTML output"),
) -> None:
    if structure not in STRUCTURES:
        console.print(f"[red]Unknown structure '{structure}'[/red]")
        console.print(f"Available structures: {', '.join(STRUCTURES.keys())}")
        raise typer.Exit(1)

    cell = STRUCTURES[structure]()
    is_html = interactive or output.suffix.lower() == ".html"

    if is_html:
        content = render_interactive(cell, width=width, height=height)
    else:
        content = render_unit_cell_svg(cell, theta=theta, phi=phi, width=width, height=height)

    output.write_text(content)
    console.print(f"[green]Wrote {output}[/green]")


@app.command()
def list_structures() -> None:
    for name, factory in STRUCTURES.items():
        cell = factory()
        console.print(f"  [bold]{name}[/bold]  {cell.title} ({len(cell.atoms)} atoms)")


if __name__ == "__main__":
    app()
