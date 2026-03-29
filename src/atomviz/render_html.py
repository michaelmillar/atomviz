from __future__ import annotations

from atomviz.render_svg import render_unit_cell_svg
from atomviz.structure import UnitCell


def render_interactive(
    cell: UnitCell,
    width: int = 500,
    height: int = 500,
) -> str:
    initial_svg = render_unit_cell_svg(cell, theta=0.5, phi=0.5, width=width, height=height)

    atoms_js = "[\n"
    for atom in cell.atoms:
        atoms_js += (
            f'  {{element: "{atom.element}", '
            f'position: [{atom.position[0]}, {atom.position[1]}, {atom.position[2]}], '
            f'radius: {atom.radius}, colour: "{atom.colour}"}},\n'
        )
    atoms_js += "]"

    lattice_js = "[\n"
    for vec in cell.lattice_vectors:
        lattice_js += f"  [{vec[0]}, {vec[1]}, {vec[2]}],\n"
    lattice_js += "]"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{cell.title}</title>
<style>
body {{
    font-family: sans-serif;
    display: flex;
    flex-direction: column;
    align-items: center;
    background: #fafafa;
    margin: 20px;
}}
h1 {{
    color: #333;
    font-size: 1.4em;
}}
.controls {{
    display: flex;
    gap: 20px;
    margin: 16px 0;
    align-items: center;
}}
.controls label {{
    font-size: 0.9em;
    color: #555;
}}
.controls input[type="range"] {{
    width: 200px;
}}
#svg-container {{
    border: 1px solid #ddd;
    border-radius: 4px;
    background: white;
}}
</style>
</head>
<body>
<h1>{cell.title}</h1>
<div class="controls">
    <label>Theta <input type="range" id="theta" min="0" max="6.28" step="0.05" value="0.5"></label>
    <label>Phi <input type="range" id="phi" min="0" max="3.14" step="0.05" value="0.5"></label>
</div>
<div id="svg-container">{initial_svg}</div>

<script>
const atoms = {atoms_js};
const lattice = {lattice_js};
const title = "{cell.title}";
const W = {width};
const H = {height};
const atomScale = 0.3;
const minOpacity = 0.4;

const COVALENT_RADII = {{
    H: 0.31, C: 0.76, N: 0.71, O: 0.66, Si: 1.11,
    Fe: 1.32, Ti: 1.60, Al: 1.21, Ga: 1.22, As: 1.19,
    Cd: 1.44, Te: 1.38, Zn: 1.22, S: 1.05, Cu: 1.32,
    In: 1.42, Se: 1.20, Pb: 1.46, I: 1.39, Br: 1.20,
    Sn: 1.39, Ge: 1.20, B: 0.84, Na: 1.66, K: 2.03,
    Ca: 1.76, Mg: 1.41, Li: 1.28, F: 0.57, Cl: 1.02,
    P: 1.07
}};

const LATTICE_EDGES = [
    [0,1],[0,2],[0,3],[1,4],[1,5],[2,4],[2,6],[3,5],[3,6],[4,7],[5,7],[6,7]
];

function rotationMatrix(theta, phi) {{
    const ct = Math.cos(theta), st = Math.sin(theta);
    const cp = Math.cos(phi), sp = Math.sin(phi);
    return [
        [ct, 0, st],
        [st*sp, cp, -ct*sp],
        [-st*cp, sp, ct*cp]
    ];
}}

function matVecMul(m, v) {{
    return [
        m[0][0]*v[0] + m[0][1]*v[1] + m[0][2]*v[2],
        m[1][0]*v[0] + m[1][1]*v[1] + m[1][2]*v[2],
        m[2][0]*v[0] + m[2][1]*v[1] + m[2][2]*v[2]
    ];
}}

function toCartesian(frac) {{
    return [
        frac[0]*lattice[0][0] + frac[1]*lattice[1][0] + frac[2]*lattice[2][0],
        frac[0]*lattice[0][1] + frac[1]*lattice[1][1] + frac[2]*lattice[2][1],
        frac[0]*lattice[0][2] + frac[1]*lattice[1][2] + frac[2]*lattice[2][2]
    ];
}}

function latticeCorners() {{
    const a = lattice[0], b = lattice[1], c = lattice[2];
    return [
        [0,0,0], a, b, c,
        [a[0]+b[0], a[1]+b[1], a[2]+b[2]],
        [a[0]+c[0], a[1]+c[1], a[2]+c[2]],
        [b[0]+c[0], b[1]+c[1], b[2]+c[2]],
        [a[0]+b[0]+c[0], a[1]+b[1]+c[1], a[2]+b[2]+c[2]]
    ];
}}

function dist(p1, p2) {{
    return Math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2);
}}

function depthOpacity(depth, minD, maxD) {{
    const span = maxD - minD;
    if (span < 1e-6) return 1.0;
    const t = (depth - minD) / span;
    return minOpacity + (1.0 - minOpacity) * (1.0 - t);
}}

function getCovalentRadius(el) {{
    return COVALENT_RADII[el] || 1.5;
}}

