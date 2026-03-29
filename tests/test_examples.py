from atomviz.examples import gaas_zincblende, nacl_rocksalt, silicon_diamond


def test_silicon_diamond():
    cell = silicon_diamond()
    assert len(cell.atoms) == 8
    assert cell.title == "Silicon Diamond"
    assert all(a.element == "Si" for a in cell.atoms)
    assert len(cell.lattice_vectors) == 3


def test_gaas_zincblende():
    cell = gaas_zincblende()
    assert len(cell.atoms) == 8
    assert cell.title == "GaAs Zincblende"
    ga_count = sum(1 for a in cell.atoms if a.element == "Ga")
    as_count = sum(1 for a in cell.atoms if a.element == "As")
    assert ga_count == 4
    assert as_count == 4


def test_nacl_rocksalt():
    cell = nacl_rocksalt()
    assert len(cell.atoms) == 8
    assert cell.title == "NaCl Rocksalt"
    na_count = sum(1 for a in cell.atoms if a.element == "Na")
    cl_count = sum(1 for a in cell.atoms if a.element == "Cl")
    assert na_count == 4
    assert cl_count == 4


def test_lattice_vectors_are_cubic():
    for factory in [silicon_diamond, gaas_zincblende, nacl_rocksalt]:
        cell = factory()
        for vec in cell.lattice_vectors:
            nonzero = [v for v in vec if abs(v) > 0.01]
            assert len(nonzero) == 1


def test_atoms_have_element_properties():
    cell = silicon_diamond()
    for atom in cell.atoms:
        assert atom.colour != "#808080"
        assert atom.radius > 0
