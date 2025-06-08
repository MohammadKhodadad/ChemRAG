# rag_reranker.py

import os
from glob import glob
from typing import List, Tuple
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
# Use updated embeddings from langchain-openai
from langchain_openai import OpenAIEmbeddings
from langchain.retrievers import ContextualCompressionRetriever
from langchain.chat_models import ChatOpenAI
from langchain.schema import Document, SystemMessage, HumanMessage
from langchain_community.document_compressors import FlashrankRerank


class RagReranker:
    """
    A RAG wrapper with FlashRank reranking over Markdown files.
    Automatically loads an existing FAISS index from `<docs_dir>/.idx` if valid;
    otherwise builds the index from all `.md` files under `docs_dir`.
    Provides methods to answer queries and share the source documents used.
    """

    def __init__(
        self,
        docs_dir: str,
        embedding_model: str = "text-embedding-ada-002",
        llm_model: str = "gpt-3.5-turbo",
        k: int = 20,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        self.docs_dir = docs_dir
        self.index_dir = os.path.join('./', ".idx")
        self.embedding_model = embedding_model
        self.llm_model = llm_model
        self.k = k
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Prepare embeddings
        self.embedding = OpenAIEmbeddings(model=embedding_model)

        # Paths for index files
        faiss_path = os.path.join(self.index_dir, "index.faiss")
        pkl_path = os.path.join(self.index_dir, "index.pkl")
        has_valid_index = os.path.isdir(self.index_dir) and os.path.isfile(faiss_path) and os.path.isfile(pkl_path)

        if has_valid_index:
            # Load existing index
            self.vectorstore = FAISS.load_local(
                self.index_dir,
                self.embedding,
                allow_dangerous_deserialization=True
            )
        else:
            # Build index from Markdown files
            docs: List[Document] = []
            pattern = os.path.join(docs_dir, "**", "*.md")
            for path in glob(pattern, recursive=True):
                if os.path.isfile(path):
                    try:
                        loader = TextLoader(path, encoding="utf-8")
                        loaded = loader.load()
                        for doc in loaded:
                            doc.metadata["source"] = path
                        docs.extend(loaded)
                    except Exception as e:
                        print(f"Warning: failed to load {path}: {e}")

            if not docs:
                raise ValueError(f"No Markdown documents found under {docs_dir}")

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )
            texts = splitter.split_documents(docs)

            if not texts:
                raise ValueError("No text chunks created; check chunk_size and chunk_overlap values.")

            self.vectorstore = FAISS.from_documents(texts, self.embedding)
            os.makedirs(self.index_dir, exist_ok=True)
            self.vectorstore.save_local(self.index_dir)

        # Setup retriever + reranker
        base_retriever = self.vectorstore.as_retriever(search_kwargs={"k": self.k})
        reranker = FlashrankRerank()
        self.retriever = ContextualCompressionRetriever(
            base_retriever=base_retriever,
            base_compressor=reranker
        )

        # LLM
        self.llm = ChatOpenAI(model_name=llm_model, temperature=0.0)

    def get_reranked(self, query: str) -> List[Document]:
        """
        Retrieve and rerank top-k documents for the query.
        Returns a list of Document objects.
        """
        return self.retriever.invoke(query)

    def answer_with_sources(self, query: str) -> Tuple[str, List[str]]:
        """
        Answer the query by retrieving, reranking, and passing context to the LLM.
        Returns a tuple of (answer_text, list_of_source_paths).
        """
        docs = self.get_reranked(query)
        context = "\n\n".join(d.page_content for d in docs)

        # Strict system prompt
        messages = [
            SystemMessage(
                content=(
                    "You are a helpful assistant. "
                    "Answer the question using ONLY the following context. "
                    "Do NOT use any external knowledge or assumptions beyond the context provided."
                )
            ),
            HumanMessage(content=f"Context:\n{context}\n\nQuestion: {query}"),
        ]
        resp = self.llm(messages)
        sources = [doc.metadata.get("source", "") for doc in docs]
        return resp.content, sources