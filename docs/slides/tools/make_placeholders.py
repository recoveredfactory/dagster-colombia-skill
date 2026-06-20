#!/usr/bin/env python3
"""Generate clean SVG placeholder images for the slide deck.

Reads ``assets/manifest.json`` and writes one ``assets/<name>.svg`` per entry,
so the deck looks finished before any real screenshots exist. Replace a
placeholder by dropping a real image in ``assets/`` and pointing the slide at
it (or just overwrite the ``.svg``).

Usage:
    python3 tools/make_placeholders.py            # write missing placeholders
    python3 tools/make_placeholders.py --force    # overwrite existing ones too

No third-party dependencies — standard library only.
"""
from __future__ import annotations

import argparse
import html
import json
import textwrap
from pathlib import Path

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets"
MANIFEST = ASSETS / "manifest.json"

# Placeholders are TRANSPARENT (no background fill) and drawn in palette-neutral
# grays, so the card/slide background comes from CSS and they read on any palette.
NEUTRAL = "#8f877a"   # label text + glyph
MUTED = "#a89e8d"     # filename / source
LINE = "#9a9182"      # dashed border + glyph strokes
HOT = "#c8553f"       # small accent (dot + "IMAGE PLACEHOLDER")

# Logical pixel dimensions per kind.
DIMS = {
    "shot":  (1600, 1000),
    "photo": (1600, 1067),
    "phone": (460, 920),
    "book":  (640, 900),
}


def mountains(cx: float, cy: float, scale: float) -> str:
    """A small, friendly 'image' glyph (sun + two peaks)."""
    s = scale
    return f"""
    <g stroke="{LINE}" stroke-width="{6*s/40:.1f}" fill="none" stroke-linejoin="round" opacity="0.9">
      <circle cx="{cx - 70*s/40:.1f}" cy="{cy - 38*s/40:.1f}" r="{16*s/40:.1f}" fill="{HOT}" stroke="none" opacity="0.85"/>
      <polyline points="{cx-110*s/40:.1f},{cy+45*s/40:.1f} {cx-45*s/40:.1f},{cy-20*s/40:.1f} {cx+5*s/40:.1f},{cy+18*s/40:.1f} {cx+55*s/40:.1f},{cy-35*s/40:.1f} {cx+115*s/40:.1f},{cy+45*s/40:.1f}"/>
    </g>"""


def make_svg(name: str, kind: str, label: str, source: str | None) -> str:
    w, h = DIMS.get(kind, DIMS["shot"])
    label = html.escape(label)
    fname = html.escape(f"{name}.svg")
    is_small = kind in ("phone", "book")

    eyebrow_size = 16 if is_small else 22
    label_size = 26 if is_small else 40
    file_size = 14 if is_small else 18
    glyph_scale = 46 if is_small else 78

    # Wrap the label so long titles don't overflow narrow placeholders.
    wrap_at = 22 if is_small else 34
    lines = textwrap.wrap(label, width=wrap_at) or [label]
    line_h = label_size * 1.25
    block_h = line_h * len(lines)
    start_y = h / 2 + glyph_scale * 0.5 + 30 - block_h / 2 + label_size
    tspans = "".join(
        f'<tspan x="{w/2:.0f}" y="{start_y + i*line_h:.1f}">{ln}</tspan>'
        for i, ln in enumerate(lines)
    )

    src_line = (
        f'<text x="{w/2:.0f}" y="{h-46:.0f}" text-anchor="middle" '
        f'font-family="monospace" font-size="{file_size-2}" fill="{MUTED}">{html.escape(source)}</text>'
        if source else ""
    )

    inset = 18
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Placeholder: {label}">
  <rect x="{inset}" y="{inset}" width="{w-2*inset}" height="{h-2*inset}" rx="14"
        fill="none" stroke="{LINE}" stroke-width="3" stroke-dasharray="14 12"/>
  {mountains(w/2, h/2 - (40 if is_small else 70), glyph_scale)}
  <text x="{w/2:.0f}" y="{h/2 + glyph_scale*0.4:.0f}" text-anchor="middle"
        font-family="monospace" font-size="{eyebrow_size}" letter-spacing="3"
        fill="{HOT}" font-weight="bold">IMAGE PLACEHOLDER</text>
  <text text-anchor="middle" font-family="Georgia, serif" font-size="{label_size}"
        fill="{NEUTRAL}" font-weight="bold">{tspans}</text>
  <text x="{w/2:.0f}" y="{h-72:.0f}" text-anchor="middle"
        font-family="monospace" font-size="{file_size}" fill="{MUTED}">assets/{fname}</text>
  {src_line}
</svg>
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--force", action="store_true", help="overwrite existing placeholders")
    args = ap.parse_args()

    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    written, skipped = 0, 0
    for entry in data["assets"]:
        out = ASSETS / f"{entry['name']}.svg"
        if out.exists() and not args.force:
            skipped += 1
            continue
        out.write_text(
            make_svg(entry["name"], entry.get("kind", "shot"),
                     entry.get("label", entry["name"]), entry.get("source")),
            encoding="utf-8",
        )
        written += 1
        print(f"  wrote {out.relative_to(HERE.parent)}")

    print(f"\nDone. {written} written, {skipped} kept "
          f"({'use --force to overwrite' if skipped else 'all generated'}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
