"""Small deterministic regression evaluation for the offline demo path."""
from __future__ import annotations
import json
from pathlib import Path
from agent.graph import offline_answer

CASES = Path(__file__).with_name("cases.json")


def evaluate() -> dict:
    cases = json.loads(CASES.read_text(encoding="utf-8"))
    rows = []
    for case in cases:
        result = offline_answer(case["query"])
        answer = result["answer"].lower()
        contains_ok = all(fragment.lower() in answer for fragment in case["must_contain"])
        tool_ok = case["must_use_tool"] in result["tools_used"]
        rows.append({"id": case["id"], "pass": contains_ok and tool_ok, "contains_ok": contains_ok, "tool_ok": tool_ok, "answer": result["answer"]})
    passed = sum(row["pass"] for row in rows)
    return {"passed": passed, "total": len(rows), "pass_rate": round(passed / len(rows), 3) if rows else 0, "cases": rows}

if __name__ == "__main__":
    report = evaluate()
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["passed"] == report["total"] else 1)
