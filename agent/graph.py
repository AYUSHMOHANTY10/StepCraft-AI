"""LangGraph tool-calling agent with an offline deterministic fallback."""
from __future__ import annotations

import os
from typing import Annotated, TypedDict
import operator

from agent.knowledge import search_knowledge_base
from agent.tools import check_refund_eligibility, create_support_ticket, lookup_order, search_kb

try:
    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
    from langchain_core.tools import tool
    from langchain_openai import ChatOpenAI
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.graph import END, MessagesState, StateGraph
    from langgraph.prebuilt import ToolNode, tools_condition
    LANGGRAPH_AVAILABLE = True
except ImportError:  # allows a basic fallback if optional dependencies are not installed
    LANGGRAPH_AVAILABLE = False


SYSTEM_PROMPT = """You are Steps Support, a careful e-commerce support agent for a fictional demo.
Use tools for order-specific questions, policy questions, and support-ticket requests.
Only discuss synthetic DEMO- order IDs. Never claim a refund was issued: the tool only checks
eligibility. Tickets are created in a local demo store, not in a real support system.
Ground policy answers in retrieved knowledge-base passages. If evidence is missing, say so.
Be concise, distinguish facts from assumptions, and ask for missing information when needed."""


def offline_answer(query: str) -> dict:
    """Predictable no-key demo path. Does not claim to be an LLM."""
    q = query.lower()
    order_id = next((token.strip(".,?!") for token in query.upper().split() if token.startswith("DEMO-")), None)
    if order_id and ("order" in q or "track" in q or "status" in q or "deliver" in q):
        result = lookup_order(order_id)
        if result.get("found"):
            answer = f"Order {order_id} is {result['status']}. Estimated delivery: {result['eta']}. Item: {result['item']}."
        else:
            answer = result["message"]
        return {"answer": answer, "mode": "offline-demo", "tools_used": ["lookup_order"], "sources": []}
    if order_id and "refund" in q:
        result = check_refund_eligibility(order_id)
        status_note = f" Order status: {result['order_status']}." if result.get("order_status") else ""
        answer = f"Refund eligible: {result['eligible']}. {result['reason']}{status_note} No refund has been issued."
        return {"answer": answer, "mode": "offline-demo", "tools_used": ["check_refund_eligibility"], "sources": []}
    results = search_knowledge_base(query)
    if results:
        best = results[0]
        answer = f"According to {best['title']}: {best['content']}"
        return {"answer": answer, "mode": "offline-demo", "tools_used": ["search_kb"], "sources": [{"id": best['id'], "title": best['title'], "score": best['score']} ]}
    return {
        "answer": "I couldn't find enough information to answer confidently. Please share the relevant order ID or clarify your question.",
        "mode": "offline-demo", "tools_used": [], "sources": [],
    }


def build_graph():
    if not LANGGRAPH_AVAILABLE or not os.getenv("OPENAI_API_KEY"):
        return None

    @tool
    def search_knowledge(query: str) -> str:
        """Search support policy and FAQ passages. Use for policy/product questions."""
        return str(search_kb(query))

    @tool
    def get_order_status(order_id: str) -> str:
        """Look up a synthetic order. Only DEMO- IDs are supported."""
        return str(lookup_order(order_id))

    @tool
    def check_refund(order_id: str) -> str:
        """Check refund eligibility for a synthetic order; does not issue a refund."""
        return str(check_refund_eligibility(order_id))

    @tool
    def open_demo_ticket(subject: str, details: str) -> str:
        """Create a local demo ticket record, not an external support ticket."""
        return str(create_support_ticket(subject, details))

    available_tools = [search_knowledge, get_order_status, check_refund, open_demo_ticket]
    model = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0).bind_tools(available_tools)

    class AgentState(MessagesState):
        trace: Annotated[list[str], operator.add]

    def call_model(state):
        response = model.invoke([SystemMessage(content=SYSTEM_PROMPT), *state["messages"]])
        trace = ["model:tool_call" if getattr(response, "tool_calls", None) else "model:final"]
        return {"messages": [response], "trace": trace}

    def record_tools(state):
        return {"trace": [f"tool:{message.name}" for message in state["messages"] if isinstance(message, ToolMessage)]}

    workflow = StateGraph(AgentState)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode(available_tools))
    workflow.add_node("record_tools", record_tools)
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges("agent", tools_condition, {"tools": "tools", END: END})
    workflow.add_edge("tools", "record_tools")
    workflow.add_edge("record_tools", "agent")
    return workflow.compile(checkpointer=MemorySaver())


GRAPH = build_graph()


def run_agent(query: str, thread_id: str = "default") -> dict:
    if not query.strip():
        raise ValueError("query must not be empty")
    if GRAPH is None:
        return offline_answer(query)
    from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
    config = {"configurable": {"thread_id": thread_id}}
    result = GRAPH.invoke({"messages": [HumanMessage(content=query)], "trace": []}, config=config)
    messages = result.get("messages", [])
    final = next((m for m in reversed(messages) if isinstance(m, AIMessage) and not getattr(m, "tool_calls", None)), None)
    tools_used = [m.name for m in messages if isinstance(m, ToolMessage)]
    return {
        "answer": str(final.content) if final else "I couldn't produce a final answer.",
        "mode": "langgraph-openai",
        "tools_used": tools_used,
        "sources": [],
        "trace": result.get("trace", []),
    }
