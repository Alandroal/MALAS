import os
import chromadb
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFDirectoryLoader # Use community loader
from backend.app.core.config import settings
from backend.app.rag.retriever import get_embedding_function # Reuse the embedding function

def index_documents():
    """Loads PDFs, splits them, creates embeddings, and stores them in ChromaDB."""
    print(f"Starting document indexing process...")
    print(f"Loading documents from: {settings.LEGAL_DOCS_PATH}")

    if not os.path.exists(settings.LEGAL_DOCS_PATH) or not os.listdir(settings.LEGAL_DOCS_PATH):
        print(f"Warning: Document directory '{settings.LEGAL_DOCS_PATH}' is empty or does not exist.")
        print("No documents to index.")
        # Create the DB directory anyway if it doesn't exist
        if not os.path.exists(settings.VECTOR_DB_PATH):
            os.makedirs(settings.VECTOR_DB_PATH)
            print(f"Created empty vector database directory: {settings.VECTOR_DB_PATH}")
        return False # Indicate nothing was indexed

    # 1. Load Documents
    loader = PyPDFDirectoryLoader(settings.LEGAL_DOCS_PATH)
    try:
        documents = loader.load()
        if not documents:
             print("No documents were loaded successfully from the directory.")
             return False
        print(f"Loaded {len(documents)} document pages/sections.")
    except Exception as e:
        print(f"Error loading documents: {e}")
        return False


    # 2. Split Documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # Adjust size as needed
        chunk_overlap=200   # Adjust overlap as needed
    )
    texts = text_splitter.split_documents(documents)
    print(f"Split documents into {len(texts)} text chunks.")

    if not texts:
        print("No text chunks generated after splitting.")
        return False

    # 3. Get Embedding Function
    embedding_function = get_embedding_function()

    # 4. Create and Persist Vector Store
    print(f"Creating/updating vector store at: {settings.VECTOR_DB_PATH}")
    # This will create the directory if it doesn't exist
    vector_store = Chroma.from_documents(
        documents=texts,
        embedding=embedding_function,
        persist_directory=settings.VECTOR_DB_PATH
        # collection_name="legal_documents" # Optional: specify collection name
    )

    # Explicitly persist (good practice, though often done automatically on creation/add)
    vector_store.persist()
    print(f"Successfully indexed {len(texts)} chunks to {settings.VECTOR_DB_PATH}")
    return True