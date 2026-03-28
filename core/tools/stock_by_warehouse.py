# core/tools/stock_by_warehouse.py

import json
from core.observability import track_tool_latency

@track_tool_latency("stock_by_warehouse")
def stock_by_warehouse(product_id: str) -> list[dict]:
    """
    Returns inventory levels by warehouse.
    Handles both int and string product_id.
    """
    with open("seed_data.json", "r") as f:
        data = json.load(f)
    
    # Convert to int for matching
    pid_int = int(product_id) if isinstance(product_id, str) and product_id.isdigit() else product_id
    
    inventory = [
        inv for inv in data["inventory"]
        if inv["product_id"] == pid_int
    ]
    
    # Return minimal data
    return [
        {
            "warehouse": inv["warehouse"],
            "qty": inv["qty"],
            "available": inv["qty"] > 0
        }
        for inv in inventory
    ]