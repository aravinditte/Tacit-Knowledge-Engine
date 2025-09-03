from dkg_manager import DKGManager
from workflow_weaver import WorkflowWeaver
from connectors import fetch_jira_data, fetch_slack_data

USER_REGISTRY = {
    'jane.doe@example.com': {"consent": True, "role": "Senior Engineer"},
    'bob.smith@example.com': {"consent": True, "role": "DBA"}
}

def run_ingestion():
    dkg = DKGManager("bolt://localhost:7687", "neo4j", "12345678")
    weaver = WorkflowWeaver()

    print("Wiping database for fresh ingestion...")
    dkg.run_query("MATCH (n) DETACH DELETE n")
    
    all_events = fetch_jira_data() + fetch_slack_data()
    all_events.sort(key=lambda x: x['text'])

    print("Ingesting events based on user consent...")
    for entry in all_events:
        user_email = entry.get('user_email')
        if USER_REGISTRY.get(user_email, {}).get("consent"):
            user_role = USER_REGISTRY[user_email].get("role", "Employee")
            chain_id, event_props = weaver.process_log_entry(entry, user_role)
            
            if chain_id and event_props:
                print(f"  -> Adding Event: {event_props['decision_type']} from {event_props['source']} by {user_role}")
                dkg.add_event_to_chain(chain_id, event_props)
        else:
            print(f"  -> SKIPPING Event: No consent from {entry.get('user_name')}")

    print("✅ Passive observation ingestion complete.")
    dkg.close()

if __name__ == "__main__":
    run_ingestion()