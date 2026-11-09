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


# 21px glyphs at scale 2. Wide enough for "Was using Pi mostly," and narrow
# enough that "as well" and "as a daily driver." stay on their own lines.
BODY_SCALE = 2
BODY_MAX_W = 328
STACK_CARDS = [
    ("CODE", ["Go", "Node.js", "TypeScript", "Python", "Terraform", "Ansible"]),
    (
        "TOOL",
        [
            "Grok Bot",
            "Herdr",
            "Was using Pi mostly, changed to Grok Bot as a daily driver.",
        ],
    ),
    ("DATA", ["meh"]),
    ("CLOUD", ["AWS", "GCP", "some Chinese cloud as well"]),
]


def wrap_text(text: str, scale: int, max_w: int, atlas: dict) -> list[str]:
    words = text.split(" ")
    lines: list[str] = []
    current = ""
    for word in words:
        trial = word if not current else f"{current} {word}"
        if text_width(trial, scale, atlas) <= max_w:
            current = trial
            continue
        if not current or text_width(word, scale, atlas) > max_w:
            raise SystemExit(f"{word!r} is wider than the card ({max_w}px)")
        lines.append(current)
        current = word
    if current:
        lines.append(current)
    return lines


def card_lines(parts: list[str], atlas: dict) -> list[str]:
    lines: list[str] = []
    for part in parts:
        lines.extend(wrap_text(part, BODY_SCALE, BODY_MAX_W, atlas))
    joined = " ".join(lines)
    source = " ".join(parts)
    if joined != source:
        raise SystemExit(f"wrap changed card text:\n{source}\n{joined}")
    return lines


def mini_card(
    svg: Svg,
    x: int,
    y: int,
    w: int,
    h: int,
    label: str,
    lines: list[str],
    atlas: dict,
) -> None:
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
    body_top = y + 18 + text_height(2, atlas) + 14
    body_bot = y + h - 18
    # One short word keeps the old center-of-card treatment.
    if len(lines) == 1 and text_width(lines[0], 4, atlas) <= w - 64:
        scale = 4
        word_w = text_width(lines[0], scale, atlas)
        word_h = text_height(scale, atlas)
        draw_shadow_text(
            svg,
            lines[0],
            x + (w - word_w) // 2,
            body_top + (body_bot - body_top - word_h) // 2,
            scale,
            PEACH,
            DEEP,
            atlas,
        )
        return
    scale = BODY_SCALE
    gap = 8
    line_h = text_height(scale, atlas)
    block = len(lines) * line_h + (len(lines) - 1) * gap
    room = body_bot - body_top
    if block > room:
        raise SystemExit(f"{label} needs {block}px of card face, only {room}px free")
    cursor = body_top + (room - block) // 2
    for line in lines:
        line_w = text_width(line, scale, atlas)
        if line_w > BODY_MAX_W:
            raise SystemExit(f"{label} line {line!r} is {line_w}px")
        draw_text(svg, line, x + (w - line_w) // 2, cursor, scale, CREAM, atlas)
        cursor += line_h + gap


def write_stack(atlas: dict) -> None:
    prepared = [(label, card_lines(parts, atlas)) for label, parts in STACK_CARDS]
    line_h = text_height(BODY_SCALE, atlas)
    gap_line = 8
    max_lines = max(len(lines) for _, lines in prepared)
    block = max_lines * line_h + (max_lines - 1) * gap_line
    card_w = BODY_MAX_W + 72
    card_h = 18 + text_height(2, atlas) + 14 + block + 18
    gap = 16
    origin_x = (W - (card_w * 2 + gap)) // 2
    origin_y = 108
    height = origin_y + card_h * 2 + gap + 24
    svg = Svg(W, height)
    chrome(svg)
    blit(svg, GEM, 32, 28, 3, SPRITE_COLORS)
    draw_shadow_text(svg, "TECH STACK", 32 + len(GEM[0]) * 3 + 16, 34, 3, CREAM, DEEP, atlas)
    for index, (label, lines) in enumerate(prepared):
        col = index % 2
        row = index // 2
        mini_card(
            svg,
            origin_x + col * (card_w + gap),
            origin_y + row * (card_h + gap),
            card_w,
            card_h,
            label,
            lines,
            atlas,
        )
    svg.save(OUT / "stack.svg", "Tech stack trading cards")


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
    line = "DABBLING IN TECH"
    title_h = text_height(4, atlas)
    line_h = text_height(2, atlas)
    gap = 16
    top = (height - (title_h + gap + line_h)) // 2
    title_w = text_width(title, 4, atlas)
    draw_shadow_text(svg, title, (W - title_w) // 2, top, 4, PEACH, DEEP, atlas)
    line_w = text_width(line, 2, atlas)
    draw_text(svg, line, (W - line_w) // 2, top + title_h + gap, 2, CREAM, atlas)
    svg.save(OUT / "footer.svg", "PDAWGY. Dabbling in tech.")


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
