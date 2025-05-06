import streamlit as st
import requests
import os
import traceback # Good to have for more detailed frontend errors if needed

# --- Configuration ---
# Assuming backend runs locally on port 8000 defined in .env
# In production, this should point to your deployed backend API URL
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000/api/v1/process-query")

# --- Streamlit App ---

st.set_page_config(page_title="Legal AI Advisor", layout="wide")

st.title("🏛️ Multi-Agent Legal Advisor System")
st.caption("Powered by CrewAI & Gemini Pro - Enter your legal query below")

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = [] # Store chat history {role: "user/assistant", content: "..."}
if "processing" not in st.session_state:
    st.session_state.processing = False # Flag to prevent multiple submissions

# --- Display Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"]) # Using markdown to render potential formatting

# --- Input Form ---
with st.sidebar:
    st.header("Case Details")
    doc_type = st.selectbox(
        "Select Desired Output Format:", # Slightly rephrased for clarity
        ("Legal Opinion", "Formal Letter", "Case Summary", "Analysis Points"), # Changed one option
        index=0 # Default to Legal Opinion
    )
    st.info(
        "This system uses AI agents to analyze your query based on a local knowledge base. "
        "Ensure your PDF documents are in `backend/data/legal_docs/` and indexed."
    ) # More informative text

# --- User Input Area ---
prompt = st.chat_input("Enter your legal query here...")

if prompt and not st.session_state.processing:
    st.session_state.processing = True # Lock input

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display thinking indicator
    with st.chat_message("assistant"):
        # Use a placeholder that can be updated if streaming were implemented
        message_placeholder = st.empty()
        message_placeholder.markdown("Processing your request with the legal team... ⏳")

        try:
            # --- Call Backend API ---
            payload = {
                "client_query": prompt,
                "document_type": doc_type # This is still sent to the backend
            }
            # Increased timeout for potentially long CrewAI processing
            # Set a very long timeout for debugging, but consider UX for production
            response = requests.post(BACKEND_API_URL, json=payload, timeout=1800)

            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

            # --- Process Response ---
            api_response = response.json()
            assistant_response = api_response.get("result", "Error: No result found in API response from backend.")
            # Update the placeholder with the actual response
            message_placeholder.markdown(assistant_response)

        except requests.exceptions.Timeout:
            st.error(f"The request to the backend timed out after {1800/60} minutes. The legal team is taking longer than expected. Please try a simpler query or check backend logs.")
            assistant_response = "Sorry, the analysis took too long and the request timed out."
            message_placeholder.markdown(assistant_response)
        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to backend API: {e}")
            assistant_response = f"Sorry, I encountered an error trying to reach the legal advisory service. Please ensure the backend is running correctly. Details: ({type(e).__name__})"
            message_placeholder.markdown(assistant_response)
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            traceback.print_exc() # Print full traceback to Streamlit console for dev
            assistant_response = f"An unexpected error occurred while processing your request. Details: ({type(e).__name__})"
            message_placeholder.markdown(assistant_response)

        # Add final assistant response to chat history (even if it's an error message)
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        st.session_state.processing = False # Unlock input
        # No st.rerun() needed here if updating placeholder, but if not using placeholder, rerun is needed.
        # For simplicity with placeholder update, st.rerun() is omitted to avoid clearing the new message briefly.

elif st.session_state.processing:
    # Keep input disabled while processing
    st.chat_input("Processing previous request...", disabled=True)


# Add a clear button in the sidebar
if st.sidebar.button("Clear Chat History"):
    st.session_state.messages = []
    st.session_state.processing = False
    st.rerun()