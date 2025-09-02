from dkg_manager import DKGManager
from workflow_weaver import WorkflowWeaver

def run_ingestion():
    """Wipes the database and ingests simulated logs as workflow event chains."""
    dkg = DKGManager("bolt://localhost:7687", "neo4j", "12345678")
    weaver = WorkflowWeaver()

    # Clear old data for a fresh start
    print("Wiping database...")
    dkg.run_query("MATCH (n) DETACH DELETE n")
    
    # A log of events in chronological order for a single ticket
    simulated_log = [
        {
            'type': 'jira_comment', 'user_name': 'Jane Doe', 'ticket_id': 'PROJ-123',
            'text': "This looks like a 'database lock' issue. I've seen this before. Pinging @bob.smith to confirm."
        },
        {
            'type': 'slack_message', 'user_name': 'Bob Smith', 'ticket_id': 'PROJ-123',
            'text': "Confirmed. The 'database lock' is the root cause for PROJ-123. Escalating to SRE."
        },
        {
            'type': 'jira_comment', 'user_name': 'Jane Doe', 'ticket_id': 'PROJ-123',
            'text': "Thanks Bob. Applying the hotfix now. This issue is resolved."
        }
    ]

    print("Ingesting simulated event log...")
    for entry in simulated_log:
        chain_id, event_props = weaver.process_log_entry(entry)
        if chain_id and event_props:
            print(f"  -> Adding Event: {event_props['decision_type']} by {event_props['user']}")
            dkg.add_event_to_chain(chain_id, event_props)

    print("✅ Ingestion complete. Workflow chains have been built.")
    dkg.close()

if __name__ == "__main__":
    run_ingestion()