"""
GW Assessment: Odoo + AI/LLM Engineer PoC
Main FastAPI Application Entry Point
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Optional, Literal
from pydantic import BaseModel, Field
import time
import json
import logging

from config import UserType, TOOL_ALLOWLIST
from core.router import classify_intent, extract_product_id, extract_budget, extract_state
from core.state import session_store
from core.observability import ObservabilityTracker
from core.chains.sales_chain import run_sales_chain
from core.chains.compliance_chain import run_compliance_chain
from core.chains.vendor_chain import run_vendor_chain
from core.tools.stock_by_warehouse import stock_by_warehouse
from core.tools.kb_search import kb_search
from utils.security import check_tool_permission, sanitize_for_llm
from utils.llm_stub import LLMStub

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gw_assessment")

# ============================================================================
# FastAPI Application Setup
# ============================================================================

app = FastAPI(
    title="GW Assessment - Odoo + AI/LLM Engineer PoC",
    description="Tool-first AI orchestration layer over ERP",
    version="1.0.0",
    docs_url="/docs",        # Swagger UI (enabled by default)
    redoc_url="/redoc",      # ReDoc (explicitly enable)
    openapi_url="/openapi.json"  # OpenAPI schema
)

llm = LLMStub()

# ============================================================================
# Request/Response Models
# ============================================================================

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    user_type: UserType = Field(default="portal_customer")
    session_id: Optional[str] = Field(default="default")

class ChatResponse(BaseModel):
    request_id: str
    intent: Literal["SALES_RECO", "COMPLIANCE_CHECK", "VENDOR_ONBOARDING", "OPS_STOCK", "GENERAL_KB"]
    response: str
    data: dict
    session_id: str
    user_type: UserType

class HealthResponse(BaseModel):
    status: str
    service: str

# ============================================================================
# Custom Exception Handler (CRITICAL for 403 vs 500)
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTPException with proper status codes."""
    logger.warning(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions - log but don't expose details."""
    logger.exception(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# ============================================================================
# API Endpoints
# ============================================================================

@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint with tool-first orchestration."""
    
    # Extract request fields
    query = request.query
    user_type = request.user_type
    session_id = request.session_id or "default"
    
    # 1. Initialize observability
    obs = ObservabilityTracker(user_type=user_type, query=query)
    
    # 2. Get session state
    state = session_store.get_or_create(session_id)
    
    # 3. Classify intent
    intent = classify_intent(query)
    obs.intent = intent
    
    # 4. Extract parameters
    product_id = extract_product_id(query)
    budget = extract_budget(query)
    customer_state = extract_state(query)
    state["customer_state"] = customer_state
    
    # 5. Execute chains with permission checks
    response_data = {}
    
    # === SALES_RECO ===
    if intent == "SALES_RECO":
        if not check_tool_permission(user_type, "hot_picks"):
            obs.finalize(intent=intent, status="error:unauthorized", token_estimate=0)
            raise HTTPException(status_code=403, detail="Unauthorized: portal_customer cannot access hot_picks")
        
        response_data = run_sales_chain(state, budget, limit=5)
        state["last_intent"] = intent
        state["last_budget"] = budget
        state["last_product_ids"] = [p["product_id"] for p in response_data.get("allowed_picks", [])]
    
    # === COMPLIANCE_CHECK ===
    elif intent == "COMPLIANCE_CHECK":
        if not check_tool_permission(user_type, "compliance_filter"):
            obs.finalize(intent=intent, status="error:unauthorized", token_estimate=0)
            raise HTTPException(status_code=403, detail="Unauthorized: tool not allowed for this user_type")
        
        product_ids = [product_id] if product_id else state.get("last_product_ids", [])
        if not product_ids:
            obs.finalize(intent=intent, status="error:no_product", token_estimate=0)
            raise HTTPException(status_code=400, detail="No product ID found")
        
        response_data = run_compliance_chain(state, product_ids)
        state["last_intent"] = intent
    
    # === VENDOR_ONBOARDING ===
    elif intent == "VENDOR_ONBOARDING":
        # CRITICAL: Permission check BEFORE any processing
        if not check_tool_permission(user_type, "vendor_validate"):
            obs.finalize(intent=intent, status="error:unauthorized", token_estimate=0)
            raise HTTPException(status_code=403, detail="Unauthorized: portal_customer cannot access vendor_validate")
        
        attributes = {
            "name": "Example Product",
            "category": "THC Beverage",
            "net_wt_oz": None,
            "lab_report_attached": False
        }
        response_data = run_vendor_chain(attributes)
        state["last_intent"] = intent
    
    # === OPS_STOCK ===
    elif intent == "OPS_STOCK":
        if not check_tool_permission(user_type, "stock_by_warehouse"):
            obs.finalize(intent=intent, status="error:unauthorized", token_estimate=0)
            raise HTTPException(status_code=403, detail="Unauthorized: tool not allowed for this user_type")
        
        if not product_id:
            obs.finalize(intent=intent, status="error:no_product", token_estimate=0)
            raise HTTPException(status_code=400, detail="Product ID required")
        
        stock = stock_by_warehouse(product_id)
        response_data = {
            "product_id": product_id,
            "stock_results": stock,
            "total_qty": sum(s["qty"] for s in stock)
        }
        state["last_intent"] = intent
    
    # === GENERAL_KB ===
    elif intent == "GENERAL_KB":
        if not check_tool_permission(user_type, "kb_search"):
            obs.finalize(intent=intent, status="error:unauthorized", token_estimate=0)
            raise HTTPException(status_code=403, detail="Unauthorized: tool not allowed for this user_type")
        
        results = kb_search(query, top_k=3)
        response_data = {"kb_results": results, "query": query}
    
    # === FALLBACK ===
    else:
        response_data = {"message": "Intent not recognized"}
        results = kb_search(query, top_k=2)
        response_data["kb_results"] = results
    
    # 6. Format response
    formatted_text = llm.format_response(intent, response_data)
    token_estimate = llm.estimate_tokens(formatted_text)
    
    # 7. Finalize observability
    obs.finalize(intent=intent, status="success", token_estimate=token_estimate)
    
    # 8. Return response
    return ChatResponse(
        request_id=obs.request_id,
        intent=intent,
        response=formatted_text,
        data=sanitize_for_llm(response_data),
        session_id=session_id,
        user_type=user_type
    )

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    return HealthResponse(status="healthy", service="gw-assessment-poc")

@app.get("/debug/routes", tags=["Debug"])
async def debug_routes():
    return {
        "routes": [{"path": r.path, "methods": list(r.methods)} for r in app.routes if hasattr(r, "path")],
        "total_routes": len([r for r in app.routes if hasattr(r, "path")])
    }

# ============================================================================
# Run Instructions
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)