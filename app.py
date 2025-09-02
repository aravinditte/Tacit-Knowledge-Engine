import streamlit as st
from dkg_manager import DKGManager
from workflow_weaver import WorkflowWeaver
import json

# --- Page Config and Services ---
st.set_page_config(page_title="Synapse 3.0", page_icon="⚡️", layout="wide")

@st.cache_resource
def get_services():
    dkg = DKGManager("bolt://localhost:7687", "neo4j", "12345678")
    weaver = WorkflowWeaver()
    return dkg, weaver

dkg, weaver = get_services()

# --- App UI ---
st.title("⚡️ Synapse 3.0: The Agentic Workflow Engine")
st.write("From tacit knowledge to automated action.")

# --- Workflow Intelligence Section ---
st.header("Workflow Intelligence")
st.markdown("Synapse analyzes event chains to discover hidden workflows.")

if st.button("Mine for Workflow Patterns"):
    # This query finds the most common two-step sequences of decisions.
    pattern_query = """
    MATCH (e1:Event)-[:NEXT]->(e2:Event)
    RETURN e1.decision_type AS step1, e2.decision_type AS step2, COUNT(*) AS frequency
    ORDER BY frequency DESC
    LIMIT 5
    """
    patterns = dkg.run_query(pattern_query)
    
    if patterns:
        st.subheader("Top Discovered Workflow Patterns")
        st.dataframe(patterns)

        st.subheader("Example Reusable Blueprint")
        st.markdown("This pattern can be converted into a reusable, automated blueprint:")
        
        # Take the top pattern and format it as a blueprint
        top_pattern = patterns[0]
        blueprint = {
            "name": f"Standard {top_pattern['step1']} to {top_pattern['step2']} Procedure",
            "trigger": {"type": "Event", "decision_type": top_pattern['step1']},
            "steps": [
                {"action": "Execute Step 1", "details": f"Perform task related to {top_pattern['step1']}"},
                {"action": "Execute Step 2", "details": f"Proceed with {top_pattern['step2']} protocol"}
            ],
            "confidence": f"{top_pattern['frequency']} occurrences observed"
        }
        st.json(blueprint)
    else:
        st.warning("No patterns found. Ingest more data to discover workflows.")

st.divider()

# --- Agentic Assistant Section ---
st.header("Agentic Assistant")
st.markdown("Simulate a new problem and see Synapse recommend the next step based on a learned blueprint.")

new_problem = st.text_input("Describe a new problem (e.g., 'The payment gateway is down again')", "")

if new_problem:
    # Use the weaver to analyze the new problem
    problem_embedding = weaver._get_embedding(new_problem)
    
    # Find the closest matching event in the graph to understand the context
    context_query = """
    CALL db.index.vector.fromEmbedding($embedding, 1) YIELD node AS event
    MATCH (event)-[:NEXT]->(next_event:Event)
    RETURN event.decision_type AS current_step, next_event.decision_type AS next_step_suggestion
    """
    # Note: Requires creating a vector index on Event nodes.
    # For this demo, we will simulate the match.
    
    if "database" in new_problem or "payment" in new_problem:
        st.success("Pattern Matched: Standard Triage to Escalation Procedure")
        st.subheader("Synapse Recommends Next Action:")
        
        st.info("**Action:** Escalate the issue to a senior team member.")
        st.markdown("**Reasoning:** The system has observed that after an initial 'Triage' of this problem type, the most common successful next step is 'Escalation'.")

        if st.button("✅ Execute Suggested Action (Simulated)"):
            st.toast("Action logged! The workflow continues.")
    else:
        st.warning("No matching workflow blueprint found for this problem.")