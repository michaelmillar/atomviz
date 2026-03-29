from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class ProjectedPoint:
    x: float
    y: float
    depth: float
    index: int


def _rotation_matrix(theta: float, phi: float) -> list[list[float]]:
    ct = math.cos(theta)
    st = math.sin(theta)
    cp = math.cos(phi)
    sp = math.sin(phi)

    return [
        [ct, 0, st],
        [st * sp, cp, -ct * sp],
        [-st * cp, sp, ct * cp],
    ]


def _mat_vec_mul(
    mat: list[list[float]], vec: tuple[float, float, float],
) -> tuple[float, float, float]:
    return (
        mat[0][0] * vec[0] + mat[0][1] * vec[1] + mat[0][2] * vec[2],
        mat[1][0] * vec[0] + mat[1][1] * vec[1] + mat[1][2] * vec[2],
        mat[2][0] * vec[0] + mat[2][1] * vec[1] + mat[2][2] * vec[2],
    )


def orthographic_project(
    points: list[tuple[float, float, float]],
    theta: float = 0.5,
    phi: float = 0.5,
) -> list[ProjectedPoint]:
    rot = _rotation_matrix(theta, phi)
    projected = []

    for i, point in enumerate(points):
        rx, ry, rz = _mat_vec_mul(rot, point)
        projected.append(ProjectedPoint(x=rx, y=ry, depth=rz, index=i))

    projected.sort(key=lambda p: p.depth)
    return projected


def project_point(
    point: tuple[float, float, float],
    theta: float = 0.5,
    phi: float = 0.5,
) -> tuple[float, float, float]:
    rot = _rotation_matrix(theta, phi)
    return _mat_vec_mul(rot, point)
