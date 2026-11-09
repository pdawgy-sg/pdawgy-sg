"""Outline Press Start 2P into the profile SVG cards."""

from __future__ import annotations

import json
from pathlib import Path

from pixels import Svg, blit, draw_shadow_text, draw_text, load_atlas, text_height, text_width

ROOT = Path(__file__).resolve().parents[1]
ATLAS_PATH = ROOT / "scripts" / "glyphs.json"
FONT_PATH = ROOT / "fonts" / "PressStart2P-Regular.ttf"
OUT = ROOT / "assets"

W = 880
BG = "#1e1f29"
PANEL = "#282a36"
PURPLE = "#bd93f9"
PEACH = "#d5a195"
CREAM = "#f3cfe0"
BLUE = "#60aeff"
DEEP = "#211652"
INK = "#14141f"

GEM = [
    "....p....",
    "...pbp...",
    "..pbdbp..",
    ".pbdddbp.",
    "..pbdbp..",
    "...pbp...",
    "....p....",
]
SWORD = [
    "...bb...",
    "...bb...",
    "...bb...",
    "...bb...",
    "...bb...",
    "...bb...",
    "bbbbbbbb",
    "...pp...",
    "..pppp..",
]
CROWN = [
    "h..h..h..h..",
    "hhhhhhhhhhhh",
    "hh.pp.pp.hh.",
    "hhhhhhhhhhhh",
    ".hhhhhhhhhh.",
    "..pppppppp..",
]
ROBOT = [
    "......bbb.......",
    ".....bbbbb......",
    "......bbb.......",
    "....oooooooo....",
    "...oppppppppo...",
    "..opccccccccpo..",
    "..opcbbppbbcpo..",
    "..opcbbppbbcpo..",
    "..opccccccccpo..",
    "..oppphhhppppo..",
    "..opphhhhhpppo..",
    "...oppppppppo...",
    "....oooooooo....",
    "...oppppppppo...",
    "..oppppppppppo..",
    "..opkkppppkkpo..",
    "..oppppppppppo..",
    "..opbbbbbbbbpo..",
    "...oooooooooo...",
    "....oo....oo....",
    "....oo....oo....",
]
SPRITE_COLORS = {
    "p": PURPLE,
    "b": BLUE,
    "c": CREAM,
    "d": "#f8f8f2",
    "h": PEACH,
    "o": INK,
    "k": DEEP,
}


def build_atlas(font_path: Path) -> dict:
    from PIL import Image, ImageDraw, ImageFont

    font = ImageFont.truetype(str(font_path), 8)
    glyphs: dict[str, list[str]] = {}
    for code in range(32, 127):
        ch = chr(code)
        advance = int(round(font.getlength(ch))) or 8
        canvas = Image.new("1", (advance + 8, 16), 0)
        ImageDraw.Draw(canvas).text((0, 0), ch, font=font, fill=1)
        bbox = canvas.getbbox()
        if bbox and (bbox[0] < 0 or bbox[1] < 0 or bbox[2] > advance or bbox[3] > 8):
            raise SystemExit(f"glyph {ch!r} bbox {bbox} does not fit advance {advance}")
        glyphs[ch] = [
            "".join("1" if canvas.getpixel((x, y)) else "0" for x in range(advance))
            for y in range(8)
        ]
    return {
        "font": "Press Start 2P",
        "license": "SIL Open Font License 1.1",
        "size": 8,
        "glyphs": {ch: glyphs[ch] for ch in sorted(glyphs, key=ord)},
    }


def chrome(svg: Svg, inset: int = 8) -> None:
    svg.rect(0, 0, svg.width, svg.height, BG)
    x, y = inset, inset
    cw, ch = svg.width - inset * 2, svg.height - inset * 2
    svg.rect(x, y, cw, ch, PANEL)
    border = 4
    svg.rect(x, y, cw, border, PURPLE)
    svg.rect(x, y + ch - border, cw, border, PURPLE)
    svg.rect(x, y, border, ch, PURPLE)
    svg.rect(x + cw - border, y, border, ch, PURPLE)
    corner = 10
    for cx, cy in (
        (x, y),
        (x + cw - corner, y),
        (x, y + ch - corner),
        (x + cw - corner, y + ch - corner),
    ):
        svg.rect(cx, cy, corner, corner, PEACH)
    ix, iy = x + 10, y + 10
    iw, ih = cw - 20, ch - 20
    hair = 2
    svg.rect(ix, iy, iw, hair, BLUE)
    svg.rect(ix, iy + ih - hair, iw, hair, BLUE)
    svg.rect(ix, iy, hair, ih, BLUE)
    svg.rect(ix + iw - hair, iy, hair, ih, BLUE)


