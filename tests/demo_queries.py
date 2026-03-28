import httpx
import json

BASE_URL = "http://127.0.0.1:8000"

DEMO_QUERIES = [
    {
        "name": "Sales: Hot picks under budget",
        "query": "Give me hot picks for CA under $5000",
        "user_type": "internal_sales",
        "expected_intent": "SALES_RECO"
    },
    {
        "name": "Compliance: Why blocked + alternatives",
        "query": "Why is SKU-1001 not available in CA? Suggest alternatives.",
        "user_type": "portal_customer",
        "expected_intent": "COMPLIANCE_CHECK"
    },
    {
        "name": "Ops: Stock check",
        "query": "How much stock does SKU-1001 have and where?",
        "user_type": "internal_sales",
        "expected_intent": "OPS_STOCK"
    },
    {
        "name": "Vendor onboarding validation",
        "query": "I'm uploading a product missing Net Wt and no lab report—what do I fix?",
        "user_type": "portal_vendor",
        "expected_intent": "VENDOR_ONBOARDING"
    },
    {
        "name": "Memory follow-up",
        "query": "Ok add 2 of the first one to the basket",
        "user_type": "internal_sales",
        "expected_intent": "SALES_RECO",
        "uses_memory": True
    }
]

def run_demo():
    print("🚀 Running GW Assessment Demo Queries\n")
    print("=" * 60)
    
    with httpx.Client() as client:
        for i, test in enumerate(DEMO_QUERIES, 1):
            print(f"\n{i}. {test['name']}")
            print(f"   Query: {test['query']}")
            print(f"   User Type: {test['user_type']}")
            
            response = client.post(
                f"{BASE_URL}/chat",
                json={
                    "query": test["query"],
                    "user_type": test["user_type"],
                    "session_id": "demo-session"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Intent: {data['intent']}")
                print(f"   ✅ Response: {data['response'][:100]}...")
                print(f"   ✅ Request ID: {data['request_id']}")
            else:
                print(f"   ❌ Error: {response.status_code}")
            
            print("-" * 60)
    
    print("\n✅ Demo complete! Check server logs for observability data.")

if __name__ == "__main__":
    run_demo()