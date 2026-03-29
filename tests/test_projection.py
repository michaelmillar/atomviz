import math

from atomviz.projection import orthographic_project, project_point


def test_identity_projection():
    result = project_point((1.0, 0.0, 0.0), theta=0.0, phi=0.0)
    assert abs(result[0] - 1.0) < 1e-10
    assert abs(result[1] - 0.0) < 1e-10
    assert abs(result[2] - 0.0) < 1e-10


def test_project_multiple_points():
    points = [
        (0.0, 0.0, 0.0),
        (1.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
        (0.0, 0.0, 1.0),
    ]
    projected = orthographic_project(points, theta=0.3, phi=0.3)
    assert len(projected) == 4
    assert all(hasattr(p, "x") for p in projected)
    assert all(hasattr(p, "y") for p in projected)
    assert all(hasattr(p, "depth") for p in projected)


def test_depth_sorting():
    points = [
        (0.0, 0.0, 10.0),
        (0.0, 0.0, -10.0),
        (0.0, 0.0, 0.0),
    ]
    projected = orthographic_project(points, theta=0.0, phi=0.0)
    depths = [p.depth for p in projected]
    assert depths == sorted(depths)


def test_rotation_preserves_distance():
    point = (3.0, 4.0, 5.0)
    original_length = math.sqrt(sum(c**2 for c in point))
    result = project_point(point, theta=1.2, phi=0.8)
    result_length = math.sqrt(sum(c**2 for c in result))
    assert abs(original_length - result_length) < 1e-10
