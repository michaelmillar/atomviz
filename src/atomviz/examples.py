from __future__ import annotations

from atomviz.elements import get_colour, get_radius
from atomviz.structure import Atom, UnitCell


def _make_atom(element: str, position: tuple[float, float, float]) -> Atom:
    return Atom(
        element=element,
        position=position,
        radius=get_radius(element),
        colour=get_colour(element),
    )


def silicon_diamond() -> UnitCell:
    a = 5.43
    lattice = [(a, 0.0, 0.0), (0.0, a, 0.0), (0.0, 0.0, a)]

    frac_positions = [
        (0.0, 0.0, 0.0),
        (0.5, 0.5, 0.0),
        (0.5, 0.0, 0.5),
        (0.0, 0.5, 0.5),
        (0.25, 0.25, 0.25),
        (0.75, 0.75, 0.25),
        (0.75, 0.25, 0.75),
        (0.25, 0.75, 0.75),
    ]

    atoms = [_make_atom("Si", pos) for pos in frac_positions]
    return UnitCell(atoms=atoms, lattice_vectors=lattice, title="Silicon Diamond")


def gaas_zincblende() -> UnitCell:
    a = 5.65
    lattice = [(a, 0.0, 0.0), (0.0, a, 0.0), (0.0, 0.0, a)]

    ga_positions = [
        (0.0, 0.0, 0.0),
        (0.5, 0.5, 0.0),
        (0.5, 0.0, 0.5),
        (0.0, 0.5, 0.5),
    ]

    as_positions = [
        (0.25, 0.25, 0.25),
        (0.75, 0.75, 0.25),
        (0.75, 0.25, 0.75),
        (0.25, 0.75, 0.75),
    ]

    atoms = [_make_atom("Ga", pos) for pos in ga_positions]
    atoms += [_make_atom("As", pos) for pos in as_positions]
    return UnitCell(atoms=atoms, lattice_vectors=lattice, title="GaAs Zincblende")


def nacl_rocksalt() -> UnitCell:
    a = 5.64
    lattice = [(a, 0.0, 0.0), (0.0, a, 0.0), (0.0, 0.0, a)]

    na_positions = [
        (0.0, 0.0, 0.0),
        (0.5, 0.5, 0.0),
        (0.5, 0.0, 0.5),
        (0.0, 0.5, 0.5),
    ]

    cl_positions = [
        (0.5, 0.0, 0.0),
        (0.0, 0.5, 0.0),
        (0.0, 0.0, 0.5),
        (0.5, 0.5, 0.5),
    ]

    atoms = [_make_atom("Na", pos) for pos in na_positions]
    atoms += [_make_atom("Cl", pos) for pos in cl_positions]
    return UnitCell(atoms=atoms, lattice_vectors=lattice, title="NaCl Rocksalt")
