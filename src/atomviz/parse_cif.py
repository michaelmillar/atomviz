from __future__ import annotations

import math
import re
from pathlib import Path

from atomviz.elements import get_colour, get_radius
from atomviz.structure import Atom, UnitCell


def _cell_vectors(a: float, b: float, c: float, alpha: float, beta: float, gamma: float) -> list[tuple[float, float, float]]:
    alpha_r = math.radians(alpha)
    beta_r = math.radians(beta)
    gamma_r = math.radians(gamma)

    a_vec = (a, 0.0, 0.0)

    bx = b * math.cos(gamma_r)
    by = b * math.sin(gamma_r)
    b_vec = (bx, by, 0.0)

    cx = c * math.cos(beta_r)
    cy = c * (math.cos(alpha_r) - math.cos(beta_r) * math.cos(gamma_r)) / math.sin(gamma_r)
    cz = math.sqrt(max(c * c - cx * cx - cy * cy, 0.0))
    c_vec = (cx, cy, cz)

    return [a_vec, b_vec, c_vec]


def _strip_uncertainty(value: str) -> float:
    cleaned = re.sub(r"\([^)]*\)", "", value.strip())
    return float(cleaned)


def _parse_token(raw: str) -> str:
    if raw.startswith("'") and raw.endswith("'"):
        return raw[1:-1]
    if raw.startswith('"') and raw.endswith('"'):
        return raw[1:-1]
    return raw


def _extract_element(label: str) -> str:
    match = re.match(r"([A-Z][a-z]?)", label)
    if match:
        return match.group(1)
    return label


def parse_cif(source: str | Path) -> UnitCell:
    if isinstance(source, Path):
        text = source.read_text()
        title = source.stem
    else:
        text = source
        title = "CIF Structure"

    cell_params: dict[str, float] = {}
    cell_keys = {
        "_cell_length_a", "_cell_length_b", "_cell_length_c",
        "_cell_angle_alpha", "_cell_angle_beta", "_cell_angle_gamma",
    }

    lines = text.splitlines()
    idx = 0
    atoms: list[Atom] = []

    while idx < len(lines):
        line = lines[idx].strip()

        if not line or line.startswith("#"):
            idx += 1
            continue

        if line.lower().startswith("data_"):
            tag = line[5:].strip()
            if tag:
                title = tag
            idx += 1
            continue

        if line.startswith("_") and "loop_" not in line:
            parts = line.split(None, 1)
            if len(parts) == 2:
                key = parts[0].lower()
                if key in cell_keys:
                    cell_params[key] = _strip_uncertainty(parts[1])
            idx += 1
            continue

        if line.lower() == "loop_":
            idx += 1
            headers: list[str] = []
            while idx < len(lines) and lines[idx].strip().startswith("_"):
                headers.append(lines[idx].strip().lower())
                idx += 1

            has_fract = (
                "_atom_site_fract_x" in headers
                and "_atom_site_fract_y" in headers
                and "_atom_site_fract_z" in headers
            )

            if not has_fract:
                while idx < len(lines):
                    row = lines[idx].strip()
                    if not row or row.startswith("_") or row.lower().startswith("loop_") or row.lower().startswith("data_"):
                        break
                    idx += 1
                continue

            col_fx = headers.index("_atom_site_fract_x")
            col_fy = headers.index("_atom_site_fract_y")
            col_fz = headers.index("_atom_site_fract_z")

            col_symbol = None
            if "_atom_site_type_symbol" in headers:
                col_symbol = headers.index("_atom_site_type_symbol")
            elif "_atom_site_label" in headers:
                col_symbol = headers.index("_atom_site_label")

            while idx < len(lines):
                row = lines[idx].strip()
                if not row or row.startswith("_") or row.lower().startswith("loop_") or row.lower().startswith("data_"):
                    break

                tokens = row.split()
                if len(tokens) < len(headers):
                    idx += 1
                    continue

                fx = _strip_uncertainty(tokens[col_fx])
                fy = _strip_uncertainty(tokens[col_fy])
                fz = _strip_uncertainty(tokens[col_fz])

                if col_symbol is not None:
                    raw_label = _parse_token(tokens[col_symbol])
                    element = _extract_element(raw_label)
                else:
                    element = "X"

                atoms.append(Atom(
                    element=element,
                    position=(fx, fy, fz),
                    radius=get_radius(element),
                    colour=get_colour(element),
                ))
                idx += 1
            continue

        idx += 1

    a = cell_params.get("_cell_length_a", 1.0)
    b = cell_params.get("_cell_length_b", 1.0)
    c = cell_params.get("_cell_length_c", 1.0)
    alpha = cell_params.get("_cell_angle_alpha", 90.0)
    beta = cell_params.get("_cell_angle_beta", 90.0)
    gamma = cell_params.get("_cell_angle_gamma", 90.0)

    lattice = _cell_vectors(a, b, c, alpha, beta, gamma)

    return UnitCell(atoms=atoms, lattice_vectors=lattice, title=title)
