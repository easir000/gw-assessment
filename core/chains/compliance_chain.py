from typing import List  # ← ADD THIS IMPORT
from core.tools.compliance_filter import compliance_filter
from core.tools.stock_by_warehouse import stock_by_warehouse
from core.observability import track_tool_latency

@track_tool_latency("compliance_chain")
def run_compliance_chain(state: dict, product_ids: List[str]) -> dict:
    """
    Chain B: Compliance - Why blocked + alternatives
    Flow: compliance_filter -> return reasons + alternatives
    """
    # Get compliance results
    compliance_results = compliance_filter(state, product_ids)
    
    # Get stock info for alternatives
    results_with_stock = []
    for result in compliance_results:
        if result["status"] != "allowed" and result["alternatives"]:
            # Get stock for alternatives
            alt_stock = []
            for alt_id in result["alternatives"]:
                stock = stock_by_warehouse(alt_id)
                alt_stock.append({"product_id": alt_id, "stock": stock})
            result["alternative_stock"] = alt_stock
        
        results_with_stock.append(result)
    
    return {
        "compliance_results": results_with_stock,
        "blocked_count": sum(1 for r in results_with_stock if r["status"] == "blocked"),
        "review_count": sum(1 for r in results_with_stock if r["status"] == "review")
    }