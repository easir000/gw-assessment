import json
from typing import List, Dict
from core.observability import track_tool_latency

@track_tool_latency("kb_search")
def kb_search(query: str, top_k: int = 3) -> List[Dict]:
    """
    Naive keyword search over KB docs.
    NO embeddings/RAG for this PoC (per requirements).
    """
    with open("seed_data.json", "r") as f:
        data = json.load(f)
    
    query_lower = query.lower()
    scored_docs = []
    
    for doc in data["kb_docs"]:
        # Simple keyword matching
        text_lower = doc["text"].lower()
        title_lower = doc["title"].lower()
        
        score = 0
        for word in query_lower.split():
            if len(word) > 2:  # Ignore short words
                if word in text_lower:
                    score += 2
                if word in title_lower:
                    score += 3
        
        if score > 0:
            scored_docs.append({
                "doc_id": doc["doc_id"],
                "title": doc["title"],
                "text": doc["text"][:200],  # Truncate for token efficiency
                "score": score
            })
    
    # Sort by score and return top_k
    scored_docs.sort(key=lambda x: x["score"], reverse=True)
    return scored_docs[:top_k]