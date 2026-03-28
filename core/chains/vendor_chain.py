from core.tools.vendor_validate import vendor_validate
from core.observability import track_tool_latency

@track_tool_latency("vendor_chain")
def run_vendor_chain(attributes: dict) -> dict:
    """
    Chain C: Vendor onboarding validation
    Flow: vendor_validate -> return checklist and status
    """
    validation = vendor_validate(attributes)
    
    return {
        "status": validation["status"],
        "missing_fields": validation["missing_fields"],
        "required_documents": validation["required_documents"],
        "fixes": validation["fixes"],
        "next_steps": "Submit missing information" if validation["status"] != "PASS" else "Proceed to approval"
    }