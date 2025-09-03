from sentence_transformers import SentenceTransformer
import time
import uuid

class WorkflowWeaver:
    """Processes raw data into structured workflow events and extracts decision points."""

    def __init__(self):
        print("Loading semantic model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Semantic model loaded.")

    def _get_embedding(self, text):
        return self.model.encode(text).tolist()

    def _extract_decision_point(self, text):
        """Simulated LLM analysis to determine the 'why' behind an action."""
        text_lower = text.lower()
        if "confirm" in text_lower or "looks like" in text_lower or "root cause" in text_lower:
            return {"type": "Triage", "reason": "Identifying root cause."}
        if "pinging" in text_lower or "@" in text_lower or "escalate" in text_lower:
            return {"type": "Escalation", "reason": "Involving another team member."}
        if "applying" in text_lower or "resolved" in text_lower or "fixed" in text_lower:
            return {"type": "Resolution", "reason": "Implementing a fix."}
        return {"type": "Discussion", "reason": "General comment."}

    def process_log_entry(self, log_data, user_role):
        """Processes a single log entry as a workflow event, including the user's role."""
        text = log_data.get('text', '')
        decision = self._extract_decision_point(text)
        
        event_props = {
            "id": str(uuid.uuid4()),
            "timestamp": int(time.time()),
            "source": log_data.get('source'),
            "user": log_data.get('user_name'),
            "user_role": user_role,
            "text": text,
            "decision_type": decision['type'],
            "reasoning": decision['reason'],
            "embedding": self._get_embedding(text)
        }
        
        chain_id = log_data.get('ticket_id')
        return chain_id, event_props