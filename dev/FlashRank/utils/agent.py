import json
from typing import List, Tuple, Optional

from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
if __name__=="__main__":
    from rag_reranker import RagReranker  # adjust import as needed
else:
    from .rag_reranker import RagReranker  # adjust import as needed

class AgentQA:
    """
    An agentic QA system that uses a core LLM to think and decide when to query the RAG retriever.
    Accepts the same input and returns the same output (answer, sources) as RagReranker.
    """

    def __init__(
        self,
        docs_dir: str,
        embedding_model: str = "text-embedding-ada-002",
        llm_model: str = "gpt-3.5-turbo",
        k: int = 20,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        agent_llm_model: str = "gpt-3.5-turbo"
    ):
        # Initialize RAG reranker for retrieval
        self.rag = RagReranker(
            docs_dir=docs_dir,
            embedding_model=embedding_model,
            llm_model=llm_model,
            k=k,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        # LLM for planning and synthesis
        self.agent_llm = ChatOpenAI(model_name=agent_llm_model, temperature=0.0)

    def ask(
        self,
        question: str,
        history: Optional[List[Tuple[str, str]]] = None
    ) -> Tuple[str, List[str]]:
        """
        Agentic QA: think, decide whether to retrieve documents, and answer.
        - question: the user’s current query.
        - history: optional list of prior (role, content) pairs.
        Returns (answer_text, source_paths).
        """
        history = history or []

        # 1) Planning step: decide direct vs retrieve
        print("STEP 1")
        plan_prompt = [
            SystemMessage(content=(
                "You are an intelligent agent. Given a user question and conversation history, "
                "first decide whether you need to retrieve documents. "
                "Respond *only* with a JSON object: {\"action\": \"retrieve\"|\"direct\", \"reason\": \"...\"}"
            )),
            HumanMessage(content=json.dumps({
                "question": question,
                "history": history
            }))
        ]
        plan_resp: AIMessage = self.agent_llm(plan_prompt)
        try:
            plan = json.loads(plan_resp.content)
            action = plan.get("action", "retrieve")
        except json.JSONDecodeError:
            action = "retrieve"

        # 2) Direct answer path
        print("STEP 2")
        if action == "direct":
            direct_resp: AIMessage = self.agent_llm([
                SystemMessage(content="You are a helpful assistant."),
                HumanMessage(content=json.dumps({
                    "question": question,
                    "history": history
                }))
            ])
            return direct_resp.content, []

        # 3) Retrieval path: first form a retrieval query via the LLM.
        print("STEP 3")
        query_prompt = [
            SystemMessage(content=(
                "You are an agent that crafts precise retrieval queries. "
                "Given the user's question and conversation history, "
                "produce a single, concise retrieval query to fetch the most relevant documents."
            )),
            HumanMessage(content=json.dumps({
                "question": question,
                "history": history
            }))
        ]
        query_resp: AIMessage = self.agent_llm(query_prompt)
        retrieval_query = query_resp.content.strip()

        # 4) Execute RAG with the crafted query
        print("STEP 4")
        rag_answer, sources = self.rag.answer_with_sources(
            retrieval_query,
        )

        # 5) Synthesis step: refine the final answer
        print("STEP 5")
        synth_prompt = [
            SystemMessage(content=(
                "You are an expert assistant. Given the user question, the conversation history, "
                "and the retrieved context, produce a concise, accurate final answer. "
                "Cite sources by path when appropriate."
            )),
            HumanMessage(content=json.dumps({
                "question": question,
                "history": history,
                "retrieved_query": retrieval_query,
                "retrieved_answer": rag_answer,
                "sources": sources
            }))
        ]
        synth_resp: AIMessage = self.agent_llm(synth_prompt)
        final_answer = synth_resp.content

        return final_answer, sources


    def clear_history(self):
        """Clears RAG conversation history."""
        self.rag.clear_history()


# Example usage
if __name__ == "__main__":
    agent = AgentQA(docs_dir="./docs")
    # Pass previous turns via history=[("user","..."), ("assistant","..."), ...]
    ans, srcs = agent.ask("What is Hamilton, Ontario known for?", history=[])
    print(ans)
    if srcs:
        print("Sources:", srcs)
