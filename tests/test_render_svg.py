from atomviz.examples import silicon_diamond
from atomviz.render_svg import render_unit_cell_svg


def test_render_produces_svg():
    cell = silicon_diamond()
    svg = render_unit_cell_svg(cell)
    assert svg.startswith("<svg")
    assert svg.endswith("</svg>")


def test_svg_contains_circles():
    cell = silicon_diamond()
    svg = render_unit_cell_svg(cell)
    assert "<circle" in svg


def test_svg_contains_lattice_edges():
    cell = silicon_diamond()
    svg = render_unit_cell_svg(cell)
    assert "stroke-dasharray" in svg


def test_svg_contains_element_labels():
    cell = silicon_diamond()
    svg = render_unit_cell_svg(cell)
    assert ">Si<" in svg


def test_svg_contains_title():
    cell = silicon_diamond()
    svg = render_unit_cell_svg(cell)
    assert "Silicon Diamond" in svg


def test_svg_custom_dimensions():
    cell = silicon_diamond()
    svg = render_unit_cell_svg(cell, width=800, height=600)
    assert 'width="800"' in svg
    assert 'height="600"' in svg


def test_svg_bonds_present():
    cell = silicon_diamond()
    svg = render_unit_cell_svg(cell)
    assert 'stroke-linecap="round"' in svg
