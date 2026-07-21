#!/usr/bin/env python3
"""
tei2json.py — Extract searchable fields from TEI XML into JSON for client-side search.

Output fields match the search.js state/display fields:
  title, displayTitleEnglish, author, fullText, idno, type, persName, placeName

Usage:
    python3 tei2json.py input.xml                    # Single file to stdout
    python3 tei2json.py input.xml -o output.json     # Single file to file
    python3 tei2json.py /path/to/tei/ -o output/     # Directory to directory
    python3 tei2json.py /path/to/tei/ --combined combined.json  # Merge all into one file
"""

import argparse
import json
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {"tei": "http://www.tei-c.org/ns/1.0"}
XML_NS = "http://www.w3.org/XML/1998/namespace"


def text_content(el):
    if el is None:
        return ""
    return " ".join("".join(el.itertext()).split())


def tei_to_json(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()

    header = root.find("tei:teiHeader", NS)
    body = root.find(".//tei:body", NS)
    if header is None or body is None:
        return None

    title_stmt = header.find(".//tei:titleStmt", NS)

    # Titles
    titles = []
    work_uri = ""
    if title_stmt is not None:
        for t in title_stmt.findall("tei:title", NS):
            text = text_content(t)
            if text:
                titles.append(text)
            ref = t.get("ref", "")
            if ref and not work_uri:
                work_uri = ref

    # Authors
    authors = []
    if title_stmt is not None:
        for a in title_stmt.findall("tei:author", NS):
            pn = a.find("tei:persName", NS)
            name = text_content(pn) if pn is not None else text_content(a)
            if name:
                authors.append(name)

    # Editors (translator, creator, etc.)
    editors = []
    if title_stmt is not None:
        for e in title_stmt.findall("tei:editor", NS):
            name = text_content(e)
            role = e.get("role", "")
            if name and role == "translator":
                editors.append(name)

    # Publication URI
    idno = ""
    pub_stmt = header.find(".//tei:publicationStmt", NS)
    if pub_stmt is not None:
        id_el = pub_stmt.find("tei:idno[@type='URI']", NS)
        if id_el is not None:
            idno = (id_el.text or "").strip()
    if not idno and work_uri:
        idno = work_uri

    # Series
    series = []
    for stmt in header.iter(f"{{{NS['tei']}}}seriesStmt"):
        t = text_content(stmt.find("tei:title", NS))
        if t:
            series.append(t)

    # Source
    source = text_content(header.find(".//tei:sourceDesc", NS))

    # Type from div[@type='work']
    doc_type = ""
    for div in body.iter(f"{{{NS['tei']}}}div"):
        dt = div.get("type", "")
        if dt:
            doc_type = dt
            break

    # Persons referenced in body
    person_names = []
    seen_persons = set()
    for el in body.iter(f"{{{NS['tei']}}}persName"):
        name = text_content(el)
        if name and name not in seen_persons:
            seen_persons.add(name)
            person_names.append(name)

    # Places referenced in body
    place_names = []
    seen_places = set()
    for el in body.iter(f"{{{NS['tei']}}}placeName"):
        name = text_content(el)
        if name and name not in seen_places:
            seen_places.add(name)
            place_names.append(name)

    # Headings
    headings = []
    for head in body.iter(f"{{{NS['tei']}}}head"):
        text = text_content(head)
        if text:
            headings.append(text)

    # Full text from body
    full_text = text_content(body)

    # Build display title
    display_title = titles[0] if titles else ""
    if len(titles) > 1:
        display_title = f"{titles[0]} — {titles[1]}"

    doc = {
        "title": titles,
        "displayTitleEnglish": display_title,
        "author": authors,
        "translator": editors,
        "idno": idno,
        "type": doc_type,
        "series": series,
        "source": source,
        "persName": person_names,
        "placeName": place_names,
        "headings": headings,
        "fullText": full_text,
    }

    # Remove empty fields
    return {k: v for k, v in doc.items() if v}


def main():
    parser = argparse.ArgumentParser(description="Extract searchable JSON from TEI XML for client-side search")
    parser.add_argument("input", help="TEI XML file or directory")
    parser.add_argument("-o", "--output", help="Output JSON file or directory")
    parser.add_argument("--combined", help="Merge all records into a single JSON array file")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = parser.parse_args()

    indent = 2 if args.pretty else None
    input_path = Path(args.input)

    if input_path.is_file():
        doc = tei_to_json(input_path)
        if doc is None:
            print(f"Error: Could not parse {input_path}", file=sys.stderr)
            sys.exit(1)
        output = json.dumps(doc, ensure_ascii=False, indent=indent)
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
        else:
            print(output)

    elif input_path.is_dir():
        files = sorted(input_path.glob("*.xml"))
        all_docs = []

        output_dir = Path(args.output) if args.output and not args.combined else None
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)

        for f in files:
            doc = tei_to_json(f)
            if doc is None:
                print(f"Skipping {f.name}: not valid TEI", file=sys.stderr)
                continue
            all_docs.append(doc)
            if output_dir:
                out_file = output_dir / f"{f.stem}.json"
                out_file.write_text(json.dumps(doc, ensure_ascii=False, indent=indent), encoding="utf-8")
                print(f"{f.name} -> {out_file.name}")

        if args.combined:
            combined = json.dumps(all_docs, ensure_ascii=False, indent=indent)
            Path(args.combined).write_text(combined, encoding="utf-8")
            print(f"Combined {len(all_docs)} records -> {args.combined}")
        elif not output_dir:
            print(json.dumps(all_docs, ensure_ascii=False, indent=indent))
    else:
        print(f"Error: {input_path} not found", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
