# Evaluation Report

## Scope

This evaluation checks six deterministic support scenarios: known order status, refund eligibility for a processing order, shipping policy retrieval, privacy guidance, unknown order handling, and cautious warranty answers.

## Metrics

- **Cases:** 6
- **Assertions per case:** required answer fragment(s) and expected tool label
- **Primary metric:** exact-rule pass rate (all required assertions pass)
- **Not measured:** LLM answer quality, factuality under model variation, latency, token cost, concurrent load, retrieval recall on a labeled corpus, or user satisfaction

## Execution status

**Executed in the authoring environment on 2026-10-22:** `python -m evals.run_eval` passed **6/6 cases (100%)** and `pytest -q` passed **6 tests**. These results cover only the deterministic offline path in this repository. Re-run both commands after any changes and before sharing the report.

| Case | Expected behavior |
|---|---|
| `order_status_known` | Returns shipped status and delivery estimate for DEMO-1001; order lookup path |
| `refund_pending_order` | States processing order is not refund-eligible; eligibility-check path |
| `shipping_policy` | Retrieves the standard shipping window from the local KB |
| `privacy_policy` | Warns against sharing passwords or OTPs |
| `unknown_order` | Says unknown synthetic order was not found |
| `insufficient_context` | Gives the general warranty caveat without inventing a duration |

## Interpretation

This is a smoke/regression suite for deterministic behavior, not proof of production readiness. For the LLM-enabled LangGraph route, add a separate labeled dataset and score tool-selection accuracy, answer groundedness, refusal/abstention correctness, tool-loop termination, p50/p95 latency, and token cost over multiple runs.
