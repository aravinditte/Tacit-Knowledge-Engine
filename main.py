from dkg_manager import DKGManager
from workflow_weaver import AdvancedWeaver
import time

def setup_database_index(dkg):
    """Creates a vector index in Neo4j for each node label with an embedding."""
    print("Setting up database vector indexes...")
    
    # --- FIX START ---
    # We must create one index per label.
    
    # Index for Ticket nodes
    index_query_ticket = """
    CREATE VECTOR INDEX `ticket_semantic_index` IF NOT EXISTS
    FOR (n:Ticket) ON (n.embedding)
    OPTIONS {indexConfig: {
        `vector.dimensions`: 384,
        `vector.similarity_function`: 'cosine'
    }}
    """
    # Index for Message nodes
    index_query_message = """
    CREATE VECTOR INDEX `message_semantic_index` IF NOT EXISTS
    FOR (n:Message) ON (n.embedding)
    OPTIONS {indexConfig: {
        `vector.dimensions`: 384,
        `vector.similarity_function`: 'cosine'
    }}
    """
    
    try:
        with dkg._driver.session() as session:
            # Run both index creation queries
            session.run(index_query_ticket)
            session.run(index_query_message)
        print("✅ Vector indexes are ready.")
    except Exception as e:
        print(f"❌ Error creating indexes: {e}")
    # --- FIX END ---


def run_synapse_pipeline():
    dkg = DKGManager("bolt://localhost:7687", "neo4j", "12345678")
    weaver = AdvancedWeaver()

    # Create the necessary vector indexes before adding data
    setup_database_index(dkg)

    simulated_events = [
        # Same events as before
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

    print("\nSynapse pipeline started. Processing simulated events...")
    for event in simulated_events:
        print(f"  -> Processing event: {event['type']} from {event['user_name']}")
        processed_data = weaver.process_event(event)
        for node in processed_data['nodes']:
            dkg.add_node(node['label'], node['props'])
        for rel in processed_data['rels']:
            start_label, start_id = rel['from']
            end_label, end_id = rel['to']
            dkg.add_relationship(start_label, start_id, end_label, end_id, rel['type'])

    print("Pipeline finished. Knowledge has been captured in the DKG.")
    dkg.close()

if __name__ == "__main__":
    run_synapse_pipeline()