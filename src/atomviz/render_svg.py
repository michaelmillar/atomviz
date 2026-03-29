from __future__ import annotations

import math
from dataclasses import dataclass

from atomviz.elements import get_covalent_radius
from atomviz.projection import orthographic_project
from atomviz.structure import UnitCell


@dataclass
class Style:
    background: str = "white"
    lattice_stroke: str = "#999"
    bond_stroke: str = "#666"
    atom_stroke: str = "#333"
    label_fill: str = "#555"
    title_fill: str = "#333"
    font_family: str = "sans-serif"
    show_labels: bool = True
    show_title: bool = True
    show_bonds: bool = True
    show_lattice: bool = True
    depth_fade: bool = True
    min_opacity: float = 0.4


def _lattice_corners(lattice: list[tuple[float, float, float]]) -> list[tuple[float, float, float]]:
    a, b, c = lattice
    return [
        (0.0, 0.0, 0.0),
        a,
        b,
        c,
        (a[0] + b[0], a[1] + b[1], a[2] + b[2]),
        (a[0] + c[0], a[1] + c[1], a[2] + c[2]),
        (b[0] + c[0], b[1] + c[1], b[2] + c[2]),
        (a[0] + b[0] + c[0], a[1] + b[1] + c[1], a[2] + b[2] + c[2]),
    ]


_LATTICE_EDGES = [
    (0, 1), (0, 2), (0, 3),
    (1, 4), (1, 5),
    (2, 4), (2, 6),
    (3, 5), (3, 6),
    (4, 7), (5, 7), (6, 7),
]


def _distance(p1: tuple[float, float, float], p2: tuple[float, float, float]) -> float:
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(p1, p2)))


def _find_bonds(
    positions: list[tuple[float, float, float]],
    elements: list[str],
    tolerance: float = 0.45,
) -> list[tuple[int, int]]:
    bonds = []
    n = len(positions)
    for i in range(n):
        ri = get_covalent_radius(elements[i])
        for j in range(i + 1, n):
            rj = get_covalent_radius(elements[j])
            d = _distance(positions[i], positions[j])
            if 0.5 < d < ri + rj + tolerance:
                bonds.append((i, j))
    return bonds


def _to_cartesian(
    frac: tuple[float, float, float],
    lattice: list[tuple[float, float, float]],
) -> tuple[float, float, float]:
    a, b, c = lattice
    return (
        frac[0] * a[0] + frac[1] * b[0] + frac[2] * c[0],
        frac[0] * a[1] + frac[1] * b[1] + frac[2] * c[1],
        frac[0] * a[2] + frac[1] * b[2] + frac[2] * c[2],
    )


def _depth_opacity(depth: float, min_depth: float, max_depth: float, min_opacity: float) -> float:
    span = max_depth - min_depth
    if span < 1e-6:
        return 1.0
    t = (depth - min_depth) / span
    return min_opacity + (1.0 - min_opacity) * (1.0 - t)


def _svg_style_block(style: Style) -> str:
    return f"""<style>
.atomviz-bg {{ fill: {style.background}; }}
.atomviz-title {{ font-family: {style.font_family}; font-size: 14px; fill: {style.title_fill}; }}
.atomviz-edge {{ stroke: {style.lattice_stroke}; stroke-width: 1; stroke-dasharray: 4 3; fill: none; }}
.atomviz-bond {{ stroke: {style.bond_stroke}; stroke-width: 2; stroke-linecap: round; }}
.atomviz-atom {{ stroke: {style.atom_stroke}; stroke-width: 0.5; }}
.atomviz-label {{ font-family: {style.font_family}; font-size: 10px; fill: {style.label_fill}; }}
</style>"""


