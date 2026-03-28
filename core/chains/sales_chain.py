from core.tools.hot_picks import hot_picks
from core.tools.compliance_filter import compliance_filter
from core.observability import track_tool_latency

@track_tool_latency("sales_chain")
def run_sales_chain(state: dict, budget: float, limit: int = 5) -> dict:
    """
    Chain A: Sales - Hot picks under budget
    Flow: hot_picks -> compliance_filter -> final response
    """
    # Step 1: Get hot picks
    picks = hot_picks(state, budget, limit)
    product_ids = [p["product_id"] for p in picks]
    
    # Step 2: Compliance filter (CRITICAL: gate before recommendation)
    compliance_results = compliance_filter(state, product_ids)
    
    # Step 3: Filter out blocked items (compliance gating)
    allowed_picks = []
    blocked_picks = []
    for i, pick in enumerate(picks):
        compliance = next((c for c in compliance_results if c["product_id"] == pick["product_id"]), None)
        if compliance and compliance["status"] == "allowed":
            allowed_picks.append({**pick, "compliance_status": "allowed"})
        elif compliance:
            blocked_picks.append({**pick, "compliance_status": compliance["status"], "reason": compliance["reason_code"]})
    
    return {
        "allowed_picks": allowed_picks,
        "blocked_picks": blocked_picks,
        "total_picks": len(picks),
        "allowed_count": len(allowed_picks)
    }