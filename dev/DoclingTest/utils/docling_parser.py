# File: utils/docling_utils.py

import os
from pathlib import Path
from docling.document_converter import DocumentConverter

def parse_and_store(source: str, output_dir: str):
    """
    Parse a single PDF (local path or URL) using Docling, then save its contents
    as Markdown to <output_dir>/markdown/document.md.

    In other words, under each PDF’s output_dir, we now create a "markdown/" folder,
    and write "document.md" inside it.
    """
    converter = DocumentConverter()
    try:
        result = converter.convert(source)
    except Exception as e:
        raise RuntimeError(f"Docling conversion failed for '{source}': {e}")
    doc = result.document

    full_markdown: str = doc.export_to_markdown()

    # Build the path: <output_dir>/markdown/document.md
    markdown_folder = os.path.join(output_dir, "markdown")
    os.makedirs(markdown_folder, exist_ok=True)

    out_path = os.path.join(markdown_folder, "document.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(full_markdown)


def batch_parse(input_dir: str, output_root: str):
    """
    For each PDF in input_dir:
      1) create parsed_outputs/<basename>/
      2) create parsed_outputs/<basename>/markdown/
      3) call parse_and_store(pdf_path, parsed_outputs/<basename>)
      4) inside that folder, the Markdown file is "markdown/document.md"
    """
    os.makedirs(output_root, exist_ok=True)

    for filename in os.listdir(input_dir):
        if not filename.lower().endswith(".pdf"):
            continue

        name_without_ext = os.path.splitext(filename)[0]
        output_dir = os.path.join(output_root, name_without_ext)
        os.makedirs(output_dir, exist_ok=True)

        # If the markdown subfolder already has something inside, skip
        markdown_folder = os.path.join(output_dir, "markdown")
        if os.path.isdir(markdown_folder) and os.listdir(markdown_folder):
            print(f"Skipping '{filename}' (already parsed).")
            continue

        pdf_path = os.path.join(input_dir, filename)
        try:
            parse_and_store(pdf_path, output_dir)
            print(f"Parsed '{filename}' → '{output_dir}/markdown/document.md'")
        except Exception as e:
            print(f"Error parsing '{filename}': {e}")
