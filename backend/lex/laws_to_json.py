#!/usr/bin/env python3
from pathlib import Path
from typing import Any
from urllib.request import urlopen
import json
import logging
import re
import tempfile
import xml.etree.ElementTree as ET
import zipfile


def fetch_law_xml(law_code: str) -> Path:
    # Download and extract zip file
    with urlopen(f"https://www.gesetze-im-internet.de/{law_code}/xml.zip", timeout=10) as r:
        data = r.read()

    with tempfile.TemporaryDirectory() as td:
        zpath = Path(td) / "dl.zip"
        zpath.write_bytes(data)
        with zipfile.ZipFile(zpath) as zf:
            name = next(n for n in zf.namelist() if n.lower().endswith(".xml"))
            xml_file_contents = zf.read(name)

    # Find the first <norm> element, and use its builddate attribute as the file name
    norm = ET.fromstring(xml_file_contents).find(".//norm")
    if len(norm) == 0 or not (build_date := norm.get("builddate")):
        raise ValueError("Invalid document format. Norm does not exist, or has no builddate attribute")

    law_dir = Path(law_code)
    law_dir.mkdir(exist_ok=True)
    law_path = law_dir / f"{build_date}.xml"
    if law_path.exists():
        raise FileExistsError

    law_path.write_bytes(xml_file_contents)
    return law_path


ignored_paragraphs = ("Inhaltsübersicht",)


def parse_paragraph(norm: ET.Element):
    if (
        norm.get("doknr") is None
        or (paragraph_name_node := norm.find("metadaten/enbez")) is None
        or (paragraph_name := paragraph_name_node.text.strip()) in ignored_paragraphs
    ):
        return

    try:
        parsed_paragraph_name = re.search(r"§\s*([\d]+[a-z]?)", paragraph_name).group(1)
    except AttributeError:
        logging.error(f"Can't parse paragraph name: '{paragraph_name}'")

    return {
        "full_name": paragraph_name,
        "name": parsed_paragraph_name,
        "title": getattr(norm.find("metadaten/titel"), "text", None),
        "doknr": norm.get("doknr"),
        "text": getattr(norm.find("textdaten/text/Content"), "text", None),
        "footnotes": getattr(norm.find("textdaten/fussnoten/Content"), "text", None),
    }


def parse_paragraphs(xml: ET.Element) -> dict[str, dict[str, Any]]:
    xml_paragraphs = [n for n in xml.findall(".//norm")]
    return {n["name"]: n for n in map(parse_paragraph, xml_paragraphs) if n}


def parse_law(law_code):
    xml = ET.fromstring(sorted(Path(law_code).glob("*.xml"))[-1].read_bytes())
    return {
        "name": xml.find("norm/metadaten/jurabk").text.strip(),
        "paragraphs": parse_paragraphs(xml),
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Monitor German law XML files.")
    parser.add_argument(
        "laws",
        nargs="+",
        help="List of law short names (e.g., bgb, aufenthg_2004)",
    )
    args = parser.parse_args()

    for law_code in args.laws:
        # try:
        #     fetch_law_xml(law_code)
        # except FileExistsError:
        #     logging.debug(f"{law_code} has not changed; file already exists")

        print(json.dumps(parse_law(law_code), indent=4))
