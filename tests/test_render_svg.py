from atomviz.examples import silicon_diamond
from atomviz.render_svg import Style, render_unit_cell_svg


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
    assert 'class="atomviz-bond' in svg


def test_svg_has_css_classes():
    cell = silicon_diamond()
    svg = render_unit_cell_svg(cell)
    assert 'class="atomviz"' in svg
    assert 'class="atomviz-atom atom-Si"' in svg
    assert 'class="atomviz-label label-Si"' in svg
    assert 'class="atomviz-edge"' in svg


def test_svg_has_data_attributes():
    cell = silicon_diamond()
    svg = render_unit_cell_svg(cell)
    assert 'data-element="Si"' in svg
    assert 'data-index="' in svg
    assert 'data-structure="Silicon Diamond"' in svg


def test_svg_has_style_block():
    cell = silicon_diamond()
    svg = render_unit_cell_svg(cell)
    assert "<style>" in svg
    assert ".atomviz-atom" in svg


def test_svg_depth_opacity():
    cell = silicon_diamond()
    svg = render_unit_cell_svg(cell)
    assert 'opacity="' in svg


def test_svg_no_labels():
    cell = silicon_diamond()
    style = Style(show_labels=False)
    svg = render_unit_cell_svg(cell, style=style)
    assert 'class="atomviz-label' not in svg


def test_svg_no_bonds():
    cell = silicon_diamond()
    style = Style(show_bonds=False)
    svg = render_unit_cell_svg(cell, style=style)
    assert 'class="atomviz-bond' not in svg


def test_svg_no_lattice():
    cell = silicon_diamond()
    style = Style(show_lattice=False)
    svg = render_unit_cell_svg(cell, style=style)
    assert "atomviz-lattice" not in svg


def test_svg_no_depth_fade():
    cell = silicon_diamond()
    style = Style(depth_fade=False)
    svg = render_unit_cell_svg(cell, style=style)
    assert 'opacity="1.00"' in svg or 'opacity="1.0"' in svg


def test_svg_deterministic():
    cell = silicon_diamond()
    svg1 = render_unit_cell_svg(cell, theta=0.5, phi=0.5)
    svg2 = render_unit_cell_svg(cell, theta=0.5, phi=0.5)
    assert svg1 == svg2
