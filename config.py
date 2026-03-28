"""
Configuration Module
====================
Updated for Official GW seed_data.json

Compliance rules match actual blocked_states in the official data.
"""

from typing import Literal

UserType = Literal["internal_sales", "portal_vendor", "portal_customer"]

# Security: Tool Allowlist by user_type
TOOL_ALLOWLIST: dict[UserType, list[str]] = {
    "internal_sales": ["hot_picks", "compliance_filter", "stock_by_warehouse", "vendor_validate", "kb_search"],
    "portal_vendor": ["compliance_filter", "stock_by_warehouse", "vendor_validate", "kb_search"],
    "portal_customer": ["hot_picks", "compliance_filter", "stock_by_warehouse", "kb_search"],
}

# Compliance Rules (Updated for Official GW Data)
# Based on actual blocked_states in seed_data.json
COMPLIANCE_RULES = {
    # THC Beverages: Blocked in ID, UT (per seed_data: SKU-1003, 1005, 1023, 1026, 1034, 1047, 1058)
    "THC Beverage": {"blocked_states": ["ID", "UT"], "reason_code": "STATE_RESTRICTION"},
    
    # Nicotine Vapes: Blocked in MA (per seed_data: SKU-1002)
    "Nicotine Vape": {"blocked_states": ["MA"], "reason_code": "FLAVOR_BAN"},
    
    # Mushroom Gummies: Blocked in CA, NY (per seed_data: SKU-1031, 1041)
    "Mushroom Gummies": {"blocked_states": ["CA", "NY"], "reason_code": "PSYCHEDELIC_RESTRICTION"},
    
    # Kratom: Blocked in WI (per seed_data: SKU-1042)
    "Kratom": {"blocked_states": ["WI"], "reason_code": "KRATOM_RESTRICTION"},
    
    # CBD Tincture: Generally legal (no blocks in seed_data)
    "CBD Tincture": {"blocked_states": [], "reason_code": "OK"},
    
    # Accessories: No restrictions
    "Accessories": {"blocked_states": [], "reason_code": "OK"},
}

# Required documents for vendor onboarding
VENDOR_REQUIRED_DOCS = ["COA", "Insurance Certificate", "Business License"]

# Vendor validation required fields (per SOP-VENDOR-UPLOAD)
VENDOR_REQUIRED_FIELDS = ["name", "category", "net_wt_oz", "lab_report_attached"]

# All valid states in seed_data.json (for extraction)
VALID_STATES = [
    "CA", "NV", "AZ", "TX", "CO", "IL", "GA", "WA", "NY", 
    "ID", "UT", "WI", "MA", "FL"
]