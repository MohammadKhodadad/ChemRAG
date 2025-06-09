import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from utils.agent import AgentQA

# Load environment variables from .env
load_dotenv()

# Ensure API key is set
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("Please set the OPENAI_API_KEY environment variable or define it in a .env file")

# Initialize Flask app
app = Flask(__name__)

# Configuration via environment variables
DOCS_DIR = os.getenv("DOCS_DIR", "../DoclingTest/parsed_outputs")
EMBED_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")
AGENT_LLM_MODEL = os.getenv("AGENT_LLM_MODEL", LLM_MODEL)
K = int(os.getenv("K", "20"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# Instantiate AgentQA with retrieval and reasoning capabilities
agent = AgentQA(
    docs_dir=DOCS_DIR,
    embedding_model=EMBED_MODEL,
    llm_model=LLM_MODEL,
    k=K,
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    agent_llm_model=AGENT_LLM_MODEL
)

@app.route("/ask", methods=["POST"])
def ask():
    """
    Ask a question. Expects JSON with:
      - "query": str
      - optional "history": List[{"role": str, "content": str}]
    Uses AgentQA to decide whether to retrieve or answer directly.
    """
    data = request.get_json() or {}
    query = data.get("query")
    history = data.get("history", [])

    if not query:
        return jsonify({"error": "Missing 'query' in request body"}), 400

    try:
        # Pass history through to the agent
        answer, sources = agent.ask(query, history=history)
        return jsonify({
            "answer": answer,
            "sources": sources
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, threaded=True)
