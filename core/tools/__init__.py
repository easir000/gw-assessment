# Tools module initialization

import os
import json

def load_seed_data():
    """Load seed_data.json with graceful fallback."""
    path = os.path.join(os.path.dirname(__file__), "../../seed_data.json")
    if not os.path.exists(path):
        # Return minimal stub for testing
        return {"products": [], "inventory": [], "customers": [], "vendors": [], "kb_docs": []}
    with open(path, "r") as f:
        return json.load(f)