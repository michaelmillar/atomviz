from atomviz.parse_cif import parse_cif


SILICON_CIF = """data_silicon
_cell_length_a   5.43
_cell_length_b   5.43
_cell_length_c   5.43
_cell_angle_alpha   90.0
_cell_angle_beta    90.0
_cell_angle_gamma   90.0

loop_
_atom_site_type_symbol
_atom_site_fract_x
_atom_site_fract_y
_atom_site_fract_z
Si 0.0 0.0 0.0
Si 0.5 0.5 0.0
Si 0.5 0.0 0.5
Si 0.0 0.5 0.5
Si 0.25 0.25 0.25
Si 0.75 0.75 0.25
Si 0.75 0.25 0.75
Si 0.25 0.75 0.75
"""


def test_parse_cif_atom_count():
    cell = parse_cif(SILICON_CIF)
    assert len(cell.atoms) == 8


def test_parse_cif_elements():
    cell = parse_cif(SILICON_CIF)
    assert all(a.element == "Si" for a in cell.atoms)


def test_parse_cif_lattice():
    cell = parse_cif(SILICON_CIF)
    a_vec = cell.lattice_vectors[0]
    assert abs(a_vec[0] - 5.43) < 0.01
    assert abs(a_vec[1]) < 0.01
    assert abs(a_vec[2]) < 0.01


def test_parse_cif_title():
    cell = parse_cif(SILICON_CIF)
    assert cell.title == "silicon"


def test_parse_cif_fractional_coords():
    cell = parse_cif(SILICON_CIF)
    first = cell.atoms[0]
    assert first.position == (0.0, 0.0, 0.0)


def test_parse_cif_with_uncertainty():
    cif = """data_test
_cell_length_a   5.430(1)
_cell_length_b   5.430(1)
_cell_length_c   5.430(1)
_cell_angle_alpha   90.0
_cell_angle_beta    90.0
_cell_angle_gamma   90.0

loop_
_atom_site_type_symbol
_atom_site_fract_x
_atom_site_fract_y
_atom_site_fract_z
Si 0.125(1) 0.125(1) 0.125(1)
"""
    cell = parse_cif(cif)
    assert len(cell.atoms) == 1
    assert abs(cell.atoms[0].position[0] - 0.125) < 0.001


def test_parse_cif_label_fallback():
    cif = """data_test
_cell_length_a   5.0
_cell_length_b   5.0
_cell_length_c   5.0
_cell_angle_alpha   90.0
_cell_angle_beta    90.0
_cell_angle_gamma   90.0

loop_
_atom_site_label
_atom_site_fract_x
_atom_site_fract_y
_atom_site_fract_z
Fe1 0.0 0.0 0.0
O2 0.5 0.5 0.5
"""
    cell = parse_cif(cif)
    assert cell.atoms[0].element == "Fe"
    assert cell.atoms[1].element == "O"


def test_parse_cif_non_cubic():
    cif = """data_hexagonal
_cell_length_a   3.0
_cell_length_b   3.0
_cell_length_c   5.0
_cell_angle_alpha   90.0
_cell_angle_beta    90.0
_cell_angle_gamma   120.0

loop_
_atom_site_type_symbol
_atom_site_fract_x
_atom_site_fract_y
_atom_site_fract_z
Zn 0.333 0.667 0.0
"""
    cell = parse_cif(cif)
    assert len(cell.atoms) == 1
    b_vec = cell.lattice_vectors[1]
    assert abs(b_vec[0] - (-1.5)) < 0.01
    assert abs(b_vec[1] - 2.598) < 0.01