function renderSVG(theta, phi) {{
    const rot = rotationMatrix(theta, phi);
    const cartPositions = atoms.map(a => toCartesian(a.position));
    const corners = latticeCorners();
    const allPts = cartPositions.concat(corners);

    const projected = allPts.map((p, i) => {{
        const r = matVecMul(rot, p);
        return {{x: r[0], y: r[1], depth: r[2], index: i}};
    }});

    const nAtoms = cartPositions.length;
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    for (const p of projected) {{
        if (p.x < minX) minX = p.x;
        if (p.x > maxX) maxX = p.x;
        if (p.y < minY) minY = p.y;
        if (p.y > maxY) maxY = p.y;
    }}

    const spanX = maxX > minX ? maxX - minX : 1;
    const spanY = maxY > minY ? maxY - minY : 1;
    const margin = 60;
    const scale = Math.min((W - 2*margin)/spanX, (H - 2*margin)/spanY);
    const cx = W/2, cy = H/2;
    const midX = (minX+maxX)/2, midY = (minY+maxY)/2;

    function scr(px, py) {{
        return [cx + (px-midX)*scale, cy + (py-midY)*scale];
    }}

    const atomDepths = projected.filter(p => p.index < nAtoms).map(p => p.depth);
    const minD = Math.min(...atomDepths);
    const maxD = Math.max(...atomDepths);

    let svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${{W}}" height="${{H}}" viewBox="0 0 ${{W}} ${{H}}" class="atomviz" data-structure="${{title}}">`;
    svg += `<style>
.atomviz-bg {{ fill: white; }}
.atomviz-title {{ font-family: sans-serif; font-size: 14px; fill: #333; }}
.atomviz-edge {{ stroke: #999; stroke-width: 1; stroke-dasharray: 4 3; fill: none; }}
.atomviz-bond {{ stroke: #666; stroke-width: 2; stroke-linecap: round; }}
.atomviz-atom {{ stroke: #333; stroke-width: 0.5; }}
.atomviz-label {{ font-family: sans-serif; font-size: 10px; fill: #555; }}
</style>`;
    svg += `<rect class="atomviz-bg" width="${{W}}" height="${{H}}"/>`;
    svg += `<text class="atomviz-title" x="${{W/2}}" y="24" text-anchor="middle">${{title}}</text>`;

    svg += '<g class="atomviz-lattice">';
    for (const [ei, [i,j]] of LATTICE_EDGES.entries()) {{
        const p1 = projected[nAtoms+i], p2 = projected[nAtoms+j];
        const [x1,y1] = scr(p1.x, p1.y);
        const [x2,y2] = scr(p2.x, p2.y);
        svg += `<line class="atomviz-edge" data-edge="${{ei}}" x1="${{x1.toFixed(1)}}" y1="${{y1.toFixed(1)}}" x2="${{x2.toFixed(1)}}" y2="${{y2.toFixed(1)}}"/>`;
    }}
    svg += '</g>';

    const drawOrder = [];

    for (let i = 0; i < nAtoms; i++) {{
        for (let j = i+1; j < nAtoms; j++) {{
            const d = dist(cartPositions[i], cartPositions[j]);
            const ri = getCovalentRadius(atoms[i].element);
            const rj = getCovalentRadius(atoms[j].element);
            if (d > 0.5 && d < ri + rj + 0.45) {{
                const p1 = projected[i], p2 = projected[j];
                const [x1,y1] = scr(p1.x, p1.y);
                const [x2,y2] = scr(p2.x, p2.y);
                const avgD = (p1.depth+p2.depth)/2;
                const op = depthOpacity(avgD, minD, maxD);
                drawOrder.push([avgD, `<line class="atomviz-bond bond-${{atoms[i].element}}-${{atoms[j].element}}" data-from="${{i}}" data-to="${{j}}" x1="${{x1.toFixed(1)}}" y1="${{y1.toFixed(1)}}" x2="${{x2.toFixed(1)}}" y2="${{y2.toFixed(1)}}" opacity="${{op.toFixed(2)}}"/>`]);
            }}
        }}
    }}

    for (const p of projected.filter(p => p.index < nAtoms)) {{
        const atom = atoms[p.index];
        const [sx, sy] = scr(p.x, p.y);
        let r = atom.radius * atomScale * scale * 0.15;
        r = Math.max(r, 4);
        r = Math.min(r, 25);
        const op = depthOpacity(p.depth, minD, maxD);
        drawOrder.push([p.depth, `<circle class="atomviz-atom atom-${{atom.element}}" data-index="${{p.index}}" data-element="${{atom.element}}" cx="${{sx.toFixed(1)}}" cy="${{sy.toFixed(1)}}" r="${{r.toFixed(1)}}" fill="${{atom.colour}}" opacity="${{op.toFixed(2)}}"/>`]);
        drawOrder.push([p.depth+0.001, `<text class="atomviz-label label-${{atom.element}}" data-index="${{p.index}}" x="${{sx.toFixed(1)}}" y="${{(sy+r+12).toFixed(1)}}" text-anchor="middle" opacity="${{op.toFixed(2)}}">${{atom.element}}</text>`]);
    }}

    drawOrder.sort((a,b) => a[0] - b[0]);
    for (const [, elem] of drawOrder) {{
        svg += elem;
    }}

    svg += '</svg>';
    return svg;
}}

const thetaSlider = document.getElementById('theta');
const phiSlider = document.getElementById('phi');
const container = document.getElementById('svg-container');

function update() {{
    container.innerHTML = renderSVG(parseFloat(thetaSlider.value), parseFloat(phiSlider.value));
}}

thetaSlider.addEventListener('input', update);
phiSlider.addEventListener('input', update);
</script>
</body>
</html>"""
