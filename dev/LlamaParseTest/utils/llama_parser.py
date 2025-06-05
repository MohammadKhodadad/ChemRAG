# File: utils/llama_utils.py

import os
import json
import dotenv
from llama_cloud_services import LlamaParse

dotenv.load_dotenv()

def parse_and_store(pdf_path: str, output_dir: str):
    """
    Parse a single PDF with LlamaParse and store all outputs into the specified output directory.
    Creates subdirectories for markdown, text, images, and pages.
    """
    LLAMA_API_KEY = os.environ['LLAMA_API_KEY']
    parser = LlamaParse(
        api_key=LLAMA_API_KEY,
        num_workers=4,
        verbose=True,
        language="en",
    )

    # Parse the PDF
    result = parser.parse(pdf_path)

    # Create necessary subdirectories
    markdown_dir = os.path.join(output_dir, "markdown")
    text_dir = os.path.join(output_dir, "text")
    images_dir = os.path.join(output_dir, "images")
    pages_dir = os.path.join(output_dir, "pages")

    os.makedirs(markdown_dir, exist_ok=True)
    os.makedirs(text_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(pages_dir, exist_ok=True)

    # 1. Save per-page Markdown files
    markdown_documents = result.get_markdown_documents(split_by_page=True)
    for idx, doc in enumerate(markdown_documents, start=1):
        md_content = doc.text if hasattr(doc, 'text') else str(doc)
        with open(os.path.join(markdown_dir, f"page_{idx}.md"), "w", encoding="utf-8") as f:
            f.write(md_content)

    # 2. Save plain text (aggregated or split)
    text_documents = result.get_text_documents(split_by_page=False)
    if len(text_documents) > 1:
        for idx, doc in enumerate(text_documents, start=1):
            txt_content = doc.text if hasattr(doc, 'text') else str(doc)
            with open(os.path.join(text_dir, f"page_{idx}.txt"), "w", encoding="utf-8") as f:
                f.write(txt_content)
    else:
        txt_content = text_documents[0].text if hasattr(text_documents[0], 'text') else str(text_documents[0])
        with open(os.path.join(text_dir, "parsed_text.txt"), "w", encoding="utf-8") as f:
            f.write(txt_content)

    # 3. Download image documents into images_dir
    image_documents = result.get_image_documents(
        include_screenshot_images=True,
        include_object_images=False,
        image_download_dir=images_dir,
    )

    # Save image metadata
    image_metadata = []
    for img_doc in image_documents:
        metadata = {
            "page_number": getattr(img_doc, "page_number", None),
            "image_type": getattr(img_doc, "type", None),
            "local_path": getattr(img_doc, "local_path", None),
            "width": getattr(img_doc, "width", None),
            "height": getattr(img_doc, "height", None),
        }
        image_metadata.append(metadata)

    with open(os.path.join(output_dir, "image_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(image_metadata, f, indent=2)

    # 4. Save per-page structured data
    for idx, page in enumerate(result.pages, start=1):
        page_data = {
            "page_number": idx,
            "text": page.text,
            "markdown": page.md,
            "images": [
                {
                    "type": getattr(img, "type", None),
                    "local_path": getattr(img, "local_path", None),
                    "width": getattr(img, "width", None),
                    "height": getattr(img, "height", None),
                }
                for img in page.images
            ],
            "layout": repr(page.layout),
            "structuredData": repr(page.structuredData),
        }
        with open(os.path.join(pages_dir, f"page_{idx}_data.json"), "w", encoding="utf-8") as f:
            json.dump(page_data, f, indent=2)


def batch_parse(input_dir: str, output_root: str):
    """
    For every PDF in `input_dir`, create a corresponding subdirectory under `output_root`
    and run `parse_and_store`. Skip any file whose output folder already exists.
    """
    for filename in os.listdir(input_dir):
        if not filename.lower().endswith(".pdf"):
            continue
        try:
            name_without_ext = os.path.splitext(filename)[0]
            output_dir = os.path.join(output_root, name_without_ext)

            # Skip if we've already created this output folder (i.e., it likely ran before)
            if os.path.isdir(output_dir) and os.listdir(output_dir):
                print(f"Skipping '{filename}' (output folder already exists).")
                continue

            os.makedirs(output_dir, exist_ok=True)
            parse_and_store(os.path.join(input_dir, filename), output_dir)
        except Exception as e:
            print(f"Error with {filename}:\n{e}")

# ----------------------------------------------
# Example usage (if this file is run directly):
# ----------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Batch-parse PDFs using LlamaParse")
    parser.add_argument("--input_dir", required=True, help="Directory containing PDF files to parse")
    parser.add_argument("--output_root", required=True, help="Root directory where outputs will be stored")
    args = parser.parse_args()

    batch_parse(args.input_dir, args.output_root)

