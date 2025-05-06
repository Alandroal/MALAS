# scripts/index_documents.py

import sys
import os
import traceback

# Calculate the absolute path to the project root directory (Malas/)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Insert the project root directory at the beginning of the Python path
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Core libraries
import chromadb
from langchain_community.vectorstores import Chroma # Corrected import for deprecation
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFDirectoryLoader # Use community loader

# Project-specific imports from backend
try:
    from backend.app.core.config import settings
    from backend.app.rag.retriever import get_embedding_function # Reuse the embedding function
except ImportError as e:
    print(f"Error importing from backend: {e}")
    print(f"Project root added to path: {project_root}")
    print(f"Current sys.path: {sys.path}")
    print("Please check that 'backend/app/core/config.py' and 'backend/app/rag/retriever.py' exist.")
    sys.exit(1)
# --- End Imports ---


# --- Indexing Logic ---
def perform_indexing():
    """Loads PDFs, splits them, creates embeddings, and stores them in ChromaDB."""
    print(f"Starting document indexing process...")
    print(f"Loading documents from: {settings.LEGAL_DOCS_PATH}")

    # Check if the document directory exists and is not empty
    if not os.path.exists(settings.LEGAL_DOCS_PATH):
        print(f"Error: Document directory '{settings.LEGAL_DOCS_PATH}' does not exist.")
        return False
    if not os.listdir(settings.LEGAL_DOCS_PATH):
         print(f"Warning: Document directory '{settings.LEGAL_DOCS_PATH}' is empty.")
         print("No documents to index.")
         # Create the DB directory anyway if it doesn't exist
         if not os.path.exists(settings.VECTOR_DB_PATH):
             os.makedirs(settings.VECTOR_DB_PATH)
             print(f"Created empty vector database directory: {settings.VECTOR_DB_PATH}")
         return False # Indicate nothing was indexed, but not necessarily an error

    # 1. Load Documents
    print("Loading PDF documents...")
    loader = PyPDFDirectoryLoader(settings.LEGAL_DOCS_PATH)
    try:
        documents = loader.load()
        if not documents:
             print("No documents were loaded successfully from the directory (check PDF files).")
             return False
        print(f"Loaded {len(documents)} document pages/sections.")
    except Exception as e:
        print(f"Error loading documents: {e}")
        traceback.print_exc()
        return False

    # 2. Split Documents
    print("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # Adjust size as needed
        chunk_overlap=200   # Adjust overlap as needed
    )
    try:
        texts = text_splitter.split_documents(documents)
        print(f"Split documents into {len(texts)} text chunks.")
        if not texts:
            print("No text chunks generated after splitting. Check document content and splitter settings.")
            return False
    except Exception as e:
        print(f"Error splitting documents: {e}")
        traceback.print_exc()
        return False

    # 3. Get Embedding Function
    print("Initializing embedding function...")
    try:
        embedding_function = get_embedding_function()
        if not embedding_function:
             raise ValueError("Failed to get embedding function.")
    except Exception as e:
        print(f"Error getting embedding function: {e}")
        traceback.print_exc()
        return False

    # 4. Create and Persist Vector Store
    print(f"Creating/updating vector store at: {settings.VECTOR_DB_PATH}")
    try:
        # Ensure the target directory exists
        os.makedirs(settings.VECTOR_DB_PATH, exist_ok=True)

        vector_store = Chroma.from_documents(
            documents=texts,
            embedding=embedding_function,
            persist_directory=settings.VECTOR_DB_PATH
            # collection_name="legal_documents" # Optional: specify collection name if needed later
        )

        # Explicitly persist (good practice)
        vector_store.persist()
        print(f"Successfully indexed {len(texts)} chunks to {settings.VECTOR_DB_PATH}")
        return True
    except Exception as e:
        print(f"Error creating/persisting vector store: {e}")
        traceback.print_exc()
        return False
# --- End Indexing Logic ---


# --- Main Execution Block ---
if __name__ == "__main__":
    print("="*50)
    print("Running Standalone RAG Document Indexing Script")
    print("="*50)
    success = perform_indexing() # Call the function defined above
    print("="*50)
    if success:
        print("Indexing completed successfully.")
        print("="*50)
    else:
        print("Indexing failed or no documents were processed. Check logs above.")
        print("="*50)
        sys.exit(1) # Exit with error code
# --- End Main Execution Block ---