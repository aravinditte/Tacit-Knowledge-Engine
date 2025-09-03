import streamlit as st
from dkg_manager import DKGManager
from workflow_weaver import WorkflowWeaver
from synapse_bots import DecisionClarificationBot

st.set_page_config(page_title="Synapse Dashboard", page_icon="🚀", layout="wide")

@st.cache_resource
def get_services():
    dkg = DKGManager("bolt://localhost:7687", "neo4j", "12345678")
    weaver = WorkflowWeaver()
    bot = DecisionClarificationBot()
    return dkg, weaver, bot

dkg, weaver, bot = get_services()

st.title("🚀 Synapse: The Tacit Knowledge Engine")
st.markdown("Welcome to the central dashboard. Navigate to different modules using the sidebar.")

st.header("🔔 Interactive Learning Center")
st.markdown("Synapse occasionally asks for clarification to enrich its knowledge. Your input makes the system smarter.")

recent_events_query = "MATCH (e:Event) RETURN e ORDER BY e.timestamp DESC LIMIT 5"
recent_events = dkg.run_query(recent_events_query)

if recent_events:
    for event_data in recent_events:
        event = event_data['e']
        prompt_data = bot.analyze_event_and_prompt(event)
        
        if prompt_data:
            st.info(f"**Action by {event['user_role']} ('{event['user']}')**: {event['text']}")
            
            with st.form(key=f"form_{event['id']}"):
                clarification = st.selectbox(prompt_data['prompt'], options=prompt_data['options'])
                submitted = st.form_submit_button("Submit Clarification")
                
                if submitted and clarification:
                    dkg.update_event_with_clarification(event['id'], clarification)
                    st.success("Thank you! Your knowledge has been captured.")
                    st.rerun()
else:
    st.write("No events requiring clarification at this time.")