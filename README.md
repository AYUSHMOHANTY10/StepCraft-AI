# Steps Agentic Support Demo

A small, interview-friendly portfolio project demonstrating a tool-using support agent, local retrieval, API design, traceable tool execution, and regression evaluation. It uses synthetic order records only; it does not connect to a real shop, CRM, payment provider, or customer account.

## Features

- **LangGraph orchestration:** agent → tool execution → agent loop when an OpenAI API key is configured.
- **Tool calling:** local knowledge-base search, synthetic order lookup, refund eligibility check, and demo ticket creation.
- **Checkpointing:** LangGraph `MemorySaver` keyed by `thread_id` for in-process conversational state.
- **Retrieval:** transparent token-overlap ranking over a small local JSON knowledge base. This is a baseline retriever, **not** a vector database or hybrid search implementation.
- **FastAPI:** typed request/response models and generated OpenAPI docs at `/docs`.
- **Offline demo:** predictable deterministic responses work without an API key.
- **Regression evaluation:** six answer/tool-use cases in `evals/cases.json`.
- **Safety boundaries:** only synthetic `DEMO-` order IDs are accepted; refund checking never issues a refund; tickets are local demo records.

## Quick start

Python 3.11+ is recommended.

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`. Example request:

```json
{
  "query": "What is the status of order DEMO-1001?",
  "thread_id": "interview-demo-1"
}
```

Without `OPENAI_API_KEY`, the app reports `mode: offline-demo` and uses deterministic local logic. To enable the LangGraph tool-calling path, copy `.env.example` to `.env`, set `OPENAI_API_KEY`, and export the variables in your shell before starting the API. `OPENAI_MODEL` defaults to `gpt-4o-mini`. Do not commit `.env` or API keys.

## Run tests and evaluation

```bash
pytest -q
python -m evals.run_eval
```

The regression evaluator reports exact answer-fragment checks and expected tool labels. The current deterministic offline path passed 6/6 cases and the test suite passed 6 tests in the authoring environment. This is a small smoke test, not a statistically powered LLM benchmark. The LLM path should be evaluated separately across repeated runs before making quality claims.

## Architecture

```text
Client
  └── FastAPI /chat
        └── run_agent
              ├── Offline deterministic route (no key)
              └── LangGraph (API key configured)
                    ├── Agent model node
                    ├── ToolNode
                    │     ├── Knowledge-base search
                    │     ├── Demo order lookup
                    │     ├── Refund eligibility check
                    │     └── Local demo ticket creation
                    └── MemorySaver checkpoint by thread_id
```

## Evaluation report

See [`evals/EVALUATION_REPORT.md`](evals/EVALUATION_REPORT.md). Run the evaluator locally and replace the placeholder execution status with the actual output from your machine before quoting a pass rate on your resume.

## Limitations and next steps

- No external order, payment, ticketing, WhatsApp, voice, or CRM integration.
- No vector database, embeddings, hybrid retrieval, reranker, Redis, Celery, or production tracing.
- Checkpointing is in-memory and is lost when the process restarts; use a persistent checkpointer for durable sessions.
- The demo ticket tool performs a local mutation without a human approval interrupt; add a LangGraph interrupt/approval step before integrating real side effects.
- Offline mode is intentionally deterministic and is not evidence of LLM reasoning quality.
- Add provider adapters, retrieval metrics, latency/cost telemetry, persistent storage, authentication, rate limits, and deployment hardening before production use.

## Resume wording after you run and verify it

**Agentic Support Assistant | Python, FastAPI, LangGraph, OpenAI tool calling** — Built a tool-using support agent with knowledge-base retrieval, synthetic order lookup, refund-eligibility checks, per-thread in-memory checkpointing, and a six-case regression suite; exposed typed chat endpoints through FastAPI.

Only list LangGraph/OpenAI tool calling as implemented after you have run the API with a configured key and verified that path. If you only run offline mode, describe it as a deterministic support-agent prototype with a LangGraph implementation included but not yet validated against a live model.
