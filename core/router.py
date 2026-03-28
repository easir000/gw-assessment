"""
Intent Router Module
====================
Updated for Official GW seed_data.json

Keyword-based intent classification with support for all states in official data.
"""

from typing import Literal
import re

Intent = Literal["SALES_RECO", "COMPLIANCE_CHECK", "VENDOR_ONBOARDING", "OPS_STOCK", "GENERAL_KB"]

KEYWORD_MAP = {
    "SALES_RECO": ["hot picks", "recommend", "budget", "under $", "top products", "best sellers"],
    "COMPLIANCE_CHECK": ["legal", "blocked", "why not", "compliance", "restricted", "available in", "not available", "why is"],
    "VENDOR_ONBOARDING": ["onboard", "upload", "missing", "vendor", "validate", "checklist", "requirements"],
    "OPS_STOCK": ["stock", "inventory", "warehouse", "qty", "quantity", "available", "how much"],
    "GENERAL_KB": ["help", "policy", "how to", "documentation", "SOP", "shipping", "return"],
}

def classify_intent(query: str) -> Intent:
    """Cheap keyword-based intent classification. NO LLM call for routing."""
    query_lower = query.lower()
    intent_scores = {}
    for intent, keywords in KEYWORD_MAP.items():
        score = sum(1 for kw in keywords if kw in query_lower)
        intent_scores[intent] = score
    
    if max(intent_scores.values()) > 0:
        return max(intent_scores, key=intent_scores.get)
    return "GENERAL_KB"


def extract_product_id(query: str) -> str | None:
    """Extract SKU/product ID from query using regex."""
    match = re.search(r'SKU-\d+', query, re.IGNORECASE)
    if match:
        return match.group(0).upper()
    # Also try to find standalone numbers (official data uses int product_id)
    match = re.search(r'\b(\d{4})\b', query)
    if match:
        return match.group(1)
    return None


def extract_budget(query: str) -> float:
    """Extract budget amount from query."""
    match = re.search(r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', query)
    if match:
        return float(match.group(1).replace(',', ''))
    return 5000.0


def extract_state(query: str) -> str:
    """Extract state code from query. Updated for all official GW states."""
    states = [
        "CA", "NV", "AZ", "TX", "CO", "IL", "GA", "WA", "NY", 
        "ID", "UT", "WI", "MA", "FL"
    ]
    query_upper = query.upper()
    for state in states:
        if f" {state}" in query_upper or f"{state} " in query_upper or query_upper.endswith(state):
            return state
    return "TX"  # Default