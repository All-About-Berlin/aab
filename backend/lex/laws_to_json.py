#!/usr/bin/env python3
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from slugify import slugify
from shutil import copy2
import json
import logging
import re
import requests
import tempfile
import xml.etree.ElementTree as ET
import zipfile


def date_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def fetch_law_xml(opener: requests.Session, law_url: str) -> bytes:
    # Download and extract the zip file containing the law XML file
    zip_response = opener.get(law_url).content

    with tempfile.TemporaryDirectory() as td:
        zpath = Path(td) / "dl.zip"
        zpath.write_bytes(zip_response)
        with zipfile.ZipFile(zpath) as zf:
            name = next(n for n in zf.namelist() if n.lower().endswith(".xml"))
            xml_file_contents = zf.read(name)

    return xml_file_contents


REPEALED_MARKER = "(weggefallen)"


def get_law_name(xml_law: ET.Element) -> str:
    amtabk_node = xml_law.find(".//norm/metadaten/amtabk")
    if amtabk_node is not None and amtabk_node.text:
        law_name = str(amtabk_node.text)
    else:
        jurabk_node = xml_law.find(".//norm/metadaten/jurabk")
        if jurabk_node is not None and jurabk_node.text:
            law_name = str(jurabk_node.text)
        else:
            raise ValueError("Could not get law name.")

    return law_name.strip()


def get_law_title(xml_law: ET.Element, long: bool) -> str:
    node_name = "langue" if long else "kurzue"

    node = xml_law.find(f".//norm/metadaten/{node_name}")
    if node is None or not node.text:
        mode = "long" if long else "short"
        raise ValueError(f"Could not get {mode} law title.")

    return node.text.strip()


def parse_paragraph_text(xml_paragraph: ET.Element) -> tuple[str | None, dict[str, str]]:
    """
    Parse and augment the TEXT of a single paragraph. For example, the text of § 21 AufenthG.
    """
    paragraph_text = deepcopy(xml_paragraph.find("textdaten/text/Content"))

    if paragraph_text is None:  # Can be empty if paragraph is repealed, but not always
        return None, {}

    subsections = {}
    for sub_element in paragraph_text:
        if match := re.match(r"\((\d+[a-z]?)\)( .*)", sub_element.text or ""):  # "(1) Law text..."
            text = match.group(2).strip()
            repealed = text == REPEALED_MARKER
            subsections[match.group(1)] = {"text": None if repealed else text, "repealed": repealed}
            sub_element.set("data-subsection", match.group(1))

    return "".join(ET.tostring(c, encoding="unicode") for c in paragraph_text), subsections


def is_paragraph_repealed(xml_paragraph: ET.Element):
    """
    Check if a paragraph is repealed ("weggefallen"). The original data does this in multiple ways.
    """
    repealed_in_title = getattr(xml_paragraph.find("metadaten/titel"), "text", "") == REPEALED_MARKER
    repealed_in_content = getattr(xml_paragraph.find("textdaten/text/Content/P"), "text", "") == REPEALED_MARKER
    return repealed_in_title or repealed_in_content


def parse_paragraph(xml_paragraph: ET.Element, parent_uri: str):
    """
    Parse and augment a single paragraph. For example, § 21 AufenthG.
    """
    if (doknr := xml_paragraph.get("doknr")) is None:
        logging.warning(f"Ignoring paragraph with no doknr (in {parent_uri})")
        return
    elif (paragraph_name_node := xml_paragraph.find("metadaten/enbez")) is None:
        # If it has a <gliederungseinheit> element, it's an outline node. Those are expected.
        if xml_paragraph.find(".//metadaten/gliederungseinheit") is None:
            logging.warning(f"Ignoring paragraph with no metadaten/enbez (in {parent_uri}/{doknr})")
        return
    elif not (paragraph_name := getattr(paragraph_name_node, "text", "").strip()):
        logging.warning(f"Ignoring paragraph with no name (in {parent_uri}/{doknr})")
        return

    # Rename paragraphs like "§ 123a" or "Art 123a" to "123a"
    if match := re.match(r"(§|Art)\s*([\d]+[a-z]?)", paragraph_name):
        parsed_paragraph_name = match.group(2)

    # Rename paragraph ranges like "(XXXX) §§ 15 bis 16", or "Art 15 und Art 16" to "15-16"
    elif match := re.match(
        r"(?:(?:\(XXXX\) ?)?(?:§{1,2}|Art)) (\d+[a-z]?) (?:bis|und|u\.) (?:(?:§{1,2}|Art) )?(\d+[a-z]?)", paragraph_name
    ):
        parsed_paragraph_name = f"{match.group(1)}-{match.group(2)}"

    else:
        if not (
            paragraph_name.startswith(("Anlage", "Anhang"))
            or paragraph_name
            in ("(XXXX)", "Eingangsformel", "Inhaltsübersicht", "Inhaltsverzeichnis", "Schlussformel", "Schlußformel")
        ):
            logging.warning(f"Unexpected paragraph name: {paragraph_name}")
        parsed_paragraph_name = paragraph_name.strip()

    text, subsections = parse_paragraph_text(xml_paragraph)
    repealed = is_paragraph_repealed(xml_paragraph)
    paragraph_id = slugify(parsed_paragraph_name)

    return {
        "uri": f"{parent_uri}/{paragraph_id}",
        "id": paragraph_id,
        "name": paragraph_name,
        "title": None if repealed else getattr(xml_paragraph.find("metadaten/titel"), "text", None),
        "repealed": repealed,
        "doknr": doknr,
        "text": None if repealed else text,
        "subsections": subsections,
        "footnotes": getattr(xml_paragraph.find("textdaten/fussnoten/Content"), "text", None),
    }


