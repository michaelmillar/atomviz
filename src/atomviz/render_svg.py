from __future__ import annotations

import math

from atomviz.projection import orthographic_project
from atomviz.structure import UnitCell


def _lattice_corners(lattice: list[tuple[float, float, float]]) -> list[tuple[float, float, float]]:
    a, b, c = lattice
    origin = (0.0, 0.0, 0.0)
    return [
        origin,
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


def render_unit_cell_svg(
    cell: UnitCell,
    theta: float = 0.5,
    phi: float = 0.5,
    width: int = 500,
    height: int = 500,
    bond_cutoff: float = 3.0,
    scale: float | None = None,
    atom_scale: float = 0.3,
) -> str:
    cart_positions = [
        _to_cartesian(atom.position, cell.lattice_vectors) for atom in cell.atoms
    ]

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

    bonds = _find_bonds(cart_positions, [a.element for a in cell.atoms], bond_cutoff)

    bond_projected = []
    for i, j in bonds:
        p1 = atom_projected[i]
        p2 = atom_projected[j]
        avg_depth = (p1.depth + p2.depth) / 2
        bond_projected.append((i, j, avg_depth))
    bond_projected.sort(key=lambda b: b[2])

    elements = []

    elements.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
    )
    elements.append(f'<rect width="{width}" height="{height}" fill="white"/>')

    elements.append(f'<text x="{width / 2}" y="20" text-anchor="middle" '
                    f'font-family="sans-serif" font-size="14" fill="#333">'
                    f'{cell.title}</text>')

    for i, j in _LATTICE_EDGES:
        p1 = corner_projected[i]
        p2 = corner_projected[j]
        s1 = screen(p1.x, p1.y)
        s2 = screen(p2.x, p2.y)
        elements.append(
            f'<line x1="{s1[0]:.1f}" y1="{s1[1]:.1f}" '
            f'x2="{s2[0]:.1f}" y2="{s2[1]:.1f}" '
            f'stroke="#999" stroke-width="1" stroke-dasharray="4,3"/>'
        )

    draw_order: list[tuple[float, str]] = []

    for i, j, depth in bond_projected:
        p1 = atom_projected[i]
        p2 = atom_projected[j]
        s1 = screen(p1.x, p1.y)
        s2 = screen(p2.x, p2.y)
        draw_order.append((
            depth,
            f'<line x1="{s1[0]:.1f}" y1="{s1[1]:.1f}" '
            f'x2="{s2[0]:.1f}" y2="{s2[1]:.1f}" '
            f'stroke="#666" stroke-width="2" stroke-linecap="round"/>'
        ))

    for p in projected:
        if p.index >= n_atoms:
            continue
        atom = cell.atoms[p.index]
        sx, sy = screen(p.x, p.y)
        r = atom.radius * atom_scale * scale * 0.15
        r = max(r, 4)
        r = min(r, 25)

        draw_order.append((
            p.depth,
            f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{r:.1f}" '
            f'fill="{atom.colour}" stroke="#333" stroke-width="0.5"/>'
        ))
        draw_order.append((
            p.depth + 0.001,
            f'<text x="{sx:.1f}" y="{sy + r + 12:.1f}" '
            f'text-anchor="middle" font-family="sans-serif" font-size="10" '
            f'fill="#555">{atom.element}</text>'
        ))

    draw_order.sort(key=lambda item: item[0])
    for _, svg_elem in draw_order:
        elements.append(svg_elem)

    elements.append("</svg>")
    return "\n".join(elements)
