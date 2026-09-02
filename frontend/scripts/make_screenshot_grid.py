#!/usr/bin/env python3

import argparse
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

MAIN = "https://localhost"
SERVICES = "https://services.localhost"

PAGES = [
    ("Home", f"{MAIN}/"),
    ("About", f"{MAIN}/about"),
    ("Contact", f"{MAIN}/contact"),
    ("Terms", f"{MAIN}/terms"),
    ("404", f"{MAIN}/does-not-exist"),
    ("Guides index", f"{MAIN}/guides"),
    ("Guide entry", f"{MAIN}/guides/abmeldung"),
    ("Glossary index", f"{MAIN}/glossary"),
    ("Glossary entry", f"{MAIN}/glossary/Anmeldung"),
    ("Tools index", f"{MAIN}/tools"),
    ("Tool entry", f"{MAIN}/tools/tax-calculator"),
    ("Newsletter index", f"{MAIN}/newsletter"),
    ("Newsletter entry", f"{MAIN}/newsletter/august-2026"),
    ("Forum index", f"{MAIN}/forum"),
    ("Forum thread", f"{MAIN}/forum/1"),
    ("Forum user profile", f"{MAIN}/forum/users/sofia_ramos"),
    ("Forum rules", f"{MAIN}/forum/rules"),
    ("Forum login", f"{MAIN}/forum/login"),
    ("Forum signup", f"{MAIN}/forum/signup"),
    ("Services home", f"{SERVICES}/"),
    ("Services entry", f"{SERVICES}/contact"),
    ("Services health insurance", f"{SERVICES}/health-insurance"),
    ("Services 404", f"{SERVICES}/does-not-exist"),
]

VIEWPORT = {"width": 1300, "height": 800}
COLUMNS = 4
LABEL_HEIGHT = 60
PADDING = 20
BG_COLOR = (30, 30, 30)
LABEL_BG = (245, 245, 245)
LABEL_FG = (20, 20, 20)
LABEL_SUB = (100, 100, 100)


def load_font(size: int):
    for name in ("Arial.ttf", "Helvetica.ttc", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def capture(page, url: str) -> Image.Image:
    page.goto(url, wait_until="networkidle", timeout=30000)
    png = page.screenshot(full_page=False)
    from io import BytesIO

    return Image.open(BytesIO(png)).convert("RGB")


def compose_grid(cells: list[tuple[str, str, Image.Image]]) -> Image.Image:
    cell_w, cell_h = VIEWPORT["width"], VIEWPORT["height"] + LABEL_HEIGHT
    rows = math.ceil(len(cells) / COLUMNS)
    grid_w = COLUMNS * cell_w + (COLUMNS + 1) * PADDING
    grid_h = rows * cell_h + (rows + 1) * PADDING

    grid = Image.new("RGB", (grid_w, grid_h), BG_COLOR)
    draw = ImageDraw.Draw(grid)
    title_font = load_font(28)
    url_font = load_font(20)

    for i, (name, url, img) in enumerate(cells):
        col, row = i % COLUMNS, i // COLUMNS
        x = PADDING + col * (cell_w + PADDING)
        y = PADDING + row * (cell_h + PADDING)

        draw.rectangle([x, y, x + cell_w, y + LABEL_HEIGHT], fill=LABEL_BG)
        draw.text((x + 15, y + 6), name, fill=LABEL_FG, font=title_font)
        draw.text((x + 15, y + 34), url, fill=LABEL_SUB, font=url_font)

        grid.paste(img, (x, y + LABEL_HEIGHT))

    return grid


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "output", nargs="?", default=str(Path.home() / "Downloads" / "page-grid.png"), help="Output PNG path"
    )
    args = parser.parse_args()

    cells: list[tuple[str, str, Image.Image]] = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        context = browser.new_context(
            viewport={"width": VIEWPORT["width"], "height": VIEWPORT["height"]},
            ignore_https_errors=True,
            reduced_motion="reduce",
        )
        page = context.new_page()
        for name, url in PAGES:
            print(f"Capturing {name}: {url}", flush=True)
            try:
                img = capture(page, url)
            except Exception as e:
                print(f"  failed: {e}", file=sys.stderr)
                img = Image.new("RGB", (VIEWPORT["width"], VIEWPORT["height"]), (220, 220, 220))
                ImageDraw.Draw(img).text((20, 20), f"Failed: {e}", fill=(180, 40, 40), font=load_font(24))
            cells.append((name, url, img))
        browser.close()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    grid = compose_grid(cells)
    grid.save(output, optimize=True)
    print(f"Saved {output} ({grid.width}x{grid.height})")


if __name__ == "__main__":
    main()