def parse_law(xml_law: ET.Element):
    name = get_law_name(xml_law)
    law_id = slugify(name)
    parsed_paragraphs = [parse_paragraph(xml_paragraph, law_id) for xml_paragraph in xml_law.findall(".//norm")]

    return {
        "uri": law_id,
        "id": law_id,
        "name": name,
        "title": get_law_title(xml_law, long=True),
        "short_title": get_law_title(xml_law, long=False),
        "doknr": xml_law.get("doknr"),
        "date_built": datetime.strptime(str(xml_law.get("builddate")), "%Y%m%d%H%M%S"),
        "paragraphs": {p["id"]: p for p in parsed_paragraphs if p},
    }


def polite_but_persistent_opener(
    retries=5,
    backoff_factor=10,
    status_forcelist=(500, 502, 504),
    session=None,
) -> requests.Session:
    """
    Opens URLs slowly, retries until successful
    """
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


if __name__ == "__main__":
    logging.basicConfig(
        datefmt="%Y-%m-%d %H:%M:%S",
        format="%(asctime)s %(levelname)s [%(name)s:%(lineno)d] %(message)s",
        level=logging.INFO,
    )

    import argparse

    parser = argparse.ArgumentParser(description="Turn German law XML files into JSON.")
    parser.add_argument(
        "--downloads-path",
        dest="downloads_path",
        nargs="?",
        type=Path,
        help="Path where files are downloaded before being parsed.",
        default=Path("./lex/downloads"),
    )
    parser.add_argument(
        "-o",
        "--output-path",
        dest="output_path",
        nargs="?",
        type=Path,
        help="Path where the API files are saved.",
        default=Path("./lex/output"),
    )
    parser.add_argument(
        "laws",
        type=str,
        nargs="*",
        help="List of law short names (e.g., bgb, aufenthg_2004)",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Format the JSON output",
    )
    args = parser.parse_args()

    opener = polite_but_persistent_opener()

    law_urls: list[str] = []
    if args.laws:
        law_urls = [f"https://www.gesetze-im-internet.de/{law_code}/xml.zip" for law_code in args.laws]
    else:
        logging.debug("No laws specified. Fetching all laws.")
        xml_response = opener.get("https://www.gesetze-im-internet.de/gii-toc.xml")
        law_urls = [str(link.text) for link in ET.fromstring(xml_response.content).findall(".//item/link") if link.text]

    for law_url in law_urls:
        logging.info(f"Fetching {law_url}")
        xml_file_contents = fetch_law_xml(opener, law_url)

        logging.info(f"Parsing {law_url}")
        xml_law = ET.fromstring(xml_file_contents)
        parsed_law = parse_law(xml_law)

        build_date_str = parsed_law["date_built"].isoformat()[0:10]

        xml_path = args.downloads_path / parsed_law["id"] / f"{build_date_str}.xml"
        xml_path.parent.mkdir(parents=True, exist_ok=True)
        xml_path.write_bytes(xml_file_contents)

        # Save to {date}.json, copy to latest.json
        json_path = args.output_path / parsed_law["id"] / f"{build_date_str}.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(parsed_law, default=date_serializer, indent=4 if args.pretty else None))
        copy2(json_path, json_path.with_stem("latest"))

        logging.info(f"Parsed {law_url} ({parsed_law['name']}). Saved to '{str(json_path)}'.")
