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

    def supercell(self, nx: int = 1, ny: int = 1, nz: int = 1) -> "UnitCell":
        new_atoms: list[Atom] = []
        for ix in range(nx):
            for iy in range(ny):
                for iz in range(nz):
                    for atom in self.atoms:
                        new_pos = (
                            (atom.position[0] + ix) / nx,
                            (atom.position[1] + iy) / ny,
                            (atom.position[2] + iz) / nz,
                        )
                        new_atoms.append(Atom(
                            element=atom.element,
                            position=new_pos,
                            radius=atom.radius,
                            colour=atom.colour,
                        ))
        a, b, c = self.lattice_vectors
        new_lattice = [
            (a[0] * nx, a[1] * nx, a[2] * nx),
            (b[0] * ny, b[1] * ny, b[2] * ny),
            (c[0] * nz, c[1] * nz, c[2] * nz),
        ]
        return UnitCell(
            atoms=new_atoms,
            lattice_vectors=new_lattice,
            title=f"{self.title} {nx}x{ny}x{nz}",
        )
