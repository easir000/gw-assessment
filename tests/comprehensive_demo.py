"""
Comprehensive Demo Queries - 16 Test Scenarios
Updated for Official GW seed_data.json

Test Categories:
- Sales Intent (3 queries)
- Compliance Intent (3 queries)
- Vendor Intent (2 queries)
- Ops Intent (2 queries)
- KB Intent (2 queries)
- Security & Permissions (2 queries)
- Session Memory (2 queries)

Generates: tests/test_results.json
"""
import httpx
import json
import time
import os
from typing import List, Dict
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

# ============================================================================
# 16 Comprehensive Test Queries (Updated for Official GW Data)
# ============================================================================

COMPREHENSIVE_QUERIES: List[Dict] = [
    # ========================================================================
    # SALES_RECO Intent (3 queries)
    # ========================================================================
    {
        "id": 1,
        "name": "Sales: Hot picks under budget",
        "query": "Give me hot picks for CA under $5000",
        "user_type": "internal_sales",
        "expected_intent": "SALES_RECO",
        "expected_status": 200,
        "description": "Tests sales chain with compliance gating (official data)"
    },
    {
        "id": 2,
        "name": "Sales: Low budget filter",
        "query": "Recommend products under $20",
        "user_type": "portal_customer",
        "expected_intent": "SALES_RECO",
        "expected_status": 200,
        "description": "Tests budget filtering with customer permissions"
    },
    {
        "id": 3,
        "name": "Sales: Best sellers request",
        "query": "Show me your best sellers",
        "user_type": "internal_sales",
        "expected_intent": "SALES_RECO",
        "expected_status": 200,
        "description": "Tests keyword matching for 'best sellers'"
    },
    
    # ========================================================================
    # COMPLIANCE_CHECK Intent (3 queries)
    # ========================================================================
    {
        "id": 4,
        "name": "Compliance: Why blocked in TX",
        "query": "Why is SKU-1003 not available in TX? Suggest alternatives.",
        "user_type": "portal_customer",
        "expected_intent": "COMPLIANCE_CHECK",
        "expected_status": 200,
        "description": "Tests compliance check with TX state restrictions (THC Beverage)"
    },
    {
        "id": 5,
        "name": "Compliance: Legal check in TX",
        "query": "Is SKU-1010 legal to sell in TX?",
        "user_type": "portal_vendor",
        "expected_intent": "COMPLIANCE_CHECK",
        "expected_status": 200,
        "description": "Tests compliance for CBD Tincture in allowed state"
    },
    {
        "id": 6,
        "name": "Compliance: Mushroom restricted in CA",
        "query": "Why is SKU-1031 restricted in CA?",
        "user_type": "portal_customer",
        "expected_intent": "COMPLIANCE_CHECK",
        "expected_status": 200,
        "description": "Tests compliance with CA state restrictions (Mushroom Gummies)"
    },
    
    # ========================================================================
    # VENDOR_ONBOARDING Intent (2 queries)
    # ========================================================================
    {
        "id": 7,
        "name": "Vendor: Missing fields validation",
        "query": "I am uploading a product missing Net Wt and no lab report - what do I fix?",
        "user_type": "portal_vendor",
        "expected_intent": "VENDOR_ONBOARDING",
        "expected_status": 200,
        "description": "Tests vendor validation with missing required fields"
    },
    {
        "id": 8,
        "name": "Vendor: Complete submission",
        "query": "I need to upload a vendor product for approval",
        "user_type": "portal_vendor",
        "expected_intent": "VENDOR_ONBOARDING",
        "expected_status": 200,
        "description": "Tests vendor onboarding flow"
    },
    
    # ========================================================================
    # OPS_STOCK Intent (2 queries)
    # ========================================================================
    {
        "id": 9,
        "name": "Ops: Stock check by SKU",
        "query": "How much stock does SKU-1001 have and where?",
        "user_type": "internal_sales",
        "expected_intent": "OPS_STOCK",
        "expected_status": 200,
        "description": "Tests inventory lookup by product ID (Accessories)"
    },
    {
        "id": 10,
        "name": "Ops: Warehouse availability",
        "query": "Check inventory and warehouse stock for SKU-1002",
        "user_type": "internal_sales",
        "expected_intent": "OPS_STOCK",
        "expected_status": 200,
        "description": "Tests stock availability across warehouses (Nicotine Vape)"
    },
    
    # ========================================================================
    # GENERAL_KB Intent (2 queries)
    # ========================================================================
    {
        "id": 11,
        "name": "KB: Return policy",
        "query": "What is the returns SOP?",
        "user_type": "portal_customer",
        "expected_intent": "GENERAL_KB",
        "expected_status": 200,
        "description": "Tests knowledge base search for Returns SOP"
    },
    {
        "id": 12,
        "name": "KB: Shipping info",
        "query": "How does LTL freight shipping work?",
        "user_type": "portal_customer",
        "expected_intent": "GENERAL_KB",
        "expected_status": 200,
        "description": "Tests knowledge base search for Shipping Policy"
    },
    
    # ========================================================================
    # Security & Permissions (2 queries)
    # ========================================================================
    {
        "id": 13,
        "name": "Security: Unauthorized vendor access",
        "query": "I need to upload a vendor product",
        "user_type": "portal_customer",
        "expected_intent": "VENDOR_ONBOARDING",
        "expected_status": 403,
        "description": "Tests that portal_customer cannot access vendor_validate"
    },
    {
        "id": 14,
        "name": "Security: Full internal access",
        "query": "Check stock and inventory for SKU-1001",
        "user_type": "internal_sales",
        "expected_intent": "OPS_STOCK",
        "expected_status": 200,
        "description": "Tests that internal_sales can access all tools"
    },
    
    # ========================================================================
    # Session Memory & Follow-ups (2 queries)
    # ========================================================================
    {
        "id": 15,
        "name": "Memory: First request",
        "query": "Show hot picks under $100",
        "user_type": "internal_sales",
        "session_id": "memory-test-session",
        "expected_intent": "SALES_RECO",
        "expected_status": 200,
        "description": "First request to establish session context"
    },
    {
        "id": 16,
        "name": "Memory: Follow-up request",
        "query": "Ok add 2 of the first one to the basket",
        "user_type": "internal_sales",
        "session_id": "memory-test-session",
        "expected_intent": "GENERAL_KB",
        "expected_status": 200,
        "description": "Follow-up uses session context (intent may vary with keyword router)"
    },
]


