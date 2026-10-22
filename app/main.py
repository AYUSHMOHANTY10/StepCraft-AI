from __future__ import annotations
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from agent.graph import run_agent, GRAPH, LANGGRAPH_AVAILABLE

app = FastAPI(
    title="Steps Agentic Support Demo",
    version="1.0.0",
    description="A portfolio demo of tool-using support agents, local retrieval, and LangGraph orchestration.",
)

class ChatRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)
    thread_id: str = Field(default="demo-session", min_length=1, max_length=128)

class ChatResponse(BaseModel):
    answer: str
    mode: str
    tools_used: list[str] = []
    sources: list[dict] = []
    trace: list[str] = []

@app.get("/health")
def health():
    return {"status": "ok", "langgraph_available": LANGGRAPH_AVAILABLE, "llm_enabled": GRAPH is not None}

@app.get("/")
def root():
    return {"name": "Steps Agentic Support Demo", "docs": "/docs", "health": "/health"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        result = run_agent(request.query, request.thread_id)
        return ChatResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
