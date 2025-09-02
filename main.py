from dkg_manager import DKGManager
from weaver import Weaver
import time

def run_synapse_pipeline():
    """Initializes the system, processes data, and confirms the result."""
    
    # --- System Initialization ---
    try:
        # Remember to use the password you set in Neo4j Desktop
        dkg = DKGManager("bolt://localhost:7687", "neo4j", "12345678")
        weaver = Weaver()
    except Exception as e:
        print(f"Error initializing services: {e}")
        return

    # --- Layer 1: Simulated Observation Layer ---
    # Data now includes mixed cases to test our fix.
    simulated_events = [
        {
            'type': 'jira_comment',
            'user_name': 'Jane Doe',
            'user_email': 'jane.doe@example.com',
            'ticket_id': 'PROJ-123',
            'summary': 'Critical failure in payment gateway',
            'text': "This looks like a 'database lock' issue. I've seen this before in 'Project Phoenix'. Pinging @bob.smith to confirm."
        },
        {
            'type': 'slack_message',
            'user_name': 'Bob Smith',
            'user_email': 'bob.smith@example.com',
            'channel': '#dev-alerts',
            'msg_id': f'slack-{int(time.time())}',
            'text': "Confirmed. The 'Database Lock' is the root cause for PROJ-123. Refer to the post-mortem doc: [link]"
        },
        {
            'type': 'jira_comment',
            'user_name': 'Jane Doe',
            'user_email': 'jane.doe@example.com',
            'ticket_id': 'PROJ-123',
            'summary': 'Critical failure in payment gateway',
            'text': "Thanks Bob. Applying the hotfix now. This issue is resolved."
        }
    ]

    print("Synapse pipeline started. Processing simulated events...")
    # --- Processing Loop ---
    for event in simulated_events:
        print(f"  -> Processing event: {event['type']} from {event['user_name']}")
        
        # Layer 2: Weaver processes the raw data
        processed_data = weaver.process_event(event)

        # Layer 3: DKG Manager writes the processed data to the graph
        for node in processed_data['nodes']:
            dkg.add_node(node['label'], node['props'])
        
        for rel in processed_data['rels']:
            start_label, start_id = rel['from']
            end_label, end_id = rel['to']
            dkg.add_relationship(start_label, start_id, end_label, end_id, rel['type'])

    print("Pipeline finished. Knowledge has been captured in the DKG.")
    
    # --- Confirmation Step ---
    print("\nRunning a confirmation query to find the 'database lock' expert...")
    
    # This is the robust query from our previous discussion.
    expert_query = """
        MATCH (k:Keyword)<-[:MENTIONS]-(t)<-[:COMMENTS_ON]-(u:User)
        WHERE k.term = 'database lock'
        RETURN u.name AS Expert, COUNT(t) AS Mentions
        ORDER BY Mentions DESC
    """
    
    # Note: Neo4j Python driver doesn't have a built-in 'run_query' method.
    # We must create it in DKGManager or handle the session here.
    # For simplicity, let's create a temporary session to run our read query.
    try:
        with dkg._driver.session() as session:
            results = session.run(expert_query)
            expert_data = results.data()
            if expert_data:
                for record in expert_data:
                    print(f"  ✅ SUCCESS: Found expert '{record['Expert']}' with {record['Mentions']} mentions.")
            else:
                print("  ❌ CONFIRMATION FAILED: Could not find the expert via query.")
    except Exception as e:
        print(f"  ❌ An error occurred during the confirmation query: {e}")
    finally:
        dkg.close() # Clean up the connection.

if __name__ == "__main__":
    run_synapse_pipeline()