from atomviz.structure import Atom, UnitCell


def test_atom_defaults():
    atom = Atom(element="Si", position=(0.0, 0.0, 0.0))
    assert atom.radius == 1.0
    assert atom.colour == "#808080"


def test_atom_custom():
    atom = Atom(element="C", position=(1.0, 2.0, 3.0), radius=0.7, colour="#333333")
    assert atom.element == "C"
    assert atom.position == (1.0, 2.0, 3.0)
    assert atom.radius == 0.7
    assert atom.colour == "#333333"


def test_unit_cell_creation():
    atoms = [
        Atom(element="Si", position=(0.0, 0.0, 0.0)),
        Atom(element="Si", position=(0.25, 0.25, 0.25)),
    ]
    lattice = [(5.43, 0.0, 0.0), (0.0, 5.43, 0.0), (0.0, 0.0, 5.43)]
    cell = UnitCell(atoms=atoms, lattice_vectors=lattice, title="Test Cell")
    assert len(cell.atoms) == 2
    assert cell.title == "Test Cell"
    assert len(cell.lattice_vectors) == 3


def test_lattice_matrix():
    lattice = [(5.0, 0.0, 0.0), (0.0, 5.0, 0.0), (0.0, 0.0, 5.0)]
    cell = UnitCell(atoms=[], lattice_vectors=lattice)
    mat = cell.lattice_matrix()
    assert mat == [[5.0, 0.0, 0.0], [0.0, 5.0, 0.0], [0.0, 0.0, 5.0]]
