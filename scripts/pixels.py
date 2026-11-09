"""Draw Press Start 2P as filled rectangles. No external font loading."""

from __future__ import annotations

import json
from pathlib import Path


def load_atlas(path: Path) -> dict[str, list[str]]:
    data = json.loads(path.read_text())
    return data["glyphs"]


def text_width(text: str, scale: int, atlas: dict[str, list[str]]) -> int:
    return sum(len(atlas[ch][0]) * scale for ch in text)


def text_height(scale: int, atlas: dict[str, list[str]]) -> int:
    sample = atlas["A"]
    return len(sample) * scale


class Svg:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.parts: list[str] = []

    def rect(self, x: int, y: int, w: int, h: int, fill: str) -> None:
        if w <= 0 or h <= 0:
            return
        self.parts.append(
            f'<rect x="{int(x)}" y="{int(y)}" width="{int(w)}" height="{int(h)}" fill="{fill}"/>'
        )

    def save(self, path: Path, title: str) -> None:
        safe = (
            title.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        body = "\n".join(self.parts)
        path.write_text(
            "\n".join(
                [
                    f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}" role="img" shape-rendering="crispEdges">',
                    f"<title>{safe}</title>",
                    body,
                    "</svg>",
                    "",
                ]
            )
        )


def draw_text(
    svg: Svg,
    text: str,
    x: int,
    y: int,
    scale: int,
    fill: str,
    atlas: dict[str, list[str]],
) -> None:
    cursor = x
    for ch in text:
        rows = atlas[ch]
        width = len(rows[0])
        for row_index, row in enumerate(rows):
            col = 0
            while col < width:
                if row[col] == "1":
                    start = col
                    while col < width and row[col] == "1":
                        col += 1
                    svg.rect(
                        cursor + start * scale,
                        y + row_index * scale,
                        (col - start) * scale,
                        scale,
                        fill,
                    )
                else:
                    col += 1
        cursor += width * scale


def draw_shadow_text(
    svg: Svg,
    text: str,
    x: int,
    y: int,
    scale: int,
    fill: str,
    shadow: str,
    atlas: dict[str, list[str]],
) -> None:
    draw_text(svg, text, x + scale, y + scale, scale, shadow, atlas)
    draw_text(svg, text, x, y, scale, fill, atlas)


def blit(
    svg: Svg,
    sprite: list[str],
    x: int,
    y: int,
    scale: int,
    colors: dict[str, str],
) -> None:
    width = len(sprite[0])
    for row in sprite:
        if len(row) != width:
            raise ValueError("sprite rows must be the same width")
    for row_index, row in enumerate(sprite):
        col = 0
        while col < width:
            paint = row[col]
            if paint == "." or paint not in colors:
                col += 1
                continue
            start = col
            while col < width and row[col] == paint:
                col += 1
            svg.rect(
                x + start * scale,
                y + row_index * scale,
                (col - start) * scale,
                scale,
                colors[paint],
            )
