# backend/app/rag/retriever.py

import chromadb

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings # For local models
from langchain_google_genai import GoogleGenerativeAIEmbeddings # Specific import for Google

from backend.app.core.config import settings
import google.generativeai as genai # Keep this for configuration
import os 
import traceback # For better error logging

# --- Embedding Function Setup ---
def get_embedding_function():
    """Gets the appropriate embedding function based on settings."""
    if settings.EMBEDDING_MODEL_TYPE == "google":
        print(f"Using Google Embedding Model: {settings.GOOGLE_EMBEDDING_MODEL_NAME}")
        # Configure googleai API key if needed (might be handled by langchain-google-genai automatically)
        # genai.configure(api_key=settings.GOOGLE_API_KEY) # Consider if needed or handled by the class
        try:
            # Use the correct class imported above
            embeddings = GoogleGenerativeAIEmbeddings(
                model=settings.GOOGLE_EMBEDDING_MODEL_NAME,
                google_api_key=settings.GOOGLE_API_KEY # Pass API key explicitly if required
            )
            return embeddings
        except Exception as e:
            print(f"Error initializing GoogleGenerativeAIEmbeddings: {e}")
            raise # Re-raise the exception to signal failure

    elif settings.EMBEDDING_MODEL_TYPE == "local":
        print(f"Using Local Sentence Transformer Model: {settings.EMBEDDING_MODEL_NAME}")
        try:
            # Use the correct class imported above
            embeddings = SentenceTransformerEmbeddings(
                model_name=settings.EMBEDDING_MODEL_NAME
                # Specify device if needed, e.g., model_kwargs={'device': 'cpu'}
            )
            return embeddings
        except Exception as e:
            print(f"Error initializing SentenceTransformerEmbeddings: {e}")
            raise # Re-raise the exception to signal failure
    else:
        # Should have been caught by config validation, but good to check
        raise ValueError(f"Unsupported EMBEDDING_MODEL_TYPE in config: {settings.EMBEDDING_MODEL_TYPE}")

# --- ChromaDB Client and Collection ---
# Ensure ChromaDB path exists
os.makedirs(settings.VECTOR_DB_PATH, exist_ok=True) # Now 'os' is defined
client = chromadb.PersistentClient(path=settings.VECTOR_DB_PATH)
# You might need to explicitly get or create the collection if Chroma() doesn't handle it
# collection_name = "legal_documents"
# collection = client.get_or_create_collection(name=collection_name)

# --- LangChain VectorStore Interface ---
# Initialize embedding function *once* for efficiency if possible,
# but handle potential errors during initialization
try:
    embedding_function_instance = get_embedding_function()
except Exception as e:
    print(f"CRITICAL: Failed to initialize embedding function. RAG will not work. Error: {e}")
    embedding_function_instance = None # Set to None to indicate failure


# Check if embedding function initialized successfully before creating vector_store
if embedding_function_instance:
    vector_store = Chroma(
        client=client,
        # collection_name=collection_name, # Use the same name if specified above
        embedding_function=embedding_function_instance,
        persist_directory=settings.VECTOR_DB_PATH # May be redundant with PersistentClient
    )
else:
    vector_store = None # Indicate that the vector store couldn't be initialized

def search_knowledge_base(query: str, k: int = 5) -> list[str]:
    """Searches the vector store for relevant documents."""
    if not vector_store:
        print("Error: Vector store not initialized (likely due to embedding function failure).")
        return ["Error: Knowledge base search is unavailable."]

    print(f"Searching knowledge base for: '{query}' (top {k} results)")
    try:
        retriever = vector_store.as_retriever(search_kwargs={"k": k})
        results = retriever.get_relevant_documents(query)
        print(f"Found {len(results)} relevant document chunks.")
        # Return content of the documents
        return [doc.page_content for doc in results] if results else ["No relevant information found in the knowledge base."]
    except Exception as e:
        print(f"Error during knowledge base search: {e}")
        traceback.print_exc() # Print full traceback for debugging
        return [f"Error during search: {e}"]