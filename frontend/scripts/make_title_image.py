#!/usr/bin/env python3
"""Generate an entry image with a given title."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from extensions.renderers.entry_images import make_cover_image

templates_path = Path(__file__).parent.parent / "templates"

parser = argparse.ArgumentParser(description="Generate an entry image")
parser.add_argument("title", help="Title text to render on the image")
parser.add_argument("output", help="Output path for the PNG file")
args = parser.parse_args()

output_path = Path(args.output)
output_path.parent.mkdir(parents=True, exist_ok=True)

image = make_cover_image(args.title, templates_path)
image.save(output_path, optimize=True)
print(f"Saved {output_path}")
