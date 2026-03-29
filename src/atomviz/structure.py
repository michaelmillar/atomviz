from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Atom:
    element: str
    position: tuple[float, float, float]
    radius: float = 1.0
    colour: str = "#808080"


@dataclass
class UnitCell:
    atoms: list[Atom]
    lattice_vectors: list[tuple[float, float, float]]
    title: str = "Unit Cell"

    def lattice_matrix(self) -> list[list[float]]:
        return [list(v) for v in self.lattice_vectors]
