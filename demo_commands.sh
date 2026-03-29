#!/bin/bash
# GW Assessment - Live Demo Commands
# Run after server is started: uvicorn main:app --host 127.0.0.1 --port 8000 --reload

BASE_URL="http://127.0.0.1:8000"
SESSION="walkthrough-demo"

echo "🎬 Starting GW Assessment Live Demo"
echo "======================================"

# 1. Sales Query
echo -e "\n1️⃣  Sales: Hot picks for CA under $5000"
curl -s -X POST "$BASE_URL/chat" \
     -H "Content-Type: application/json" \
     -d "{\"query\": \"Give me hot picks for CA under \$5000\", \"user_type\": \"internal_sales\", \"session_id\": \"$SESSION\"}" | jq '.intent, .response'

# 2. Compliance Query
echo -e "\n2️⃣  Compliance: Why SKU-1003 blocked in ID"
curl -s -X POST "$BASE_URL/chat" \
     -H "Content-Type: application/json" \
     -d "{\"query\": \"Why is SKU-1003 not available in ID? Suggest alternatives.\", \"user_type\": \"portal_customer\", \"session_id\": \"$SESSION\"}" | jq '.intent, .response'

# 3. Ops Query
echo -e "\n3️⃣  Ops: Stock for SKU-1001"
curl -s -X POST "$BASE_URL/chat" \
     -H "Content-Type: application/json" \
     -d "{\"query\": \"How much stock does SKU-1001 have and where?\", \"user_type\": \"internal_sales\", \"session_id\": \"$SESSION\"}" | jq '.intent, .response'

# 4. Vendor Query
echo -e "\n4️⃣  Vendor: Missing fields validation"
curl -s -X POST "$BASE_URL/chat" \
     -H "Content-Type: application/json" \
     -d "{\"query\": \"I'm uploading a product missing Net Wt and no lab report—what do I fix?\", \"user_type\": \"portal_vendor\", \"session_id\": \"$SESSION\"}" | jq '.intent, .response'

# 5. Memory Follow-Up
echo -e "\n5️⃣  Memory: Follow-up with prior context"
curl -s -X POST "$BASE_URL/chat" \
     -H "Content-Type: application/json" \
     -d "{\"query\": \"Ok add 2 of the first one to the basket\", \"user_type\": \"internal_sales\", \"session_id\": \"$SESSION\"}" | jq '.intent, .response'

# Security Test (should return 403)
echo -e "\n🔐 Security Test: Unauthorized vendor access (portal_customer)"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" -X POST "$BASE_URL/chat" \
     -H "Content-Type: application/json" \
     -d "{\"query\": \"I need to upload a vendor product\", \"user_type\": \"portal_customer\"}"

echo -e "\n✅ Demo complete! Check server logs for observability data."