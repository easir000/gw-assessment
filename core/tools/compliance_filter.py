# core/tools/compliance_filter.py

import json
from config import COMPLIANCE_RULES
from core.observability import track_tool_latency

@track_tool_latency("compliance_filter")
def compliance_filter(state: dict, product_ids: list) -> list[dict]:
    """
    Deterministic compliance check.
    Handles both int and string product_ids for compatibility.
    """
    with open("seed_data.json", "r") as f:
        data = json.load(f)
    
    results = []
    customer_state = state.get("customer_state", "TX")
    
    for pid in product_ids:
        # Convert to int for matching (official data uses int product_id)
        pid_int = int(pid) if isinstance(pid, str) and pid.isdigit() else pid
        
        # Search by product_id (int) or sku (string)
        product = None
        for p in data["products"]:
            if p["product_id"] == pid_int or p.get("sku", "").upper() == str(pid).upper():
                product = p
                break
        
        if not product:
            results.append({
                "product_id": str(pid),
                "status": "review",
                "reason_code": "NOT_FOUND",
                "alternatives": []
            })
            continue
        
        category = product.get("category", "")
        status = "allowed"
        reason_code = "OK"
        alternatives = []
        
        # Check category-based compliance rules
        if category in COMPLIANCE_RULES:
            rule = COMPLIANCE_RULES[category]
            if customer_state in rule.get("blocked_states", []):
                status = "blocked"
                reason_code = rule["reason_code"]
                # Find allowed alternatives in same category
                alternatives = [
                    str(p["product_id"]) for p in data["products"]
                    if p["category"] == category
                    and customer_state not in p.get("blocked_states", [])
                    and p["product_id"] != product["product_id"]
                ][:3]
        
        # Check product-level blocks (blocked_states array in product)
        if status == "allowed" and customer_state in product.get("blocked_states", []):
            status = "blocked"
            reason_code = "PRODUCT_BLOCK"
            # Find alternatives
            alternatives = [
                str(p["product_id"]) for p in data["products"]
                if p["category"] == category
                and customer_state not in p.get("blocked_states", [])
            ][:3]
        
        # Check lab report requirement (using flags.thc or flags.mushroom)
        flags = product.get("flags", {})
        lab_report_required = product.get("lab_report_required", False)
        lab_report_attached = product.get("lab_report_attached", True)
        
        if status == "allowed" and lab_report_required and not lab_report_attached:
            status = "review"
            reason_code = "MISSING_LAB_REPORT"
        
        results.append({
            "product_id": str(product["product_id"]),
            "sku": product.get("sku", ""),
            "name": product["name"],
            "status": status,
            "reason_code": reason_code,
            "alternatives": alternatives
        })
    
    return results