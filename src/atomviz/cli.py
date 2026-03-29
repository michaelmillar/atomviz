from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from atomviz.examples import gaas_zincblende, nacl_rocksalt, silicon_diamond
from atomviz.render_html import render_interactive
from atomviz.render_svg import Style, render_unit_cell_svg
from atomviz.structure import UnitCell

app = typer.Typer(help="Deterministic crystal structure to SVG/HTML renderer")
console = Console(stderr=True)

EXAMPLES = {
    "silicon": silicon_diamond,
    "gaas": gaas_zincblende,
    "nacl": nacl_rocksalt,
}


def _load_file(path: Path) -> UnitCell:
    suffix = path.suffix.lower()
    if suffix == ".cif":
        from atomviz.parse_cif import parse_cif
        return parse_cif(path)
    if suffix in (".poscar", ".vasp") or path.name in ("POSCAR", "CONTCAR"):
        from atomviz.parse_poscar import parse_poscar
        return parse_poscar(path)
    raise typer.BadParameter(f"Unsupported file format: {suffix}")


def _parse_supercell(value: str) -> tuple[int, int, int]:
    parts = value.lower().split("x")
    if len(parts) == 1:
        n = int(parts[0])
        return (n, n, n)
    if len(parts) == 3:
        return (int(parts[0]), int(parts[1]), int(parts[2]))
    raise typer.BadParameter("Supercell must be N or NxNxN (e.g. 2 or 2x2x1)")


@app.command()
def render(
    source: str = typer.Argument(
        ...,
        help="Structure file (CIF/POSCAR) or built-in name (silicon, gaas, nacl)",
    ),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output path. Omit to write to stdout"),
    theta: float = typer.Option(0.5, help="Rotation angle theta (radians)"),
    phi: float = typer.Option(0.5, help="Rotation angle phi (radians)"),
    width: int = typer.Option(500, "-w", "--width", help="Image width in pixels"),
    height: int = typer.Option(500, "-h", "--height", help="Image height in pixels"),
    supercell: Optional[str] = typer.Option(None, "--supercell", "-s", help="Supercell expansion (e.g. 2 or 2x2x1)"),
    html: bool = typer.Option(False, "--html", help="Force interactive HTML output"),
    no_labels: bool = typer.Option(False, "--no-labels", help="Hide element labels"),
    no_bonds: bool = typer.Option(False, "--no-bonds", help="Hide bonds"),
    no_lattice: bool = typer.Option(False, "--no-lattice", help="Hide lattice wireframe"),
    no_depth: bool = typer.Option(False, "--no-depth", help="Disable depth-based opacity"),
) -> None:
    if source in EXAMPLES:
        cell = EXAMPLES[source]()
    else:
        path = Path(source)
        if not path.exists():
            console.print(f"[red]File not found: {source}[/red]")
            raise typer.Exit(1)
        cell = _load_file(path)

    if supercell:
        nx, ny, nz = _parse_supercell(supercell)
        cell = cell.supercell(nx, ny, nz)

    is_html = html or (output and output.suffix.lower() == ".html")

    style = Style(
        show_labels=not no_labels,
        show_bonds=not no_bonds,
        show_lattice=not no_lattice,
        depth_fade=not no_depth,
    )

    if is_html:
        content = render_interactive(cell, width=width, height=height)
    else:
        content = render_unit_cell_svg(
            cell, theta=theta, phi=phi,
            width=width, height=height, style=style,
        )

    if output:
        output.write_text(content)
        console.print(f"[green]Wrote {output}[/green]")
    else:
        sys.stdout.write(content)


@app.command()
def batch(
    input_dir: Path = typer.Argument(..., help="Directory containing structure files"),
    output_dir: Path = typer.Option("output", "--output", "-o", help="Output directory"),
    theta: float = typer.Option(0.5, help="Rotation angle theta"),
    phi: float = typer.Option(0.5, help="Rotation angle phi"),
    width: int = typer.Option(500, "-w", "--width"),
    height: int = typer.Option(500, "-h", "--height"),
    supercell: Optional[str] = typer.Option(None, "--supercell", "-s"),
    html: bool = typer.Option(False, "--html", help="Output HTML instead of SVG"),
) -> None:
    if not input_dir.is_dir():
        console.print(f"[red]Not a directory: {input_dir}[/red]")
        raise typer.Exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    extensions = {".cif", ".poscar", ".vasp"}
    files = sorted(
        f for f in input_dir.iterdir()
        if f.suffix.lower() in extensions or f.name in ("POSCAR", "CONTCAR")
    )

    if not files:
        console.print("[yellow]No structure files found[/yellow]")
        raise typer.Exit(0)

    for path in files:
        try:
            cell = _load_file(path)
            if supercell:
                nx, ny, nz = _parse_supercell(supercell)
                cell = cell.supercell(nx, ny, nz)

            suffix = ".html" if html else ".svg"
            out_path = output_dir / f"{path.stem}{suffix}"

            if html:
                content = render_interactive(cell, width=width, height=height)
            else:
                content = render_unit_cell_svg(
                    cell, theta=theta, phi=phi, width=width, height=height,
                )

            out_path.write_text(content)
            console.print(f"  [green]{path.name}[/green] -> {out_path}")
        except Exception as e:
            console.print(f"  [red]{path.name}[/red]: {e}")

    console.print(f"\n[bold]Rendered {len(files)} structures[/bold]")


@app.command(name="list")
def list_structures() -> None:
    for name, factory in EXAMPLES.items():
        cell = factory()
        console.print(f"  [bold]{name}[/bold]  {cell.title} ({len(cell.atoms)} atoms)")


if __name__ == "__main__":
    app()
