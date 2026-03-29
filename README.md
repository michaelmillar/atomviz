<p align="center">
  <img src="assets/atomviz.svg" width="80" height="80"/>
</p>
<h1 align="center">atomviz</h1>
<p align="center">Deterministic crystal-to-SVG/HTML renderer. No GPU, no desktop app, no WebGL.</p>
<p align="center">Parses CIF and POSCAR files and produces clean, semantic, CSS-stylable SVG for docs, papers, static sites, Jupyter exports, and CI pipelines.</p>

https://github.com/user-attachments/assets/2ae44597-bba9-4979-9d92-f83879126e4c

## What it does

```python
from atomviz.parse_cif import parse_cif
from atomviz.render_svg import render_unit_cell_svg

cell = parse_cif("structure.cif")
svg = render_unit_cell_svg(cell)
```

The SVG output has stable DOM structure with CSS classes and data attributes on every element, so you can style, annotate, and script it.

```xml
<circle class="atomviz-atom atom-Si" data-index="0" data-element="Si"
        cx="250.0" cy="180.3" r="12.0" fill="#F0C8A0" opacity="0.92"/>
```

Override defaults with external CSS, target atoms by element, or select by index for annotation.

## Install

```bash
pip install .
```

Zero compiled dependencies. Pure Python. Works anywhere Python runs.

## Quick start

### CLI

```bash
atomviz render structure.cif -o cell.svg

atomviz render structure.cif --supercell 2x2x2 -o supercell.svg

atomviz render silicon -o silicon.svg

atomviz render structure.cif > output.svg

atomviz batch structures/ -o rendered/
```

### Python

```python
from atomviz.parse_cif import parse_cif
from atomviz.parse_poscar import parse_poscar
from atomviz.render_svg import Style, render_unit_cell_svg
from atomviz.render_html import render_interactive

cell = parse_cif("quartz.cif")

svg = render_unit_cell_svg(cell)

supercell = cell.supercell(2, 2, 1)
svg = render_unit_cell_svg(supercell)

style = Style(show_labels=False, depth_fade=True, background="#1a1a2e")
svg = render_unit_cell_svg(cell, style=style)

html = render_interactive(cell)
```

## Supported formats

| Format | Extensions | Notes |
|--------|-----------|-------|
| CIF | `.cif` | Fractional coordinates, cell parameters, uncertainty notation |
| POSCAR/CONTCAR | `.poscar`, `.vasp`, `POSCAR`, `CONTCAR` | VASP 5+ with element line, scale factors, selective dynamics |

## Features

**Semantic SVG** with CSS classes per element (`atom-Si`, `bond-Ga-As`), data attributes (`data-element`, `data-index`), and an embedded `<style>` block with overridable defaults

**Depth cueing** modulates opacity by z-depth for 3D perception without WebGL

**Covalent-radii bond detection** uses sum of covalent radii plus tolerance instead of a naive distance cutoff

**Supercell generation** repeats the unit cell NxMxP along each lattice direction

**Batch rendering** processes a directory of structure files in one command

**Deterministic output** guarantees the same input produces byte-identical SVG every time

**Style control** via the `Style` dataclass lets you toggle labels, bonds, lattice wireframe, depth fade, colours, and fonts

## Built-in examples

Three structures are included for quick testing.

```bash
atomviz render silicon -o silicon.svg
atomviz render gaas -o gaas.svg
atomviz render nacl -o nacl.svg
```

## Status

51 tests passing.

Not yet implemented: XYZ format, symmetry expansion from space groups, polyhedra, Miller plane overlays, perspective projection.
