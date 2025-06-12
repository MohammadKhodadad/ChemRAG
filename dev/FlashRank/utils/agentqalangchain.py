import json
import argparse
from typing import Any, Dict, List, Optional, Tuple, Union

from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
if __name__=='__main__':
    from rag_reranker import RagReranker  # adjust import path if needed
else:
    from .rag_reranker import RagReranker  # adjust import path if needed

class AgentQA:
    """
    An agentic QA system that uses a core LLM to think and decide when to query the RAG retriever.
    Accepts the same input and returns the same output (answer, sources) as RagReranker.
    """

    def __init__(
        self,
        docs_dir: str,
        embedding_model: str = "text-embedding-ada-002",
        llm_model: str = "gpt-4o",
        k: int = 20,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        agent_llm_model: str = "gpt-4o",
    ):
        # initialize RAG reranker for retrieval
        self.rag = RagReranker(
            docs_dir=docs_dir,
            embedding_model=embedding_model,
            llm_model=llm_model,
            k=k,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        # LLM for agent planning
        self.agent_llm = init_chat_model("openai:gpt-o4-mini")

        # wrap rag answer as a tool for the agent
        def _rag_tool(query: str) -> str:
            """Receives a query in form of a question; retrieves and reranks from local documents; returns JSON with 'answer' & 'sources'."""
            print(query)
            answer, sources = self.rag.answer_with_sources(query)
            return json.dumps({"answer": answer, "sources": sources})

        # build the REACT agent with the properly documented tool
        self.agent = create_react_agent(
            model=f"openai:{agent_llm_model}",
            tools=[_rag_tool],
            prompt="You are a helpful assistant. Your task is to answer user's query. Your response must be a python dict containing keys 'answer' and 'sources'. You must include the sources from rag tool in case you use it."
        )

    def ask(
        self,
        question: str,
        history: Optional[List[Union[Dict[str, Any], Tuple[str, str]]]] = None,
    ) -> Tuple[str, List[str]]:
        """
        Ask a question to the agent. Returns a tuple (answer, sources).

        :param question: The user question
        :param history: Optional list of dicts or tuples representing past messages
        :return: answer string and list of source identifiers
        """
        # convert history entries into BaseMessage objects
        history_msgs: List[Any] = []
        if history:
            for entry in history:
                if isinstance(entry, dict):
                    role = entry.get('role', 'user')
                    content = entry.get('content', '')
                else:
                    role, content = entry

                if role.lower() == "system":
                    history_msgs.append(SystemMessage(content=content))
                elif role.lower() == "assistant":
                    history_msgs.append(AIMessage(content=content))
                else:
                    history_msgs.append(HumanMessage(content=content))

        # invoke the agent with both question and history keys
        # history_msgs.append(HumanMessage(content=question))
        payload = {
            "messages": history_msgs,
        }
        print(payload)
        response: Dict = self.agent.invoke(payload)

        # extract tool outputs from response messages
        msgs = response.get("messages", [])
        print(msgs)
        for msg in msgs:
            print(type(msg))
            print(msg,'\n')
        final = msgs[-1] if msgs else {"content": ""}
        content = getattr(final, "content", str(final))
        print('Final Content:')
        print(content)
        # parse JSON answer if possible
        try:
            payload = json.loads(content)
            answer = payload.get("answer", content)
            sources = payload.get("sources", [])
        except json.JSONDecodeError:
            answer = content
            sources = []

        return answer, sources


def main():
    import dotenv
    dotenv.load_dotenv()

    parser = argparse.ArgumentParser(description="Run AgentQA on a query")
    parser.add_argument(
        "--docs_dir", type=str, default="..\..\DoclingTest\parsed_outputs",
        help="Path to the directory containing your documents"
    )
    parser.add_argument(
        "--query", type=str,
        default="Tell me about polymers from your database of knowledge",
        help="The question to ask the agent"
    )
    args = parser.parse_args()

    agent = AgentQA(
        docs_dir=args.docs_dir
    )
    answer, sources = agent.ask(args.query)
    print("Answer:", answer)
    print("Sources:", sources)


if __name__ == "__main__":
    main()
