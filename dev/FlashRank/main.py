# main.py

import os
import argparse
from dotenv import load_dotenv
from utils.rag_reranker import RagReranker

# Load environment variables from .env if present
load_dotenv()

def main():
    parser = argparse.ArgumentParser(
        description="CLI for RAG retrieval + FlashRank reranking over Markdown files"
    )
    parser.add_argument(
        "--docs",
        type=str,
        default="..\DoclingTest\parsed_outputs",
        help="Path to the root directory containing Markdown files"
    )
    parser.add_argument(
        "--query",
        type=str,
        required=True,
        help="The question you want to answer"
    )
    parser.add_argument(
        "--k",
        type=int,
        default=20,
        help="Number of documents to retrieve before reranking"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1000,
        help="Size of text chunks for splitting"
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=200,
        help="Overlap between chunks for splitting"
    )
    parser.add_argument(
        "--embedding-model",
        type=str,
        default="text-embedding-ada-002",
        help="OpenAI embedding model name"
    )
    parser.add_argument(
        "--llm-model",
        type=str,
        default="gpt-3.5-turbo",
        help="OpenAI chat model name"
    )
    args = parser.parse_args()

    # Ensure API key is available
    if not os.getenv("OPENAI_API_KEY"):
        parser.error("Please set the OPENAI_API_KEY environment variable or define it in a .env file")

    # Initialize RAG reranker (auto-loads or builds index)
    rag = RagReranker(
        docs_dir=args.docs,
        embedding_model=args.embedding_model,
        llm_model=args.llm_model,
        k=args.k,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )

    print("Retrieving, reranking, and answering…")
    answer, sources = rag.answer_with_sources(args.query)

    print("=== ANSWER ===")
    print(answer)
    print("=== SOURCES ===")
    for src in sources:
        print(f"- {src}")

if __name__ == "__main__":
    main()