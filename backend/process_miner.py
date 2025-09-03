import pandas as pd
import pm4py
from pm4py.objects.conversion.log import converter as log_converter

def generate_process_map_data():
    """
    Reads the captured data, discovers a process model, and returns it
    as a simple JSON structure (nodes and edges).
    """
    try:
        df = pd.read_csv("captured_data.csv")
    except FileNotFoundError:
        return {"error": "captured_data.csv not found."}

    # --- 1. Format the data for pm4py ---
    # pm4py requires specific column names. We'll rename ours.
    # 'case:concept:name' = The ID of a single workflow case (e.g., a specific sender).
    # 'concept:name' = The name of the activity (e.g., 'Archive').
    # 'time:timestamp' = When the activity occurred.
    df_renamed = df.rename(columns={
        'sender': 'case:concept:name',
        'user_decision': 'concept:name',
        'capture_timestamp': 'time:timestamp'
    })

    # Convert timestamp column to datetime objects
    df_renamed['time:timestamp'] = pd.to_datetime(df_renamed['time:timestamp'])

    # Convert the DataFrame to an EventLog object, which pm4py understands.
    log = log_converter.apply(df_renamed)

    # --- 2. Discover the Process Model ---
    # We use the Inductive Miner algorithm to discover a Directly-Follows Graph.
    dfg, start_activities, end_activities = pm4py.discover_dfg(log)

    # --- 3. Convert the model to a simple JSON format for the frontend ---
    nodes = set()
    edges = []

    for (source, target), count in dfg.items():
        nodes.add(source)
        nodes.add(target)
        edges.append({"source": source, "target": target, "label": str(count)})

    # Format nodes for the frontend
    formatted_nodes = [{"id": node, "label": node} for node in nodes]

    return {"nodes": formatted_nodes, "edges": edges}