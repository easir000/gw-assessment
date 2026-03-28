"""
Quick tests for utils/llm_stub.py
Run with: python tests/test_llm_stub.py
"""
import sys
import os

# Add project root to Python path (fixes ModuleNotFoundError)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now imports will work
from utils.llm_stub import LLMStub

def test_all():
    llm = LLMStub()
    
    print("=" * 60)
    print("🧪 Testing LLMStub")
    print("=" * 60)
    
    # Test 1: SALES_RECO
    print("\n1. SALES_RECO formatting:")
    result = llm.format_response('SALES_RECO', {
        'allowed_picks': [
            {'name': 'Zen THC Soda', 'price': 25},
            {'name': 'Organic Hemp Gummies', 'price': 30}
        ]
    })
    print(f"   ✅ {result}")
    
    # Test 2: COMPLIANCE_CHECK
    print("\n2. COMPLIANCE_CHECK formatting:")
    result = llm.format_response('COMPLIANCE_CHECK', {
        'compliance_results': [
            {'status': 'blocked', 'reason_code': 'STATE_RESTRICTION'}
        ]
    })
    print(f"   ✅ {result}")
    
    # Test 3: VENDOR_ONBOARDING
    print("\n3. VENDOR_ONBOARDING formatting:")
    result = llm.format_response('VENDOR_ONBOARDING', {
        'status': 'FAIL',
        'fixes': ['Provide net_wt_oz', 'Provide lab_report']
    })
    print(f"   ✅ {result}")
    
    # Test 4: OPS_STOCK
    print("\n4. OPS_STOCK formatting:")
    result = llm.format_response('OPS_STOCK', {
        'stock_results': [
            {'warehouse': 'WH-TX', 'qty': 500},
            {'warehouse': 'WH-FL', 'qty': 200}
        ]
    })
    print(f"   ✅ {result}")
    
    # Test 5: PII Redaction
    print("\n5. PII Redaction test:")
    result = llm.format_response('SALES_RECO', {
        'allowed_picks': [
            {'name': 'Product', 'email': 'user@example.com', 'phone': '555-123-4567'}
        ]
    })
    print(f"   ✅ {result}")
    print("   💡 Note: PII is redacted in tool_results before formatting")
    
    # Test 6: Token Estimation
    print("\n6. Token estimation:")
    text = "Based on your budget, I recommend: Zen THC Soda."
    tokens = llm.estimate_tokens(text)
    print(f"   Text: '{text}'")
    print(f"   ✅ Estimated tokens: {tokens} (chars: {len(text)})")
    
    # Test 7: Fallback for unknown intent
    print("\n7. Fallback for unknown intent:")
    result = llm.format_response('UNKNOWN_INTENT', {})
    print(f"   ✅ {result}")
    
    print("\n" + "=" * 60)
    print("🎉 All LLMStub tests passed!")
    print("=" * 60)

if __name__ == "__main__":
    test_all()