def render_unit_cell_svg(
    cell: UnitCell,
    theta: float = 0.5,
    phi: float = 0.5,
    width: int = 500,
    height: int = 500,
    scale: float | None = None,
    atom_scale: float = 0.3,
    style: Style | None = None,
    bond_cutoff: float | None = None,
) -> str:
    if style is None:
        style = Style()

    cart_positions = [
        _to_cartesian(atom.position, cell.lattice_vectors) for atom in cell.atoms
    ]
    elements = [a.element for a in cell.atoms]

    corners = _lattice_corners(cell.lattice_vectors)

    all_points = cart_positions + corners
    projected = orthographic_project(all_points, theta, phi)

    n_atoms = len(cart_positions)
    atom_projected = {}
    corner_projected = {}

    for p in projected:
        if p.index < n_atoms:
            atom_projected[p.index] = p
        else:
            corner_projected[p.index - n_atoms] = p

    all_x = [p.x for p in projected]
    all_y = [p.y for p in projected]

    if not all_x:
        return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"></svg>'

    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)

    span_x = max_x - min_x if max_x > min_x else 1.0
    span_y = max_y - min_y if max_y > min_y else 1.0

    margin = 60
    usable_w = width - 2 * margin
    usable_h = height - 2 * margin

    if scale is None:
        scale = min(usable_w / span_x, usable_h / span_y)

    cx = width / 2
    cy = height / 2
    mid_x = (min_x + max_x) / 2
    mid_y = (min_y + max_y) / 2

    def screen(px: float, py: float) -> tuple[float, float]:
        return (cx + (px - mid_x) * scale, cy + (py - mid_y) * scale)

    atom_depths = [atom_projected[i].depth for i in range(n_atoms)] if n_atoms else []
    min_depth = min(atom_depths) if atom_depths else 0.0
    max_depth = max(atom_depths) if atom_depths else 0.0

    if style.show_bonds:
        if bond_cutoff is not None:
            bonds = _find_bonds_legacy(cart_positions, bond_cutoff)
        else:
            bonds = _find_bonds(cart_positions, elements)
    else:
        bonds = []

    bond_projected = []
    for i, j in bonds:
        p1 = atom_projected[i]
        p2 = atom_projected[j]
        avg_depth = (p1.depth + p2.depth) / 2
        bond_projected.append((i, j, avg_depth))
    bond_projected.sort(key=lambda b: b[2])

    lines = []

    lines.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" '
        f'class="atomviz" data-structure="{cell.title}">'
    )

    lines.append(_svg_style_block(style))

    lines.append(f'<rect class="atomviz-bg" width="{width}" height="{height}"/>')

    if style.show_title:
        lines.append(
            f'<text class="atomviz-title" x="{width / 2}" y="24" '
            f'text-anchor="middle">{cell.title}</text>'
        )

    if style.show_lattice:
        lines.append('<g class="atomviz-lattice">')
        for idx, (i, j) in enumerate(_LATTICE_EDGES):
            p1 = corner_projected[i]
            p2 = corner_projected[j]
            s1 = screen(p1.x, p1.y)
            s2 = screen(p2.x, p2.y)
            lines.append(
                f'  <line class="atomviz-edge" data-edge="{idx}" '
                f'x1="{s1[0]:.1f}" y1="{s1[1]:.1f}" '
                f'x2="{s2[0]:.1f}" y2="{s2[1]:.1f}"/>'
            )
        lines.append('</g>')

    draw_order: list[tuple[float, str]] = []

    for i, j, depth in bond_projected:
        p1 = atom_projected[i]
        p2 = atom_projected[j]
        s1 = screen(p1.x, p1.y)
        s2 = screen(p2.x, p2.y)
        opacity = _depth_opacity(depth, min_depth, max_depth, style.min_opacity) if style.depth_fade else 1.0
        e1 = cell.atoms[i].element
        e2 = cell.atoms[j].element
        draw_order.append((
            depth,
            f'<line class="atomviz-bond bond-{e1}-{e2}" '
            f'data-from="{i}" data-to="{j}" '
            f'x1="{s1[0]:.1f}" y1="{s1[1]:.1f}" '
            f'x2="{s2[0]:.1f}" y2="{s2[1]:.1f}" '
            f'opacity="{opacity:.2f}"/>'
        ))

    for p in projected:
        if p.index >= n_atoms:
            continue
        atom = cell.atoms[p.index]
        sx, sy = screen(p.x, p.y)
        r = atom.radius * atom_scale * scale * 0.15
        r = max(r, 4)
        r = min(r, 25)
        opacity = _depth_opacity(p.depth, min_depth, max_depth, style.min_opacity) if style.depth_fade else 1.0

        atom_svg = (
            f'<circle class="atomviz-atom atom-{atom.element}" '
            f'data-index="{p.index}" data-element="{atom.element}" '
            f'cx="{sx:.1f}" cy="{sy:.1f}" r="{r:.1f}" '
            f'fill="{atom.colour}" opacity="{opacity:.2f}"/>'
        )
        draw_order.append((p.depth, atom_svg))

        if style.show_labels:
            label_svg = (
                f'<text class="atomviz-label label-{atom.element}" '
                f'data-index="{p.index}" '
                f'x="{sx:.1f}" y="{sy + r + 12:.1f}" '
                f'text-anchor="middle" opacity="{opacity:.2f}">{atom.element}</text>'
            )
            draw_order.append((p.depth + 0.001, label_svg))

    draw_order.sort(key=lambda item: item[0])
    for _, svg_elem in draw_order:
        lines.append(svg_elem)

    lines.append("</svg>")
    return "\n".join(lines)


def _find_bonds_legacy(
    positions: list[tuple[float, float, float]],
    cutoff: float = 3.0,
) -> list[tuple[int, int]]:
    bonds = []
    n = len(positions)
    for i in range(n):
        for j in range(i + 1, n):
            d = _distance(positions[i], positions[j])
            if 0.5 < d < cutoff:
                bonds.append((i, j))
    return bonds
