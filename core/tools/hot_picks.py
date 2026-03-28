# core/tools/hot_picks.py

import json
from core.observability import track_tool_latency

@track_tool_latency("hot_picks")
def hot_picks(state: dict, budget: float, limit: int = 5) -> list[dict]:
    """
    Returns ranked products within budget.
    Handles float popularity_score (0.0-1.0) from official data.
    """
    with open("seed_data.json", "r") as f:
        data = json.load(f)
    
    # Filter by budget
    candidates = [p for p in data["products"] if p["price"] <= budget]
    
    # Sort by popularity (float 0.0-1.0, higher is better)
    candidates.sort(key=lambda x: x["popularity_score"], reverse=True)
    
    # Return minimal data (token efficiency)
    return [
        {
            "product_id": str(p["product_id"]),  # Convert to string for consistency
            "sku": p.get("sku", ""),
            "name": p["name"],
            "price": p["price"],
            "popularity_score": p["popularity_score"]
        }
        for p in candidates[:limit]
    ]