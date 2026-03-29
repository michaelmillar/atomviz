import pytest

from atomviz.parse_poscar import parse_poscar


SILICON_POSCAR = """Silicon diamond
1.0
5.43 0.0 0.0
0.0 5.43 0.0
0.0 0.0 5.43
Si
8
Direct
0.0 0.0 0.0
0.5 0.5 0.0
0.5 0.0 0.5
0.0 0.5 0.5
0.25 0.25 0.25
0.75 0.75 0.25
0.75 0.25 0.75
0.25 0.75 0.75
"""


def test_parse_poscar_atom_count():
    cell = parse_poscar(SILICON_POSCAR)
    assert len(cell.atoms) == 8


def test_parse_poscar_elements():
    cell = parse_poscar(SILICON_POSCAR)
    assert all(a.element == "Si" for a in cell.atoms)


def test_parse_poscar_lattice():
    cell = parse_poscar(SILICON_POSCAR)
    assert abs(cell.lattice_vectors[0][0] - 5.43) < 0.01


def test_parse_poscar_title():
    cell = parse_poscar(SILICON_POSCAR)
    assert cell.title == "Silicon diamond"


def test_parse_poscar_scale_factor():
    poscar = """Scaled
2.0
2.715 0.0 0.0
0.0 2.715 0.0
0.0 0.0 2.715
Si
1
Direct
0.0 0.0 0.0
"""
    cell = parse_poscar(poscar)
    assert abs(cell.lattice_vectors[0][0] - 5.43) < 0.01


def test_parse_poscar_multi_species():
    poscar = """GaAs
1.0
5.65 0.0 0.0
0.0 5.65 0.0
0.0 0.0 5.65
Ga As
4 4
Direct
0.0 0.0 0.0
0.5 0.5 0.0
0.5 0.0 0.5
0.0 0.5 0.5
0.25 0.25 0.25
0.75 0.75 0.25
0.75 0.25 0.75
0.25 0.75 0.75
"""
    cell = parse_poscar(poscar)
    assert len(cell.atoms) == 8
    ga = [a for a in cell.atoms if a.element == "Ga"]
    assert len(ga) == 4


def test_parse_poscar_selective_dynamics():
    poscar = """Test
1.0
5.0 0.0 0.0
0.0 5.0 0.0
0.0 0.0 5.0
Fe
1
Selective dynamics
Direct
0.0 0.0 0.0 T T T
"""
    cell = parse_poscar(poscar)
    assert len(cell.atoms) == 1
    assert cell.atoms[0].element == "Fe"


def test_parse_poscar_too_short():
    with pytest.raises(ValueError):
        parse_poscar("too\nshort")
