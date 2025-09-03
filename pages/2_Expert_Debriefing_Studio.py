import streamlit as st
from dkg_manager import DKGManager
from workflow_weaver import WorkflowWeaver
import uuid

# --- State Initialization ---
# Initialize session_state keys at the very top to avoid errors.
if 'workflow_steps' not in st.session_state:
    st.session_state.workflow_steps = []
if 'workflow_name' not in st.session_state:
    st.session_state.workflow_name = ""

@st.cache_resource
def get_services():
    dkg = DKGManager("bolt://localhost:7687", "neo4j", "12345678")
    weaver = WorkflowWeaver()
    return dkg, weaver

dkg, weaver = get_services()

st.title("🧑‍🏫 Expert Debriefing Studio")
st.markdown("Convert your expert knowledge into a reusable, automated blueprint by describing your workflow step-by-step.")

# --- Form for Workflow Creation ---
with st.form(key="workflow_form"):
    st.text_input("What is the name of this workflow? (e.g., 'New Client Onboarding')", key="workflow_name_input")
    st.text_area("Describe the next step in the workflow:", key="step_description", placeholder="Example: First, the project manager receives the signed contract and creates a new project in Jira.")
    
    # --- Form Buttons ---
    add_step_submitted = st.form_submit_button("Add Step to Workflow")
    save_workflow_submitted = st.form_submit_button("✅ Save Workflow as Blueprint")

# --- Logic for "Add Step" ---
if add_step_submitted:
    if st.session_state.step_description:
        # Update workflow name from the input box inside the form
        st.session_state.workflow_name = st.session_state.workflow_name_input
        
        _, event_props = weaver.process_log_entry({
            'source': 'debriefing_session',
            'user_name': 'Expert',
            'text': st.session_state.step_description
        }, "Expert")
        st.session_state.workflow_steps.append(event_props)
    else:
        st.warning("Please describe a step.")
    
# --- Logic for "Save Workflow" ---
if save_workflow_submitted:
    st.session_state.workflow_name = st.session_state.workflow_name_input
    if st.session_state.workflow_name and st.session_state.workflow_steps:
        chain_id = str(uuid.uuid4())
        for step in st.session_state.workflow_steps:
            dkg.add_event_to_chain(chain_id, step)
        st.success(f"Blueprint '{st.session_state.workflow_name}' has been saved to the Knowledge Graph!")
        
        # Clear the state for the next debriefing
        st.session_state.workflow_steps = []
        st.session_state.workflow_name = ""
        st.rerun() # Rerun the script to reflect the cleared state
    else:
        st.error("Please provide a workflow name and at least one step before saving.")


# --- Display the workflow currently being built ---
if st.session_state.workflow_steps:
    st.subheader(f"Blueprint for: '{st.session_state.workflow_name}'")
    for i, step in enumerate(st.session_state.workflow_steps):
        st.markdown(f"**Step {i+1}:** {step['decision_type']} ({step['user_role']})")
        st.caption(step['text'])