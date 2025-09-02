import re

class Weaver:
    """Processes raw data to extract keywords and structured information."""

    def _extract_keywords(self, text):
        """
        Simulated NLP: Extracts potential keywords from text.
        Keywords are considered to be single-quoted phrases or capitalized words.
        """
        # This regex finds words inside single quotes or capitalized words (like proper nouns).
        keywords = re.findall(r"\'(.*?)\'|\b[A-Z][a-zA-Z]+\b", text)
        # We clean up the list, removing empty strings that the regex might produce.
        return [kw for kw in keywords if kw]

    def process_event(self, event_data):
        """Processes a single event, standardizes the data, and prepares it for the DKG."""
        event_type = event_data.get('type')
        processed = {'nodes': [], 'rels': []}

        # Ensure a User node is always created for the person who triggered the event.
        user_email = event_data['user_email']
        user_props = {'email': user_email, 'name': event_data['user_name']}
        processed['nodes'].append({'label': 'User', 'props': user_props})

        # Extract and standardize keywords from any text in the event.
        text_content = event_data.get('text', '')
        keywords = self._extract_keywords(text_content)
        
        # --- Process event based on its type ---
        if event_type == 'jira_comment':
            ticket_id = event_data['ticket_id']
            ticket_props = {'id': ticket_id, 'summary': event_data['summary']}
            processed['nodes'].append({'label': 'Ticket', 'props': ticket_props})
            
            # Create relationship: (User)-[:COMMENTS_ON]->(Ticket)
            processed['rels'].append({'from': ('User', user_email), 'to': ('Ticket', ticket_id), 'type': 'COMMENTS_ON'})
            
            # Create relationships for each keyword: (Ticket)-[:MENTIONS]->(Keyword)
            for kw in keywords:
                # **THE FIX**: Standardize keyword to lowercase for consistency.
                kw_lower = kw.lower()
                kw_props = {'term': kw_lower}
                processed['nodes'].append({'label': 'Keyword', 'props': kw_props})
                processed['rels'].append({'from': ('Ticket', ticket_id), 'to': ('Keyword', kw_lower), 'type': 'MENTIONS'})

        elif event_type == 'slack_message':
            msg_id = event_data['msg_id']
            msg_props = {'id': msg_id, 'text': event_data['text'], 'channel': event_data['channel']}
            processed['nodes'].append({'label': 'Message', 'props': msg_props})
            
            # Create relationship: (User)-[:SENDS_MESSAGE]->(Message)
            processed['rels'].append({'from': ('User', user_email), 'to': ('Message', msg_id), 'type': 'SENDS_MESSAGE'})

            # Create relationships for each keyword: (Message)-[:MENTIONS]->(Keyword)
            for kw in keywords:
                # **THE FIX**: Standardize keyword to lowercase for consistency.
                kw_lower = kw.lower()
                kw_props = {'term': kw_lower}
                processed['nodes'].append({'label': 'Keyword', 'props': kw_props})
                processed['rels'].append({'from': ('Message', msg_id), 'to': ('Keyword', kw_lower), 'type': 'MENTIONS'})
        
        return processed