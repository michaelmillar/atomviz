from __future__ import annotations

from pathlib import Path

from atomviz.elements import get_colour, get_radius
from atomviz.structure import Atom, UnitCell


def parse_poscar(source: str | Path) -> UnitCell:
    if isinstance(source, Path):
        text = source.read_text()
        title = source.stem
    else:
        text = source
        title = "POSCAR Structure"

    lines = [l.strip() for l in text.splitlines() if l.strip()]

    if len(lines) < 8:
        raise ValueError("POSCAR file too short")

    comment = lines[0]
    if comment and not comment[0].isdigit():
        title = comment

    scale = float(lines[1])

    lattice = []
    for i in range(2, 5):
        parts = lines[i].split()
        vec = (float(parts[0]) * scale, float(parts[1]) * scale, float(parts[2]) * scale)
        lattice.append(vec)

    line5_parts = lines[5].split()
    has_element_line = not line5_parts[0].isdigit()

    if has_element_line:
        element_symbols = line5_parts
        count_parts = lines[6].split()
        counts = [int(x) for x in count_parts]
        coord_start = 7
    else:
        counts = [int(x) for x in line5_parts]
        element_symbols = [f"X{i}" for i in range(len(counts))]
        coord_start = 6

    if coord_start < len(lines) and lines[coord_start][0].lower() in ("s", "S"):
        coord_start += 1

    is_cartesian = False
    if coord_start < len(lines):
        coord_type = lines[coord_start][0].lower()
        is_cartesian = coord_type in ("c", "k")
        coord_start += 1

    atoms: list[Atom] = []
    row = coord_start
    for element, count in zip(element_symbols, counts):
        for _ in range(count):
            if row >= len(lines):
                break
            parts = lines[row].split()
            x, y, z = float(parts[0]), float(parts[1]), float(parts[2])

            if is_cartesian:
                inv = _invert_lattice(lattice)
                fx = inv[0][0] * x + inv[0][1] * y + inv[0][2] * z
                fy = inv[1][0] * x + inv[1][1] * y + inv[1][2] * z
                fz = inv[2][0] * x + inv[2][1] * y + inv[2][2] * z
            else:
                fx, fy, fz = x, y, z

            atoms.append(Atom(
                element=element,
                position=(fx, fy, fz),
                radius=get_radius(element),
                colour=get_colour(element),
            ))
            row += 1

    return UnitCell(atoms=atoms, lattice_vectors=lattice, title=title)


def _invert_lattice(lattice: list[tuple[float, float, float]]) -> list[list[float]]:
    a, b, c = lattice
    m = [list(a), list(b), list(c)]

    det = (
        m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
        - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
        + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
    )

    if abs(det) < 1e-12:
        raise ValueError("Singular lattice matrix")

    inv_det = 1.0 / det
    return [
        [
            (m[1][1] * m[2][2] - m[1][2] * m[2][1]) * inv_det,
            (m[0][2] * m[2][1] - m[0][1] * m[2][2]) * inv_det,
            (m[0][1] * m[1][2] - m[0][2] * m[1][1]) * inv_det,
        ],
        [
            (m[1][2] * m[2][0] - m[1][0] * m[2][2]) * inv_det,
            (m[0][0] * m[2][2] - m[0][2] * m[2][0]) * inv_det,
            (m[0][2] * m[1][0] - m[0][0] * m[1][2]) * inv_det,
        ],
        [
            (m[1][0] * m[2][1] - m[1][1] * m[2][0]) * inv_det,
            (m[0][1] * m[2][0] - m[0][0] * m[2][1]) * inv_det,
            (m[0][0] * m[1][1] - m[0][1] * m[1][0]) * inv_det,
        ],
    ]
