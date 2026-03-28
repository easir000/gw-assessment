"""
Security & Permissions Module
=============================
Handles:
- Tool allowlist enforcement by user_type
- PII redaction before LLM processing
- Audit logging helpers for production

Updated for Official GW seed_data.json
"""

import re
import time
import hashlib
from typing import Any, Dict, List
from config import TOOL_ALLOWLIST, UserType


# ============================================================================
# Tool Permission Enforcement
# ============================================================================

def check_tool_permission(user_type: UserType, tool_name: str) -> bool:
    """
    Check if a user_type is allowed to access a specific tool.
    
    Args:
        user_type: The user's role (internal_sales, portal_vendor, portal_customer)
        tool_name: The tool being accessed (e.g., 'vendor_validate')
    
    Returns:
        True if allowed, False if denied
    
    Examples:
        >>> check_tool_permission("portal_customer", "vendor_validate")
        False
        >>> check_tool_permission("internal_sales", "vendor_validate")
        True
    """
    allowed_tools = TOOL_ALLOWLIST.get(user_type, [])
    return tool_name in allowed_tools


def get_allowed_tools(user_type: UserType) -> List[str]:
    """
    Get list of tools allowed for a specific user_type.
    
    Args:
        user_type: The user's role
    
    Returns:
        List of allowed tool names
    """
    return TOOL_ALLOWLIST.get(user_type, [])


def validate_user_type(user_type: str) -> bool:
    """
    Validate that user_type is one of the allowed values.
    
    Args:
        user_type: The user type string to validate
    
    Returns:
        True if valid, False otherwise
    """
    valid_types = ["internal_sales", "portal_vendor", "portal_customer"]
    return user_type in valid_types


# ============================================================================
# PII Redaction (Before LLM Processing)
# ============================================================================

def redact_pii(text: str) -> str:
    """
    Redact Personally Identifiable Information (PII) from text.
    
    Updated for Official GW Data:
    - Customer names (Retailer 501, etc.)
    - Email addresses
    - Phone numbers
    - SSN, Credit Cards
    
    This is critical for compliance (GDPR, CCPA, HIPAA) before sending
    any data to external LLM providers.
    
    Args:
        text: Input text that may contain PII
    
    Returns:
        Text with PII replaced by redaction markers
    
    Examples:
        >>> redact_pii("Contact john@example.com")
        'Contact [EMAIL_REDACTED]'
        >>> redact_pii("Retailer 501 placed an order")
        '[CUSTOMER_REDACTED] placed an order'
    """
    if not isinstance(text, str):
        return str(text)
    
    # Customer names from official GW data (e.g., "Retailer 501", "Retailer 502")
    text = re.sub(r'\bRetailer \d+\b', '[CUSTOMER_REDACTED]', text)
    
    # Email addresses
    text = re.sub(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        '[EMAIL_REDACTED]',
        text
    )
    
    # Phone numbers (US formats: 555-123-4567, 555.123.4567, 5551234567)
    text = re.sub(
        r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        '[PHONE_REDACTED]',
        text
    )
    
    # Social Security Numbers (XXX-XX-XXXX)
    text = re.sub(
        r'\b\d{3}-\d{2}-\d{4}\b',
        '[SSN_REDACTED]',
        text
    )
    
    # Credit Card numbers (XXXX-XXXX-XXXX-XXXX or with spaces)
    text = re.sub(
        r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
        '[CC_REDACTED]',
        text
    )
    
    return text


def sanitize_for_llm(payload: Any) -> Any:
    """
    Recursively sanitize all string values in a payload before LLM processing.
    
    This ensures no PII leaks to external LLM providers, even in nested
    data structures.
    
    Args:
        payload: Any data structure (dict, list, str, etc.)
    
    Returns:
        Sanitized data structure with all PII redacted
    
    Examples:
        >>> sanitize_for_llm({"email": "user@example.com", "name": "John"})
        {'email': '[EMAIL_REDACTED]', 'name': 'John'}
    """
    if isinstance(payload, dict):
        return {k: sanitize_for_llm(v) for k, v in payload.items()}
    elif isinstance(payload, list):
        return [sanitize_for_llm(item) for item in payload]
    elif isinstance(payload, str):
        return redact_pii(payload)
    elif isinstance(payload, (int, float, bool, type(None))):
        return payload
    else:
        # For any other type, convert to string and redact
        return redact_pii(str(payload))


