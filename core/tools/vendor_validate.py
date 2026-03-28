from typing import Dict, List
from config import VENDOR_REQUIRED_FIELDS, VENDOR_REQUIRED_DOCS
from core.observability import track_tool_latency

@track_tool_latency("vendor_validate")
def vendor_validate(attributes: Dict) -> Dict:
    """
    Validates vendor product submission.
    Deterministic validation - NO LLM decisions.
    """
    missing_fields = []
    status = "PASS"
    
    # Check required fields
    for field in VENDOR_REQUIRED_FIELDS:
        if field not in attributes or attributes[field] is None:
            missing_fields.append(field)
    
    # Check lab report
    if attributes.get("lab_report_attached") == False:
        missing_fields.append("lab_report")
    
    # Determine status
    if len(missing_fields) > 0:
        status = "FAIL" if len(missing_fields) >= 2 else "REVIEW"
    
    return {
        "status": status,
        "missing_fields": missing_fields,
        "required_documents": VENDOR_REQUIRED_DOCS,
        "fixes": [f"Provide {field}" for field in missing_fields]
    }