<p align="center">
  <img src="assets/atomviz.svg" width="80" height="80"/>
</p>
<h1 align="center">atomviz</h1>
<p align="center">Crystal structure visualisation in SVG and HTML. No GPU, no desktop app, no fuss.</p>

## Quickstart

### CLI

```bash
pip install .
atomviz render --structure silicon --output cell.svg
```

### Python

```python
from atomviz.examples import silicon_diamond
from atomviz.render_svg import render_unit_cell_svg

cell = silicon_diamond()
svg = render_unit_cell_svg(cell)

with open("silicon.svg", "w") as f:
    f.write(svg)
```

## Gallery

*Screenshots coming soon.*

## Supported Elements

H, C, N, O, Si, Fe, Ti, Al, Ga, As, Cd, Te, Zn, S, Cu, In, Se, Pb, I, Br, Sn, Ge, B, Na, K, Ca, Mg, Li, F, Cl, P

Each element has a default colour and atomic radius for visualisation.

## Examples

Three built-in crystal structures are provided for quick demos.

- **Silicon diamond** (8 atoms in a cubic cell)
- **GaAs zincblende** (8 atoms)
- **NaCl rocksalt** (8 atoms)

```python
from atomviz.examples import silicon_diamond, gaas_zincblende, nacl_rocksalt
from atomviz.render_html import render_interactive

html = render_interactive(silicon_diamond())
with open("silicon_interactive.html", "w") as f:
    f.write(html)
```
