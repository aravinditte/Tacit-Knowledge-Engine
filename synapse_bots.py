
class DecisionClarificationBot:
    """A bot that prompts users to clarify the reasoning behind their actions."""
    
    def analyze_event_and_prompt(self, event_node):
        """Analyzes a graph event node and returns a clarification prompt if applicable."""
        
        # Check if the event is a resolution and hasn't been clarified yet.
        if event_node['decision_type'] == "Resolution" and not event_node.get('clarification'):
            prompt = "I see this issue was resolved. To improve our knowledge base, what was the primary solution category?"
            options = ["", "Code Hotfix", "Configuration Change", "Manual Data Correction", "User Training"]
            return {"prompt": prompt, "options": options, "event_id": event_node['id']}
            
        return None 