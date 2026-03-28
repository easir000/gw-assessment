from typing import Dict, Any
from utils.security import sanitize_for_llm

class LLMStub:
    """
    Mock LLM for formatting responses.
    Production: Replace with OpenAI/Anthropic/Gemini.
    """
    
    def format_response(self, intent: str, tool_results: Dict[str, Any]) -> str:
        """
        Format tool results into natural language.
        LLM explains but does NOT invent facts.
        """
        # Sanitize before any LLM processing
        sanitized_results = sanitize_for_llm(tool_results)
        
        # Simple template-based formatting (swap for real LLM in production)
        if intent == "SALES_RECO":
            allowed = sanitized_results.get("allowed_picks", [])
            if allowed:
                products = ", ".join([p["name"] for p in allowed[:3]])
                return f"Based on your budget, I recommend: {products}. All items passed compliance checks."
            return "No products match your criteria after compliance filtering."
        
        elif intent == "COMPLIANCE_CHECK":
            results = sanitized_results.get("compliance_results", [])
            blocked = [r for r in results if r["status"] == "blocked"]
            if blocked:
                reasons = ", ".join([r["reason_code"] for r in blocked])
                return f"Product is restricted. Reason: {reasons}. See alternatives in response data."
            return "Product is compliant and available."
        
        elif intent == "VENDOR_ONBOARDING":
            status = sanitized_results.get("status", "UNKNOWN")
            fixes = sanitized_results.get("fixes", [])
            if status != "PASS":
                return f"Validation {status}. Required fixes: {', '.join(fixes)}"
            return "Vendor submission validated successfully."
        
        elif intent == "OPS_STOCK":
            stock = sanitized_results.get("stock_results", [])
            if stock:
                total = sum(s["qty"] for s in stock)
                warehouses = ", ".join([s["warehouse"] for s in stock])
                return f"Total stock: {total} units. Locations: {warehouses}"
            return "Product not found in inventory."
        
        return "Request processed. See structured data for details."
    
    def estimate_tokens(self, text: str) -> int:
        """Rough token estimate (4 chars ≈ 1 token)."""
        return len(text) // 4