def divider(name: str, title: str, icon: list[str], atlas: dict) -> None:
    height = 112
    svg = Svg(W, height)
    chrome(svg)
    scale = 3
    icon_h = len(icon) * scale
    icon_y = (height - icon_h) // 2
    blit(svg, icon, 32, icon_y, scale, SPRITE_COLORS)
    size = 3
    label_h = text_height(size, atlas)
    label_y = (height - label_h) // 2
    draw_shadow_text(svg, title, 32 + len(icon[0]) * scale + 16, label_y, size, CREAM, DEEP, atlas)
    badge = "??"
    badge_scale = 2
    badge_w = text_width(badge, badge_scale, atlas)
    pad = 10
    box_w = badge_w + pad * 2
    box_h = text_height(badge_scale, atlas) + pad
    box_x = W - 36 - box_w
    box_y = (height - box_h) // 2
    svg.rect(box_x, box_y, box_w, box_h, PEACH)
    draw_text(svg, badge, box_x + pad, box_y + pad // 2, badge_scale, INK, atlas)
    svg.save(OUT / name, title)


def mini_card(svg: Svg, x: int, y: int, w: int, h: int, label: str, atlas: dict) -> None:
    svg.rect(x, y, w, h, BG)
    svg.rect(x + 4, y + 4, w - 8, h - 8, PANEL)
    svg.rect(x + 4, y + 4, w - 8, 3, PURPLE)
    svg.rect(x + 4, y + h - 7, w - 8, 3, PURPLE)
    svg.rect(x + 4, y + 4, 3, h - 8, PURPLE)
    svg.rect(x + w - 7, y + 4, 3, h - 8, PURPLE)
    for cx, cy in ((x + 4, y + 4), (x + w - 12, y + 4), (x + 4, y + h - 12), (x + w - 12, y + h - 12)):
        svg.rect(cx, cy, 8, 8, PEACH)
    label_w = text_width(label, 2, atlas)
    draw_text(svg, label, x + (w - label_w) // 2, y + 18, 2, BLUE, atlas)
    mark = "??"
    mark_w = text_width(mark, 4, atlas)
    draw_shadow_text(svg, mark, x + (w - mark_w) // 2, y + 48, 4, PEACH, DEEP, atlas)
    left = "ATK ??"
    right = "DEF ??"
    draw_text(svg, left, x + 16, y + h - 28, 1, CREAM, atlas)
    right_w = text_width(right, 1, atlas)
    draw_text(svg, right, x + w - 16 - right_w, y + h - 28, 1, CREAM, atlas)


def write_stack(atlas: dict) -> None:
    height = 292
    svg = Svg(W, height)
    chrome(svg)
    blit(svg, GEM, 32, 28, 3, SPRITE_COLORS)
    draw_shadow_text(svg, "TECH STACK", 32 + len(GEM[0]) * 3 + 16, 34, 3, CREAM, DEEP, atlas)
    note = "PLACEHOLDER CARDS"
    note_w = text_width(note, 1, atlas)
    draw_text(svg, note, W - 36 - note_w, 46, 1, PEACH, atlas)
    labels = ["CODE", "TOOL", "DATA", "CLOUD"]
    gap = 16
    card_w = 196
    card_h = 148
    row_w = len(labels) * card_w + (len(labels) - 1) * gap
    origin_x = (W - row_w) // 2
    for index, label in enumerate(labels):
        mini_card(svg, origin_x + index * (card_w + gap), 112, card_w, card_h, label, atlas)
    svg.save(OUT / "stack.svg", "Placeholder tech stack cards")


def write_bonus(atlas: dict) -> None:
    height = 300
    svg = Svg(W, height)
    chrome(svg)
    draw_shadow_text(svg, "BONUS STAGE", 36, 28, 3, CREAM, DEEP, atlas)
    blit(svg, ROBOT, 44, 86, 6, SPRITE_COLORS)
    blit(svg, GEM, 780, 28, 3, SPRITE_COLORS)
    lines = ["THIS PLAYER", "LOVES", "GROK BOT"]
    y = 100
    for line in lines:
        draw_shadow_text(svg, line, 180, y, 3, PEACH if line == "GROK BOT" else CREAM, DEEP, atlas)
        y += text_height(3, atlas) + 12
    draw_text(svg, "BEEP BOOP", 180, y + 4, 2, BLUE, atlas)
    svg.save(OUT / "bonus.svg", "Bonus stage. This player loves Grok Bot.")


def write_footer(atlas: dict) -> None:
    height = 196
    svg = Svg(W, height)
    chrome(svg)
    title = "PDAWGY"
    title_w = text_width(title, 4, atlas)
    draw_shadow_text(svg, title, (W - title_w) // 2, 36, 4, PEACH, DEEP, atlas)
    line = "DABBLING IN TECH"
    line_w = text_width(line, 2, atlas)
    draw_text(svg, line, (W - line_w) // 2, 86, 2, CREAM, atlas)
    hint = "FILL IN THE BRACKETS BELOW"
    hint_w = text_width(hint, 1, atlas)
    draw_text(svg, hint, (W - hint_w) // 2, 124, 1, BLUE, atlas)
    svg.save(OUT / "footer.svg", "PDAWGY footer")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    if FONT_PATH.exists():
        payload = build_atlas(FONT_PATH)
        ATLAS_PATH.write_text(json.dumps(payload, indent=2) + "\n")
        atlas = payload["glyphs"]
    else:
        atlas = load_atlas(ATLAS_PATH)
    divider("about.svg", "ABOUT", CROWN, atlas)
    divider("now.svg", "NOW DABBLING", SWORD, atlas)
    write_stack(atlas)
    write_bonus(atlas)
    write_footer(atlas)


if __name__ == "__main__":
    main()
