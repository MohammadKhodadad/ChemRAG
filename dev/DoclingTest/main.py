# File: main.py

import argparse
from utils.docling_parser import batch_parse  # Updated to use Docling-based parser

def main():
    """
    Entry point for batch parsing PDFs using docling_utils.
    """
    parser = argparse.ArgumentParser(
        description="Batch-parse PDFs using Docling-based utilities."
    )
    parser.add_argument(
        "--input_dir",
        default="input_pdfs",
        help="Path to the directory containing PDF files to parse (default: 'input_pdfs')"
    )
    parser.add_argument(
        "--output_root",
        default="parsed_outputs",
        help="Root directory where parsed outputs will be stored (default: 'parsed_outputs')"
    )
    args = parser.parse_args()

    # Call the batch_parse function from docling_utils
    batch_parse(args.input_dir, args.output_root)
    print(f"Finished parsing all PDFs from '{args.input_dir}' into '{args.output_root}'.")

if __name__ == "__main__":
    main()
