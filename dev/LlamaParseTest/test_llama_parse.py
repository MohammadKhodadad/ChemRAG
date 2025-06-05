import os
import json
import dotenv
from llama_cloud_services import LlamaParse

# Load environment variables
dotenv.load_dotenv()
LLAMA_API_KEY = os.environ['LLAMA_API_KEY']

# Initialize parser
parser = LlamaParse(
    api_key=LLAMA_API_KEY,
    num_workers=4,
    verbose=True,
    language="en",
)

# Parse the PDF
result = parser.parse("./test.pdf")

# Create output directories
os.makedirs("output/markdown", exist_ok=True)
os.makedirs("output/text", exist_ok=True)
os.makedirs("output/images", exist_ok=True)
os.makedirs("output/pages", exist_ok=True)

# -- 1. Save markdown documents split by page
markdown_documents = result.get_markdown_documents(split_by_page=True)
for idx, doc in enumerate(markdown_documents, start=1):
    md_content = doc.text if hasattr(doc, 'text') else str(doc)
    with open(f"output/markdown/page_{idx}.md", "w", encoding="utf-8") as f:
        f.write(md_content)

# -- 2. Save text documents (one aggregated or split, depending on configuration)
text_documents = result.get_text_documents(split_by_page=False)
# If multiple docs returned, save each separately; otherwise save the single aggregated text.
if len(text_documents) > 1:
    for idx, doc in enumerate(text_documents, start=1):
        txt_content = doc.text if hasattr(doc, 'text') else str(doc)
        with open(f"output/text/page_{idx}.txt", "w", encoding="utf-8") as f:
            f.write(txt_content)
else:
    # Save the aggregated text as one file
    txt_content = text_documents[0].text if hasattr(text_documents[0], 'text') else str(text_documents[0])
    with open("output/text/parsed_text.txt", "w", encoding="utf-8") as f:
        f.write(txt_content)

# -- 3. Download image documents (screenshot and object images)
image_documents = result.get_image_documents(
    include_screenshot_images=True,
    include_object_images=False,
    image_download_dir="output/images",
)
# Note: Images will be downloaded to output/images automatically.

# Optionally, save metadata for each image document
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

with open("output/image_metadata.json", "w", encoding="utf-8") as f:
    json.dump(image_metadata, f, indent=2)

# -- 4. Save per-page structured data (text, markdown, images, layout, structuredData)
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
    with open(f"output/pages/page_{idx}_data.json", "w", encoding="utf-8") as f:
        json.dump(page_data, f, indent=2)

print("All parsed content has been saved under the 'output/' directory.")