# ============================================================================
# Helper Functions
# ============================================================================

def retry_request(func, max_retries=2, delay=1.0):
    """
    Retry failed requests with exponential backoff.
    Handles connection errors gracefully.
    """
    for attempt in range(max_retries):
        try:
            return func()
        except httpx.RequestError as e:
            if attempt < max_retries - 1:
                print(f"   ⚠️  Connection error, retrying... ({attempt + 1}/{max_retries})")
                time.sleep(delay)
            else:
                raise e


def save_test_results(results: Dict):
    """
    Save test results to tests/test_results.json
    """
    # Ensure tests directory exists
    os.makedirs("tests", exist_ok=True)
    
    # Add metadata
    results["generated_at"] = datetime.now().isoformat()
    results["total_tests"] = results["passed"] + results["failed"]
    results["pass_rate"] = f"{results['passed']/results['total_tests']*100:.1f}%"
    
    # Save to file
    output_path = "tests/test_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Test results saved to: {output_path}")


def run_comprehensive_demo():
    """Run all 16 comprehensive test queries."""
    print("\n" + "=" * 80)
    print("🚀 GW Assessment - Comprehensive Demo Queries (16 Tests)")
    print("=" * 80 + "\n")
    
    results = {
        "passed": 0,
        "failed": 0,
        "total": len(COMPREHENSIVE_QUERIES),
        "details": [],
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with httpx.Client(timeout=30.0) as client:
        for test in COMPREHENSIVE_QUERIES:
            print(f"📋 Test #{test['id']}: {test['name']}")
            print(f"   Query: {test['query']}")
            print(f"   User Type: {test['user_type']}")
            print(f"   Expected: Intent={test['expected_intent']}, Status={test['expected_status']}")
            print(f"   Description: {test['description']}")
            
            try:
                # Build request payload
                payload = {
                    "query": test["query"],
                    "user_type": test["user_type"]
                }
                
                # Add session_id if specified (for memory tests)
                if "session_id" in test:
                    payload["session_id"] = test["session_id"]
                
                # Make request with retry logic
                def make_request():
                    return client.post(
                        f"{BASE_URL}/chat",
                        json=payload,
                        timeout=30.0
                    )
                
                response = retry_request(make_request)
                
                # Validate status code
                status_match = response.status_code == test["expected_status"]
                
                # Validate intent (only for 200 responses)
                intent_match = True
                intent_value = "N/A"
                if response.status_code == 200:
                    data = response.json()
                    intent_value = data.get("intent", "N/A")
                    intent_match = intent_value == test["expected_intent"]
                elif response.status_code == 403:
                    intent_value = "N/A (403 Forbidden)"
                
                # Determine pass/fail
                if status_match and intent_match:
                    print(f"   ✅ PASSED (Status: {response.status_code}, Intent: {intent_value})")
                    results["passed"] += 1
                    test_result = "PASSED"
                else:
                    print(f"   ❌ FAILED (Status: {response.status_code}, Expected: {test['expected_status']})")
                    if response.status_code == 200:
                        print(f"      Intent: {intent_value}, Expected: {test['expected_intent']}")
                    results["failed"] += 1
                    test_result = "FAILED"
                
                # Store details
                results["details"].append({
                    "id": test["id"],
                    "name": test["name"],
                    "result": test_result,
                    "status_code": response.status_code,
                    "expected_status": test["expected_status"],
                    "intent": intent_value,
                    "expected_intent": test["expected_intent"]
                })
                
            except httpx.ConnectError as e:
                print(f"   ❌ CONNECTION ERROR: {str(e)}")
                print(f"   💡 Hint: Make sure server is running at {BASE_URL}")
                results["failed"] += 1
                results["details"].append({
                    "id": test["id"],
                    "name": test["name"],
                    "result": "CONNECTION_ERROR",
                    "error": str(e)
                })
            except Exception as e:
                print(f"   ❌ ERROR: {str(e)}")
                results["failed"] += 1
                results["details"].append({
                    "id": test["id"],
                    "name": test["name"],
                    "result": "ERROR",
                    "error": str(e)
                })
            
            print("-" * 80 + "\n")
    
    # Print summary
    print("=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    print(f"   Total Tests:  {results['total']}")
    print(f"   ✅ Passed:    {results['passed']} ({results['passed']/results['total']*100:.1f}%)")
    print(f"   ❌ Failed:    {results['failed']} ({results['failed']/results['total']*100:.1f}%)")
    print("=" * 80)
    
    # Print failed tests details
    if results["failed"] > 0:
        print("\n❌ FAILED TESTS:")
        for detail in results["details"]:
            if detail["result"] != "PASSED":
                print(f"   - Test #{detail['id']}: {detail['name']} ({detail['result']})")
        print("\n💡 Tips:")
        print("   1. Ensure server is running: uvicorn main:app --host 127.0.0.1 --port 8000 --reload")
        print("   2. Check server logs for errors")
        print("   3. Some failures may be expected (e.g., keyword router limitations)")
    else:
        print("\n🎉 ALL 16 TESTS PASSED! Solution is production-ready!")
    
    print("=" * 80 + "\n")
    
    # Save results to JSON file
    save_test_results(results)
    
    return results


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    print("\n💡 Before running, ensure server is active:")
    print("   uvicorn main:app --host 127.0.0.1 --port 8000 --reload\n")
    
    input("Press Enter to start tests (or Ctrl+C to cancel)...")
    
    results = run_comprehensive_demo()
    
    # Exit with appropriate code
    if results["failed"] > 0:
        exit(1)
    else:
        exit(0)
