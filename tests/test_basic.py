import pytest
from core.router import classify_intent
from utils.security import check_tool_permission

def test_intent_classification():
    assert classify_intent("hot picks under $100") == "SALES_RECO"
    assert classify_intent("why is SKU-123 blocked") == "COMPLIANCE_CHECK"
    assert classify_intent("help me with policy") == "GENERAL_KB"

def test_tool_permissions():
    # portal_customer cannot access vendor tools
    assert check_tool_permission("portal_customer", "vendor_validate") is False
    # internal_sales can access all
    assert check_tool_permission("internal_sales", "vendor_validate") is True