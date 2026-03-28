"""
Compliance Verification Script
==============================
Verifies COMPLIANCE_RULES match actual blocked_states in seed_data.json

Run: python tests/verify_compliance.py
"""

import json

def verify_compliance_rules():
    """Verify COMPLIANCE_RULES match actual blocked_states in seed_data.json."""
    
    with open("seed_data.json", "r") as f:
        data = json.load(f)
    
    from config import COMPLIANCE_RULES
    
    print("=" * 80)
    print("🔍 Verifying Compliance Rules vs seed_data.json")
    print("=" * 80)
    
    # Group products by category
    categories = {}
    for product in data["products"]:
        cat = product["category"]
        if cat not in categories:
            categories[cat] = {"blocked_states": set(), "products": [], "count": 0}
        categories[cat]["blocked_states"].update(product.get("blocked_states", []))
        categories[cat]["products"].append(product.get("sku", str(product["product_id"])))
        categories[cat]["count"] += 1
    
    # Compare with COMPLIANCE_RULES
    all_match = True
    for category, rule in COMPLIANCE_RULES.items():
        if category in categories:
            actual_blocks = categories[category]["blocked_states"]
            rule_blocks = set(rule.get("blocked_states", []))
            
            if actual_blocks == rule_blocks:
                print(f"✅ {category}: {rule_blocks} ({categories[category]['count']} products)")
            else:
                print(f"⚠️  {category}: MISMATCH")
                print(f"   Rule says: {rule_blocks}")
                print(f"   Data has: {actual_blocks}")
                all_match = False
        else:
            print(f"⚠️  {category}: Not in seed_data")
    
    print("=" * 80)
    if all_match:
        print("🎉 All compliance rules match seed_data.json!")
    else:
        print("❌ Some rules need adjustment")
    print("=" * 80)
    
    # Print category summary
    print("\n📊 Category Summary:")
    for cat, info in categories.items():
        print(f"   {cat}: {info['count']} products, blocked in {info['blocked_states'] if info['blocked_states'] else 'None'}")
    
    return all_match


if __name__ == "__main__":
    verify_compliance_rules()