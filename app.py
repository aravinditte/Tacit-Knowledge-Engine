# app.py
import streamlit as st
from dkg_manager import DKGManager
from workflow_weaver import AdvancedWeaver
from file_processor import extract_pages_from_pdf, extract_text_from_file
import time

# --- Page Configuration & Services ---
st.set_page_config(page_title="Synapse", page_icon="🧠", layout="wide")

@st.cache_resource
def get_services():
    print("Initializing services for frontend...")
    dkg = DKGManager("bolt://localhost:7687", "neo4j", "12345678")
    weaver = AdvancedWeaver()
    
    # Create a dedicated vector index for Document Pages
    index_query = """
    CREATE VECTOR INDEX `document_page_index` IF NOT EXISTS
    FOR (p:DocumentPage) ON (p.embedding)
    OPTIONS {indexConfig: {
        `vector.dimensions`: 384,
        `vector.similarity_function`: 'cosine'
    }}
    """
    try:
        with dkg._driver.session() as session:
            session.run(index_query)
        print("✅ Document page vector index is ready.")
    except Exception as e:
        print(f"Error creating document index: {e}")
        
    return dkg, weaver

dkg, weaver = get_services()

# --- App UI ---
st.title("🧠 Synapse: The Tacit Knowledge Engine")
st.write("Ask questions or upload a document to uncover hidden knowledge and experts.")

# --- Document Upload & Analysis Section ---
st.sidebar.header("Analyze a Document")
uploaded_file = st.sidebar.file_uploader(
    "Upload a PDF, DOCX, or TXT file", 
    type=['pdf', 'docx', 'txt']
)

if uploaded_file is not None:
    st.header(f"Analysis of: `{uploaded_file.name}`")
    
    if uploaded_file.name.endswith('.pdf'):
        with st.spinner(f"Processing PDF '{uploaded_file.name}' page by page..."):
            pages_processed = 0
            doc_id = f"doc-{int(time.time())}"
            dkg.add_node('Document', {'id': doc_id, 'title': uploaded_file.name})

            for page_num, page_text in extract_pages_from_pdf(uploaded_file):
                page_id = f"{doc_id}-p{page_num}"
                embedding = weaver._get_embedding(page_text)
                
                page_props = {
                    'id': page_id,
                    'title': uploaded_file.name,
                    'page_number': page_num,
                    'text': page_text,
                    'embedding': embedding
                }
                dkg.add_node('DocumentPage', page_props)
                dkg.add_relationship('Document', doc_id, 'DocumentPage', page_id, 'HAS_PAGE')
                pages_processed += 1
            st.success(f"Processed and indexed {pages_processed} pages from '{uploaded_file.name}'.")
    else:
        st.info("Currently, only PDFs are processed with page-level tracking.")

st.divider()

# --- Dedicated Document Search Section ---
st.header("Search Uploaded Documents")
doc_search_query = st.text_input("Ask a question about the documents you've uploaded:", "")

if doc_search_query:
    query_embedding = weaver._get_embedding(doc_search_query)
    search_cypher = """
    CALL db.index.vector.queryNodes('document_page_index', 5, $embedding) YIELD node, score
    RETURN node.text AS text, node.page_number AS page, node.title as title, score
    """
    
    with dkg._driver.session() as session:
        results = session.run(search_cypher, embedding=query_embedding).data()

    if results:
        st.subheader("Most Relevant Information from your Documents:")
        for record in results:
            st.info(f"**Source: '{record['title']}' - Page {record['page']} (Similarity: {record['score']:.2f})**")
            st.markdown(f"> ...{record['text'][:500]}...")
            st.divider()
    else:
        st.warning("Could not find any relevant information in the uploaded documents.")

st.divider()

# --- Existing Semantic Search Section (for simulated data) ---
st.header("Search Simulated Jira/Slack Knowledge")
sim_search_query = st.text_input("e.g., 'What do we know about payment gateway problems?'", "")

# --- THIS SECTION IS NOW FULLY RESTORED ---
if sim_search_query:
    query_embedding = weaver._get_embedding(sim_search_query)
    
    ticket_query = "CALL db.index.vector.queryNodes('ticket_semantic_index', 5, $embedding) YIELD node, score RETURN node.text AS text, score"
    message_query = "CALL db.index.vector.queryNodes('message_semantic_index', 5, $embedding) YIELD node, score RETURN node.text AS text, score"
    
    all_results = []
    with dkg._driver.session() as session:
        ticket_results = session.run(ticket_query, embedding=query_embedding).data()
        all_results.extend(ticket_results)
        
        message_results = session.run(message_query, embedding=query_embedding).data()
        all_results.extend(message_results)

    # Sort all combined results by score (highest similarity first)
    sorted_results = sorted(all_results, key=lambda x: x['score'], reverse=True)
    
    if sorted_results:
        st.subheader("Most Relevant Knowledge:")
        # Display the top 5 overall results
        for record in sorted_results[:5]:
            st.markdown(f"> {record['text']}")
            st.caption(f"Similarity Score: {record['score']:.2f}")
            st.divider()
    else:
        st.warning("No relevant knowledge found for that query.")