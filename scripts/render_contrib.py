"""Render the public contribution graph as a Dracula-navy SVG.

Uses the public profile calendar only, so private activity stays off the README.
GITHUB_TOKEN is accepted and unused; the job needs no other secrets.
"""

from __future__ import annotations

import os
import re
import urllib.request
from pathlib import Path

from pixels import Svg, draw_shadow_text, draw_text, load_atlas, text_height, text_width

ROOT = Path(__file__).resolve().parents[1]
ATLAS_PATH = ROOT / "scripts" / "glyphs.json"
OUT = ROOT / "assets" / "contrib.svg"

W = 880
BG = "#1e1f29"
PANEL = "#282a36"
PURPLE = "#bd93f9"
PEACH = "#d5a195"
CREAM = "#f3cfe0"
BLUE = "#60aeff"
DEEP = "#211652"
LEVELS = {
    0: "#282a36",
    1: "#4c3a78",
    2: "#7d5cb8",
    3: "#bd93f9",
    4: "#d5a195",
}
MONTHS = ["", "JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]


def fetch_calendar(login: str) -> list[dict]:
    request = urllib.request.Request(
        f"https://github.com/users/{login}/contributions",
        headers={"User-Agent": "pdawgy-profile-readme"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        html = response.read().decode("utf-8", "replace")
    cells = re.findall(r"<td\b[^>]*ContributionCalendar-day[^>]*>", html)
    tips = dict(
        re.findall(
            r'<tool-tip\b[^>]*\bfor="(contribution-day-component-\d+-\d+)"[^>]*>\s*([^<]+)',
            html,
        )
    )
    days = []
    for tag in cells:
        date = re.search(r'data-date="(\d{4}-\d{2}-\d{2})"', tag)
        level = re.search(r'data-level="(\d+)"', tag)
        ident = re.search(r'id="(contribution-day-component-(\d+)-(\d+))"', tag)
        if not (date and level and ident):
            continue
        tip = tips.get(ident.group(1), "").strip()
        if tip.lower().startswith("no contribution"):
            count = 0
        else:
            matched = re.match(r"(\d+)\s+contribution", tip, re.I)
            if not matched:
                raise SystemExit(f"could not read contribution count from {tip!r}")
            count = int(matched.group(1))
        days.append(
            {
                "date": date.group(1),
                "level": int(level.group(1)),
                "row": int(ident.group(2)),
                "col": int(ident.group(3)),
                "count": count,
            }
        )
    if not days:
        raise SystemExit("public contribution calendar was empty")
    return days


def chrome(svg: Svg) -> None:
    inset = 8
    svg.rect(0, 0, svg.width, svg.height, BG)
    svg.rect(inset, inset, svg.width - 16, svg.height - 16, PANEL)
    border = 4
    x, y = inset, inset
    cw, ch = svg.width - 16, svg.height - 16
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


def render(days: list[dict], atlas: dict) -> Svg:
    rows = max(day["row"] for day in days) + 1
    cols = max(day["col"] for day in days) + 1
    cell = 11
    gap = 3
    step = cell + gap
    grid_w = cols * step - gap
    grid_h = rows * step - gap
    height = 248
    svg = Svg(W, height)
    chrome(svg)
    atlas_h = text_height(2, atlas)
    draw_shadow_text(svg, "LAST 12 MONTHS", 32, 28, 2, CREAM, DEEP, atlas)
    total = sum(day["count"] for day in days)
    total_label = f"TOTAL {total}"
    total_w = text_width(total_label, 2, atlas)
    draw_text(svg, total_label, W - 32 - total_w, 28 + atlas_h - text_height(2, atlas), 2, PEACH, atlas)

    grid_x = (W - grid_w) // 2
    month_y = 64
    grid_y = 80
    columns: list[list[dict | None]] = [[None] * rows for _ in range(cols)]
    for day in days:
        columns[day["col"]][day["row"]] = day

    last_end = -999
    last_month = None
    for col, column in enumerate(columns):
        present = [day for day in column if day]
        if not present:
            continue
        month = int(present[0]["date"][5:7])
        if month == last_month:
            continue
        label = MONTHS[month]
        label_x = grid_x + col * step
        label_w = text_width(label, 1, atlas)
        if label_x < last_end + 4:
            continue
        draw_text(svg, label, label_x, month_y, 1, BLUE, atlas)
        last_end = label_x + label_w
        last_month = month

    well_x = grid_x - 4
    well_y = grid_y - 4
    svg.rect(well_x, well_y, grid_w + 8, grid_h + 8, BG)
    for day in days:
        color = LEVELS.get(day["level"], LEVELS[0])
        svg.rect(grid_x + day["col"] * step, grid_y + day["row"] * step, cell, cell, color)

    legend = ["NONE", "LOW", "MID", "HIGH", "PEAK"]
    item_w = 12 + 8 + 8 * 4 + 10
    legend_w = len(legend) * item_w
    legend_x = (W - legend_w) // 2
    legend_y = grid_y + grid_h + 18
    for index, name in enumerate(legend):
        x = legend_x + index * item_w
        svg.rect(x, legend_y, 12, 12, BG)
        svg.rect(x + 1, legend_y + 1, 10, 10, LEVELS[index])
        draw_text(svg, name, x + 16, legend_y + 2, 1, CREAM, atlas)
    return svg


def main() -> None:
    login = os.environ.get("GH_LOGIN", "pdawgy-sg")
    days = fetch_calendar(login)
    atlas = load_atlas(ATLAS_PATH)
    svg = render(days, atlas)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    total = sum(day["count"] for day in days)
    svg.save(OUT, f"Public GitHub contributions, total {total}")
    print(f"wrote {OUT} days={len(days)} total={total}")


if __name__ == "__main__":
    main()
