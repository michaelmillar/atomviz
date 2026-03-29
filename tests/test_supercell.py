from atomviz.examples import silicon_diamond, nacl_rocksalt


def test_supercell_atom_count():
    cell = silicon_diamond()
    sc = cell.supercell(2, 2, 2)
    assert len(sc.atoms) == 8 * 8


def test_supercell_lattice_scaling():
    cell = silicon_diamond()
    sc = cell.supercell(2, 1, 3)
    assert abs(sc.lattice_vectors[0][0] - 5.43 * 2) < 0.01
    assert abs(sc.lattice_vectors[1][1] - 5.43) < 0.01
    assert abs(sc.lattice_vectors[2][2] - 5.43 * 3) < 0.01


def test_supercell_1x1x1_unchanged():
    cell = silicon_diamond()
    sc = cell.supercell(1, 1, 1)
    assert len(sc.atoms) == len(cell.atoms)
    for orig, copied in zip(cell.atoms, sc.atoms):
        for a, b in zip(orig.position, copied.position):
            assert abs(a - b) < 1e-10


def test_supercell_title():
    cell = silicon_diamond()
    sc = cell.supercell(2, 2, 2)
    assert "2x2x2" in sc.title


def test_supercell_preserves_elements():
    cell = nacl_rocksalt()
    sc = cell.supercell(2, 2, 2)
    na_count = sum(1 for a in sc.atoms if a.element == "Na")
    cl_count = sum(1 for a in sc.atoms if a.element == "Cl")
    assert na_count == 4 * 8
    assert cl_count == 4 * 8


def test_supercell_fractional_coords_in_range():
    cell = silicon_diamond()
    sc = cell.supercell(3, 3, 3)
    for atom in sc.atoms:
        for coord in atom.position:
            assert -0.01 <= coord <= 1.01
