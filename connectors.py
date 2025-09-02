import time

def fetch_jira_data():
    """Simulates fetching new event data from Jira's API."""
    print("Connector: Fetching data from Jira...")
    return [
        {
            'source': 'Jira', 'user_name': 'Jane Doe', 'user_email': 'jane.doe@example.com', 'role': 'Senior Engineer',
            'ticket_id': 'PROJ-123', 'text': "This looks like a 'database lock' issue. Pinging @bob.smith to confirm."
        },
        {
            'source': 'Jira', 'user_name': 'Jane Doe', 'user_email': 'jane.doe@example.com', 'role': 'Senior Engineer',
            'ticket_id': 'PROJ-123', 'text': "Thanks Bob. Applying the hotfix now. This issue is resolved."
        }
    ]

def fetch_slack_data():
    """Simulates fetching new event data from Slack's API."""
    print("Connector: Fetching data from Slack...")
    return [
        {
            'source': 'Slack', 'user_name': 'Bob Smith', 'user_email': 'bob.smith@example.com', 'role': 'DBA',
            'ticket_id': 'PROJ-123', 'text': "Confirmed. The 'database lock' is the root cause. Escalating to SRE."
        }
    ]