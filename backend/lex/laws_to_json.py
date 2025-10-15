#!/usr/bin/env python3
from copy import deepcopy
from pathlib import Path
from typing import Any
from urllib.request import urlopen
import json
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
REPEALED_MARKER = "(weggefallen)"


def parse_paragraph_text(element: ET.Element) -> tuple[str | None, dict[str, str]]:
    paragraph_text = deepcopy(element.find("textdaten/text/Content"))

    if paragraph_text is None:  # Can be empty if paragraph is repealed, but not always
        return None, {}

    subsections = {}
    for sub_element in paragraph_text:
        if match := re.match(r"\((\d+[a-z]?)\)( .*)", sub_element.text or ""):
            text = match.group(2).strip()
            repealed = text == REPEALED_MARKER
            subsections[match.group(1)] = {
                "text": None if repealed else text,
                "repealed": repealed
            }
            sub_element.set("data-subsection", match.group(1))

    return "".join(ET.tostring(c, encoding="unicode") for c in paragraph_text), subsections


def is_paragraph_repealed(element: ET.Element):
    repealed_in_title = getattr(element.find("metadaten/titel"), "text", "") == REPEALED_MARKER
    repealed_in_content = getattr(element.find("textdaten/text/Content/P"), "text", "") == REPEALED_MARKER
    return repealed_in_title or repealed_in_content


def parse_paragraph(element: ET.Element):
    if (
        element.get("doknr") is None
        or (paragraph_name_node := element.find("metadaten/enbez")) is None
        or (paragraph_name := getattr(paragraph_name_node, "text", "").strip()) in ignored_paragraphs
        or not paragraph_name
    ):
        return

    match = re.match(r"§\s*([\d]+[a-z]?)", paragraph_name)  # "§ 123a"
    parsed_paragraph_name = match.group(1) if match else paragraph_name  # "§ 123a -> 123a"

    text, subsections = parse_paragraph_text(element)
    repealed = is_paragraph_repealed(element)
    return {
        "full_name": paragraph_name,
        "name": parsed_paragraph_name,
        "title": None if repealed else getattr(element.find("metadaten/titel"), "text", None),
        "repealed": repealed,
        "doknr": element.get("doknr"),
        "text": None if repealed else text,
        "subsections": subsections,
        "footnotes": getattr(element.find("textdaten/fussnoten/Content"), "text", None),
    }


def parse_paragraphs(root: ET.Element) -> dict[str, dict[str, Any]]:
    xml_paragraphs = [n for n in root.findall(".//norm")]
    return {n["name"]: n for n in map(parse_paragraph, xml_paragraphs) if n}


def parse_law(law_code):
    xml = ET.fromstring(sorted(Path(law_code).glob("*.xml"))[-1].read_bytes())
    return {
        "name": getattr(xml.find("norm/metadaten/jurabk"), "text", "").strip(),
        "paragraphs": parse_paragraphs(xml),
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Turn German law XML files into JSON.")
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
