from agent.graph import offline_answer
from agent.knowledge import search_knowledge_base
from agent.tools import check_refund_eligibility, lookup_order


def test_known_order_status():
    result = offline_answer("What is the status of order DEMO-1001?")
    assert "shipped" in result["answer"]
    assert "2026-10-25" in result["answer"]
    assert "lookup_order" in result["tools_used"]


def test_unknown_order_is_not_invented():
    result = lookup_order("DEMO-9999")
    assert result["found"] is False


def test_non_demo_order_is_rejected():
    result = lookup_order("12345")
    assert result["found"] is False
    assert "synthetic" in result["message"]


def test_refund_does_not_issue_refund():
    result = check_refund_eligibility("DEMO-1003")
    assert result["eligible"] is True
    assert result["action_taken"] is False


def test_kb_retrieval_returns_relevant_shipping_passage():
    results = search_knowledge_base("How long does standard shipping take?")
    assert results
    assert results[0]["id"] == "shipping-01"


def test_unknown_warranty_duration_is_not_made_up():
    result = offline_answer("What is the warranty duration for the Acme blender?")
    assert "Warranty coverage depends" in result["answer"]