# ============================================================================
# Audit Logging Helpers (Production)
# ============================================================================

def get_audit_log_entry(
    request_id: str,
    user_type: str,
    tool_name: str,
    action: str,
    status: str = "success"
) -> Dict[str, Any]:
    """
    Create a structured audit log entry for production monitoring.
    
    This is used for compliance auditing, security investigations,
    and debugging production issues.
    
    Args:
        request_id: Unique request identifier
        user_type: User role making the request
        tool_name: Tool being accessed
        action: Action performed (e.g., "execute", "denied")
        status: Outcome (success, failure, denied)
    
    Returns:
        Dictionary with audit log fields
    """
    # Create immutable hash for integrity verification
    audit_hash = hashlib.sha256(
        f"{request_id}{tool_name}{action}{time.time()}".encode()
    ).hexdigest()[:16]
    
    return {
        "request_id": request_id,
        "user_type": user_type,
        "tool": tool_name,
        "action": action,
        "status": status,
        "timestamp": time.time(),
        "audit_hash": audit_hash
    }


def log_permission_denied(
    request_id: str,
    user_type: str,
    tool_name: str
) -> Dict[str, Any]:
    """
    Create audit log entry for permission denied events.
    
    Important for security monitoring and detecting potential abuse.
    
    Args:
        request_id: Unique request identifier
        user_type: User role that was denied
        tool_name: Tool they tried to access
    
    Returns:
        Audit log entry for denied access
    """
    return get_audit_log_entry(
        request_id=request_id,
        user_type=user_type,
        tool_name=tool_name,
        action="access_attempt",
        status="denied"
    )


def log_tool_execution(
    request_id: str,
    user_type: str,
    tool_name: str,
    latency_ms: int
) -> Dict[str, Any]:
    """
    Create audit log entry for successful tool execution.
    
    Used for performance monitoring and usage analytics.
    
    Args:
        request_id: Unique request identifier
        user_type: User role that executed the tool
        tool_name: Tool that was executed
        latency_ms: Execution time in milliseconds
    
    Returns:
        Audit log entry for tool execution
    """
    entry = get_audit_log_entry(
        request_id=request_id,
        user_type=user_type,
        tool_name=tool_name,
        action="execute",
        status="success"
    )
    entry["latency_ms"] = latency_ms
    return entry


# ============================================================================
# Security Constants (Production)
# ============================================================================

# Maximum request size (bytes)
MAX_REQUEST_SIZE = 1024 * 1024  # 1MB

# Rate limiting (requests per minute per user)
RATE_LIMIT_PER_MINUTE = 60

# Session timeout (seconds)
SESSION_TIMEOUT_SECONDS = 1800  # 30 minutes

# Allowed IP ranges (for production deployment)
# ALLOWED_IP_RANGES = ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]


# ============================================================================
# Security Validation Helpers
# ============================================================================

def validate_request_size(payload: Dict) -> bool:
    """
    Validate that request payload doesn't exceed maximum size.
    
    Prevents DoS attacks via large payloads.
    
    Args:
        payload: Request payload dictionary
    
    Returns:
        True if within limits, False if too large
    """
    import sys
    size = sys.getsizeof(str(payload))
    return size <= MAX_REQUEST_SIZE


def is_safe_input(text: str) -> bool:
    """
    Basic input validation to prevent injection attacks.
    
    Checks for common injection patterns.
    
    Args:
        text: User input string
    
    Returns:
        True if safe, False if potentially malicious
    """
    if not isinstance(text, str):
        return False
    
    # Check for SQL injection patterns
    sql_patterns = ["DROP TABLE", "DELETE FROM", "INSERT INTO", "--", ";"]
    for pattern in sql_patterns:
        if pattern.upper() in text.upper():
            return False
    
    # Check for script injection
    if "<script" in text.lower() or "javascript:" in text.lower():
        return False
    
    return True