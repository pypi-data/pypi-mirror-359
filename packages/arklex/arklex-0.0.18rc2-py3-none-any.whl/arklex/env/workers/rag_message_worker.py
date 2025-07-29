"""RAG Message worker implementation for the Arklex framework.

This module provides a specialized worker that combines Retrieval-Augmented Generation (RAG)
and message generation capabilities. The RagMsgWorker class intelligently decides whether
to use RAG retrieval or direct message generation based on the context, providing a flexible
approach to handling user queries that may require either factual information from documents
or conversational responses.
"""

from functools import partial
from typing import Any, TypedDict

from langchain.prompts import PromptTemplate
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph

from arklex.env.prompts import load_prompts
from arklex.env.tools.RAG.retrievers.milvus_retriever import RetrieveEngine
from arklex.env.workers.message_worker import MessageWorker
from arklex.env.workers.worker import BaseWorker, register_worker
from arklex.utils.graph_state import MessageState
from arklex.utils.logging_utils import LogContext
from arklex.utils.model_provider_config import PROVIDER_MAP

log_context = LogContext(__name__)


class RagMsgWorkerKwargs(TypedDict, total=False):
    """Type definition for kwargs used in RagMsgWorker._execute method."""

    tags: dict[str, Any]


@register_worker
class RagMsgWorker(BaseWorker):
    description: str = "A combination of RAG and Message Workers"

    def __init__(self) -> None:
        super().__init__()
        self.llm: BaseChatModel | None = None
        self.tags: dict[str, Any] = {}
        self.action_graph: StateGraph | None = None

    def _choose_retriever(self, state: MessageState) -> str:
        prompts: dict[str, str] = load_prompts(state.bot_config)
        prompt: PromptTemplate = PromptTemplate.from_template(
            prompts["retrieval_needed_prompt"]
        )
        input_prompt = prompt.invoke({"formatted_chat": state.user_message.history})
        log_context.info(
            f"Prompt for choosing the retriever in RagMsgWorker: {input_prompt.text}"
        )
        final_chain = self.llm | StrOutputParser()
        answer: str = final_chain.invoke(input_prompt.text)
        log_context.info(f"Choose retriever in RagMsgWorker: {answer}")
        if "yes" in answer.lower():
            return "retriever"
        return "message_worker"

    def _create_action_graph(self, tags: dict[str, Any]) -> StateGraph:
        workflow: StateGraph = StateGraph(MessageState)
        # Create a partial function with the extra argument bound
        retriever_with_args = partial(RetrieveEngine.milvus_retrieve, tags=tags)
        # Add nodes for each worker
        msg_wkr: MessageWorker = MessageWorker()
        workflow.add_node("retriever", retriever_with_args)
        workflow.add_node("message_worker", msg_wkr.execute)
        # Add edges
        workflow.add_conditional_edges(START, self._choose_retriever)
        workflow.add_edge("retriever", "message_worker")
        return workflow

    def _execute(
        self, msg_state: MessageState, **kwargs: RagMsgWorkerKwargs
    ) -> dict[str, Any]:
        self.llm = PROVIDER_MAP.get(
            msg_state.bot_config.llm_config.llm_provider, ChatOpenAI
        )(model=msg_state.bot_config.llm_config.model_type_or_path)
        self.tags = kwargs.get("tags", {})
        self.action_graph = self._create_action_graph(self.tags)
        graph = self.action_graph.compile()
        result: dict[str, Any] = graph.invoke(msg_state)
        return result
