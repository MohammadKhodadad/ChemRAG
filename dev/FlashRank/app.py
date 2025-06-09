# app.py

import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from utils.rag_reranker import RagReranker

# Load environment variables from .env
load_dotenv()

# Ensure API key is set
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("Please set the OPENAI_API_KEY environment variable or define it in a .env file")

# Initialize Flask app
app = Flask(__name__)

# Load or build the index on startup
DOCS_DIR = os.getenv("DOCS_DIR", "..\DoclingTest\parsed_outputs")
EMBED_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
K = int(os.getenv("K", "20"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# Instantiate RagReranker
rag = RagReranker(
    docs_dir=DOCS_DIR,
    embedding_model=EMBED_MODEL,
    llm_model=LLM_MODEL,
    k=K,
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
)

@app.route("/ask", methods=["POST"])
def ask():
    """
    Ask a question. Expects JSON with at least "query": str.
    History should be handled client-side and passed in requests directly to the reranker if needed.
    """
    data = request.get_json() or {}
    query = data.get("query")
    print(data)
    if not query:
        return jsonify({"error": "Missing 'query' in request body"}), 400

    try:
        answer, sources = rag.answer_with_sources(query)
        return jsonify({
            "answer": answer,
            "sources": sources
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, threaded=True)
