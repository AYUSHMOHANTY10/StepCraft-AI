"""Safe demo tools. All order/ticket data is synthetic and held in memory."""
from __future__ import annotations

from typing import Any
from agent.knowledge import search_knowledge_base

DEMO_ORDERS: dict[str, dict[str, Any]] = {
    "DEMO-1001": {"status": "shipped", "item": "Wireless Mouse", "eta": "2026-10-25", "amount": 799},
    "DEMO-1002": {"status": "processing", "item": "Laptop Stand", "eta": "2026-10-27", "amount": 1299},
    "DEMO-1003": {"status": "delivered", "item": "USB-C Hub", "eta": "2026-10-18", "amount": 1599},
}
DEMO_TICKETS: list[dict[str, str]] = []


def search_kb(query: str) -> dict[str, Any]:
    """Search the local support knowledge base and return matching passages."""
    return {"results": search_knowledge_base(query)}


def lookup_order(order_id: str) -> dict[str, Any]:
    """Look up a synthetic demo order by ID. Use only IDs beginning DEMO-."""
    normalized = order_id.strip().upper()
    if not normalized.startswith("DEMO-"):
        return {"found": False, "message": "This demo only supports synthetic DEMO- order IDs."}
    order = DEMO_ORDERS.get(normalized)
    if not order:
        return {"found": False, "message": "No demo order was found for that ID."}
    return {"found": True, "order_id": normalized, **order}


def check_refund_eligibility(order_id: str) -> dict[str, Any]:
    """Check the demo refund policy; this tool does not issue refunds."""
    order_result = lookup_order(order_id)
    if not order_result.get("found"):
        return {"eligible": False, "reason": order_result["message"], "action_taken": False}
    if order_result["status"] != "delivered":
        return {
            "eligible": False,
            "reason": "The demo policy allows refund requests only after delivery.",
            "action_taken": False,
            "order_status": order_result["status"],
        }
    return {
        "eligible": True,
        "reason": "The delivered demo order can be submitted for review within 30 days.",
        "action_taken": False,
        "order_id": order_result["order_id"],
    }


def create_support_ticket(subject: str, details: str) -> dict[str, Any]:
    """Create a local demo ticket record; no external service is contacted."""
    ticket_id = f"DEMO-TICKET-{len(DEMO_TICKETS) + 1:04d}"
    ticket = {"ticket_id": ticket_id, "subject": subject[:120], "details": details[:1000], "status": "created_in_demo"}
    DEMO_TICKETS.append(ticket)
    return ticket
