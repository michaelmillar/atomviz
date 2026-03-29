#!/usr/bin/env python3
from __future__ import annotations

import math
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

from atomviz.examples import gaas_zincblende, nacl_rocksalt, silicon_diamond
from atomviz.render_svg import Style, render_unit_cell_svg

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "assets" / "demo.mp4"

WIDTH = 800
HEIGHT = 600
FPS = 30

STRUCTURES = [
    ("Silicon Diamond", silicon_diamond()),
    ("GaAs Zincblende", gaas_zincblende()),
    ("NaCl Rocksalt", nacl_rocksalt()),
    ("Silicon 2x2x2 Supercell", silicon_diamond().supercell(2, 2, 2)),
]

HOLD_FRAMES = int(FPS * 0.6)
ROTATE_FRAMES = int(FPS * 2.5)
TRANSITION_FRAMES = int(FPS * 0.3)


def render_frame_html(svg: str) -> str:
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<style>
body {{
    margin: 0; padding: 0;
    display: flex; justify-content: center; align-items: center;
    width: {WIDTH}px; height: {HEIGHT}px;
    background: #0d1117;
    overflow: hidden;
}}
svg {{
    filter: drop-shadow(0 2px 8px rgba(0,0,0,0.3));
}}
</style>
</head><body>{svg}</body></html>"""


def generate_frames(tmpdir: Path) -> list[Path]:
    frames: list[Path] = []
    frame_num = 0

    style = Style(
        background="#0d1117",
        title_fill="#e6edf3",
        label_fill="#8b949e",
        lattice_stroke="#30363d",
        bond_stroke="#8b949e",
        atom_stroke="#484f58",
    )

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": WIDTH, "height": HEIGHT})

        for struct_idx, (_, cell) in enumerate(STRUCTURES):
            theta_start = 0.4
            theta_end = theta_start + math.pi * 0.6
            phi_base = 0.55

            for f in range(HOLD_FRAMES):
                svg = render_unit_cell_svg(
                    cell, theta=theta_start, phi=phi_base,
                    width=WIDTH - 80, height=HEIGHT - 80, style=style,
                )
                html = render_frame_html(svg)
                page.set_content(html, wait_until="load")
                path = tmpdir / f"frame_{frame_num:05d}.png"
                page.screenshot(path=str(path))
                frames.append(path)
                frame_num += 1

            for f in range(ROTATE_FRAMES):
                t = f / ROTATE_FRAMES
                ease = t * t * (3 - 2 * t)
                theta = theta_start + (theta_end - theta_start) * ease
                phi = phi_base + 0.15 * math.sin(t * math.pi)

                svg = render_unit_cell_svg(
                    cell, theta=theta, phi=phi,
                    width=WIDTH - 80, height=HEIGHT - 80, style=style,
                )
                html = render_frame_html(svg)
                page.set_content(html, wait_until="load")
                path = tmpdir / f"frame_{frame_num:05d}.png"
                page.screenshot(path=str(path))
                frames.append(path)
                frame_num += 1

            for f in range(HOLD_FRAMES):
                svg = render_unit_cell_svg(
                    cell, theta=theta_end, phi=phi_base,
                    width=WIDTH - 80, height=HEIGHT - 80, style=style,
                )
                html = render_frame_html(svg)
                page.set_content(html, wait_until="load")
                path = tmpdir / f"frame_{frame_num:05d}.png"
                page.screenshot(path=str(path))
                frames.append(path)
                frame_num += 1

            if struct_idx < len(STRUCTURES) - 1:
                for f in range(TRANSITION_FRAMES):
                    alpha = int(255 * (f / TRANSITION_FRAMES))
                    img = Image.open(frames[-1]).copy()
                    overlay = Image.new("RGBA", img.size, (13, 17, 23, alpha))
                    img = Image.alpha_composite(img.convert("RGBA"), overlay)
                    path = tmpdir / f"frame_{frame_num:05d}.png"
                    img.save(path)
                    frames.append(path)
                    frame_num += 1

        browser.close()

    return frames


def add_labels(frames: list[Path]) -> None:
    frames_per_struct = HOLD_FRAMES + ROTATE_FRAMES + HOLD_FRAMES + TRANSITION_FRAMES
    last_struct_frames = HOLD_FRAMES + ROTATE_FRAMES + HOLD_FRAMES

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 16)
    except OSError:
        font = ImageFont.load_default()

    frame_idx = 0
    for struct_idx, (label, _) in enumerate(STRUCTURES):
        is_last = struct_idx == len(STRUCTURES) - 1
        n = last_struct_frames if is_last else frames_per_struct

        for _ in range(n):
            if frame_idx >= len(frames):
                break
            img = Image.open(frames[frame_idx]).convert("RGBA")
            draw = ImageDraw.Draw(img)

            draw.text((20, HEIGHT - 36), label, fill=(139, 148, 158, 200), font=font)

            cmd = f"atomviz render {label.lower().replace(' ', '_')}"
            draw.text((20, 16), cmd, fill=(88, 96, 105, 180), font=font)

            img.save(frames[frame_idx])
            frame_idx += 1


def stitch_video(tmpdir: Path) -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-framerate", str(FPS),
            "-i", str(tmpdir / "frame_%05d.png"),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "slow",
            "-crf", "22",
            "-vf", f"scale={WIDTH}:{HEIGHT}",
            str(OUTPUT),
        ],
        check=True,
        capture_output=True,
    )


def main() -> None:
    print(f"Generating demo video at {OUTPUT}")
    tmpdir = Path(tempfile.mkdtemp(prefix="atomviz_demo_"))

    try:
        print("Rendering frames...")
        frames = generate_frames(tmpdir)
        print(f"  {len(frames)} frames generated")

        print("Adding labels...")
        add_labels(frames)

        print("Stitching video...")
        stitch_video(tmpdir)
        print(f"Done: {OUTPUT}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    main()
