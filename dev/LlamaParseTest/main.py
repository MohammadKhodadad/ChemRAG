# File: main.py

import argparse
from utils.llama_parser import batch_parse

def main():
    """
    Entry point for batch parsing PDFs using llama_parser utilities.
    """
    parser = argparse.ArgumentParser(
        description="Batch-parse PDFs using the llama_parser module."
    )
    parser.add_argument(
        "--input_dir",
        default="input_pdfs",  # default input folder name
        help="Path to the directory containing PDF files to parse (default: './pdfs')"
    )
    parser.add_argument(
        "--output_root",
        default="parsed_outputs",  # default output root folder name
        help="Root directory where parsed outputs will be stored (default: './parsed_outputs')"
    )
    args = parser.parse_args()

    # Call the batch_parse function from llama_parser
    batch_parse(args.input_dir, args.output_root)
    print(f"Finished parsing all PDFs from '{args.input_dir}' into '{args.output_root}'.")

if __name__ == "__main__":
    main()
