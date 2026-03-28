import logging
import json
import time
import uuid
import functools
from typing import Optional

# Configure structured JSON logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger("gw_assessment")

class ObservabilityTracker:
    def __init__(self, user_type: str, query: str):
        self.request_id = str(uuid.uuid4())
        self.user_type = user_type
        self.query = query
        self.start_time = time.perf_counter()
        self.tool_calls = []
        self.intent = None
    
    def log_tool_call(self, tool_name: str, args: dict, latency_ms: int):
        """Log individual tool call with timing."""
        self.tool_calls.append({
            "tool": tool_name,
            "args": {k: str(v)[:50] for k, v in args.items()},  # Truncate for privacy
            "latency_ms": latency_ms
        })
        
        # Structured log entry
        log_entry = {
            "event": "tool_call",
            "request_id": self.request_id,
            "user_type": self.user_type,
            "intent": self.intent,
            "tool": tool_name,
            "latency_ms": latency_ms,
            "timestamp": time.time()
        }
        logger.info(json.dumps(log_entry))
    
    def finalize(self, intent: str, status: str = "success", token_estimate: int = 0):
        """Log request completion with summary."""
        total_latency_ms = int((time.perf_counter() - self.start_time) * 1000)
        
        log_entry = {
            "event": "request_complete",
            "request_id": self.request_id,
            "user_type": self.user_type,
            "intent": intent,
            "tools_called": [t["tool"] for t in self.tool_calls],
            "total_latency_ms": total_latency_ms,
            "tool_count": len(self.tool_calls),
            "token_estimate": token_estimate,
            "status": status,
            "timestamp": time.time()
        }
        logger.info(json.dumps(log_entry))
        
        return log_entry

def track_tool_latency(tool_name: str):
    """Decorator to automatically track tool execution time."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                latency_ms = int((time.perf_counter() - start) * 1000)
                # Log to console (in production, send to Langfuse/monitoring)
                log_entry = {
                    "event": "tool_call",
                    "tool": tool_name,
                    "latency_ms": latency_ms,
                    "timestamp": time.time()
                }
                logger.info(json.dumps(log_entry))
        return wrapper
    return decorator