# Core Web Framework
fastapi==0.109.0
uvicorn==0.27.0
python-multipart==0.0.6

# Data Validation
pydantic==2.5.0

# Testing & Evaluation
pytest==7.4.0
httpx==0.26.0

# Observability (Optional stub included, uncomment if using Langfuse)
# langfuse==2.20.0

# Python Version: 3.9+


# GW Assessment: Odoo + AI/LLM Engineer PoC

## 🚀 How to Run
1. Install deps: `pip install -r requirements.txt`
2. Start server: `uvicorn main:app --reload`
3. Test endpoint: `POST http://127.0.0.1:8000/chat`

## 🏗️ Architecture
- **Router:** Keyword-based intent classification (Low token cost).
- **Tools:** Deterministic Python functions reading `seed_data.json`.
- **Security:** `user_type` enforce allowlists in `config.py`.
- **Observability:** Structured JSON logs in `core/observability.py`.

## 🛡️ Compliance & Integrity
- **No Hallucinations:** Live facts come from tools, not LLM.
- ** gating:** `compliance_filter` blocks restricted items before recommendation.
- **PII:** No PII sent to LLM (stubbed in `utils/security.py`).



## 🛣️ Production Roadmap (Post-PoC)

### Phase 2: Advanced Orchestration
- [ ] Migrate to **LangGraph** for state machine routing and execution
- [ ] Add **Redis** for distributed caching (replace in-memory cache)
- [ ] Implement **circuit breakers** for tool call failures
- [ ] Add **Langfuse** integration for production observability
- [ ] Deploy to **Kubernetes** with auto-scaling

### Why Not in PoC?
This PoC prioritizes **simplicity and clarity** over advanced orchestration.
The current architecture is designed to be **LangGraph-compatible** - the
chain structure (`core/chains/`) can be migrated to LangGraph state machines
without changing tool implementations.



## 🔄 Production LLM Integration

The current `LLMStub` can be replaced with a real provider:

```python
# utils/llm_production.py (example)
from openai import OpenAI

class LLMProduction:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
    
    def format_response(self, intent: str, tool_results: dict) -> str:
        # Sanitize FIRST (critical)
        sanitized = sanitize_for_llm(tool_results)
        
        # Construct minimal prompt
        prompt = f"Intent: {intent}\nFacts: {json.dumps(sanitized)}\nExplain concisely:"
        
        # Call LLM with strict parameters
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,  # Bounded output
            temperature=0.1   # Deterministic formatting
        )
        return response.choices[0].message.content