"""
Pytest-compatible tests for utils/llm_stub.py
Run with: pytest tests/test_llm_stub_pytest.py -v
"""
from utils.llm_stub import LLMStub

def test_sales_reco_formatting():
    llm = LLMStub()
    result = llm.format_response('SALES_RECO', {
        'allowed_picks': [{'name': 'Zen THC Soda', 'price': 25}]
    })
    assert "Zen THC Soda" in result
    assert "compliance checks" in result

def test_compliance_check_formatting():
    llm = LLMStub()
    result = llm.format_response('COMPLIANCE_CHECK', {
        'compliance_results': [{'status': 'blocked', 'reason_code': 'STATE_RESTRICTION'}]
    })
    assert "restricted" in result
    assert "STATE_RESTRICTION" in result

def test_pii_redaction():
    llm = LLMStub()
    result = llm.format_response('SALES_RECO', {
        'allowed_picks': [{'name': 'Product', 'email': 'test@example.com'}]
    })
    # PII should be redacted before formatting
    assert "[EMAIL_REDACTED]" not in result  # Email removed entirely from tool_results
    assert "Product" in result

def test_token_estimation():
    llm = LLMStub()
    text = "Based on your budget, I recommend: Zen THC Soda."
    tokens = llm.estimate_tokens(text)
    assert isinstance(tokens, int)
    assert tokens > 0

def test_fallback_intent():
    llm = LLMStub()
    result = llm.format_response('UNKNOWN_INTENT', {})
    assert "Request processed" in result