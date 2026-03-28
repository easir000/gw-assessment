from typing import Dict, Optional, List
import uuid

class SessionState:
    """
    Minimal in-memory session state for follow-up questions.
    Production: Replace with Redis for scalability.
    """
    
    def __init__(self):
        self.sessions: Dict[str, dict] = {}
    
    def get_or_create(self, session_id: str) -> dict:
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "last_intent": None,
                "last_state": None,
                "last_budget": None,
                "last_product_ids": [],
                "last_results": None,
            }
        return self.sessions[session_id]
    
    def update(self, session_id: str, **kwargs):
        state = self.get_or_create(session_id)
        state.update(kwargs)
        return state
    
    def clear(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]

# Global session store
session_store = SessionState()