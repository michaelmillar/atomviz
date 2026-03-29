from __future__ import annotations

ELEMENT_COLOURS: dict[str, str] = {
    "H": "#FFFFFF",
    "C": "#333333",
    "N": "#3050F8",
    "O": "#FF0D0D",
    "Si": "#F0C8A0",
    "Fe": "#E06633",
    "Ti": "#BFC2C7",
    "Al": "#BFA6A6",
    "Ga": "#C28F8F",
    "As": "#BD80E3",
    "Cd": "#FFD98F",
    "Te": "#D47A00",
    "Zn": "#7D80B0",
    "S": "#FFFF30",
    "Cu": "#C88033",
    "In": "#A67573",
    "Se": "#FFA100",
    "Pb": "#575961",
    "I": "#940094",
    "Br": "#A62929",
    "Sn": "#668080",
    "Ge": "#668F8F",
    "B": "#FFB5B5",
    "Na": "#AB5CF2",
    "K": "#8F40D4",
    "Ca": "#3DFF00",
    "Mg": "#8AFF00",
    "Li": "#CC80FF",
    "F": "#90E050",
    "Cl": "#1FF01F",
    "P": "#FF8000",
}

ELEMENT_RADII: dict[str, float] = {
    "H": 0.25,
    "C": 0.70,
    "N": 0.65,
    "O": 0.60,
    "Si": 1.10,
    "Fe": 1.26,
    "Ti": 1.47,
    "Al": 1.21,
    "Ga": 1.22,
    "As": 1.19,
    "Cd": 1.44,
    "Te": 1.38,
    "Zn": 1.22,
    "S": 1.05,
    "Cu": 1.28,
    "In": 1.42,
    "Se": 1.20,
    "Pb": 1.46,
    "I": 1.39,
    "Br": 1.20,
    "Sn": 1.39,
    "Ge": 1.20,
    "B": 0.84,
    "Na": 1.66,
    "K": 2.03,
    "Ca": 1.76,
    "Mg": 1.41,
    "Li": 1.28,
    "F": 0.57,
    "Cl": 1.02,
    "P": 1.07,
}


COVALENT_RADII: dict[str, float] = {
    "H": 0.31, "C": 0.76, "N": 0.71, "O": 0.66, "Si": 1.11,
    "Fe": 1.32, "Ti": 1.60, "Al": 1.21, "Ga": 1.22, "As": 1.19,
    "Cd": 1.44, "Te": 1.38, "Zn": 1.22, "S": 1.05, "Cu": 1.32,
    "In": 1.42, "Se": 1.20, "Pb": 1.46, "I": 1.39, "Br": 1.20,
    "Sn": 1.39, "Ge": 1.20, "B": 0.84, "Na": 1.66, "K": 2.03,
    "Ca": 1.76, "Mg": 1.41, "Li": 1.28, "F": 0.57, "Cl": 1.02,
    "P": 1.07,
}


def get_colour(element: str) -> str:
    return ELEMENT_COLOURS.get(element, "#808080")


def get_radius(element: str) -> float:
    return ELEMENT_RADII.get(element, 1.0)


def get_covalent_radius(element: str) -> float:
    return COVALENT_RADII.get(element, 1.5)
