# Malas: Multi-Agent Legal Advisory System using CrewAI

This project implements a browser-based multi-agent legal advisory service (Malas) powered by CrewAI and Google's Gemini Pro model. It features specialized legal "expert" agents for different domains (International Labour Law, Portuguese Civil Law, Portuguese Fiscal Law) and utilizes a local Retrieval-Augmented Generation (RAG) system based on PDF documents.

## Architecture Overview

*   **Frontend:** Streamlit (Browser-based Chat Interface)
*   **Backend:** FastAPI (API Gateway)
*   **Orchestration:** CrewAI (Agent coordination, task management)
*   **LLM:** Google Gemini Pro (via `langchain-google-genai`)
*   **RAG:**
    *   Local PDF documents (`backend/data/legal_docs/`)
    *   Text Splitting (`langchain`)
    *   Embeddings (Google GenAI Embeddings or local Sentence Transformers)
    *   Vector Store: ChromaDB (Local, persistent)
*   **Agents:**
    *   `Legal Advisor`: Client interaction, coordination.
    *   `Labour Law Expert`: International Civil Servant Labour Law analysis (uses RAG).
    *   `Civil Law Expert`: Portuguese Civil Law analysis (uses RAG).
    *   `Fiscal Law Expert`: Portuguese Fiscal Law analysis (uses RAG).
    *   `Legal Drafter`: Compiles analyses into final document.


# --- Project Structure ---

MALAS/
├── .env                 # Environment variables (API keys, paths, model names)
├── .gitignore           # Git ignore file
├── README.md            # Project description, setup, usage
├── requirements.txt     # Python dependencies
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI application entry point
│   │   ├── api/             # API endpoint definitions
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       └── endpoints.py   # Chat interaction endpoint
│   │   ├── core/            # Core logic & configuration
│   │   │   ├── __init__.py
│   │   │   └── config.py      # Load settings from .env
│   │   ├── agents/          # CrewAI agent definitions
│   │   │   ├── __init__.py
│   │   │   ├── legal_agents.py # Agent classes/definitions
│   │   │   └── tools/         # Custom tools (RAG search)
│   │   │       ├── __init__.py
│   │   │       └── rag_tool.py
│   │   ├── tasks/           # CrewAI task definitions
│   │   │   ├── __init__.py
│   │   │   └── legal_tasks.py  # Task classes/definitions
│   │   ├── crew/            # Crew assembly and execution
│   │   │   ├── __init__.py
│   │   │   └── legal_crew.py   # Crew setup and kickoff logic
│   │   └── rag/             # RAG system implementation
│   │       ├── __init__.py
│   │       ├── indexer.py     # Logic to build/update index
│   │       └── retriever.py   # Logic to query the index
│   └── data/                # Local data storage
│       ├── legal_docs/      # <<--- PLACE YOUR PDF LEGAL DOCS HERE
│       │   └── placeholder.txt # Keep directory in Git
│       └── vector_db/       # Directory for ChromaDB persistence
│           └── placeholder.txt # Keep directory in Git
├── frontend/
│   └── app.py             # Streamlit application script
└── scripts/               # Utility scripts
    └── index_documents.py # Script to run the RAG indexing process



## Setup

1.  **Clone the Repository:**
    ```bash
    git clone <your-repo-url> # URL pointing to your Malas repository
    cd Malas
    ```

2.  **Create a Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *Note: This project requires Python 3.12.*

4.  **Configure Environment Variables:**
    *   Copy the `.env.example` file (if provided) or create a `.env` file in the project root (`Malas/`).
    *   Add your Google API Key and configure other settings:
        ```env
        GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY_HERE"
        GEMINI_MODEL_NAME="gemini-1.5-pro-latest" # Or another compatible model

        LEGAL_DOCS_PATH="./backend/data/legal_docs"
        VECTOR_DB_PATH="./backend/data/vector_db"
        EMBEDDING_MODEL_TYPE="local" # or "google"
        EMBEDDING_MODEL_NAME="all-MiniLM-L6-v2" # if EMBEDDING_MODEL_TYPE="local"
        # GOOGLE_EMBEDDING_MODEL_NAME="models/text-embedding-004" # if EMBEDDING_MODEL_TYPE="google"

        API_HOST="0.0.0.0"
        API_PORT="8000"
        CREWAI_VERBOSE="2"
        ```
    *   **Important:** Obtain your Google API Key from [Google AI Studio](https://aistudio.google.com/app/apikey) or Google Cloud Console and ensure the Generative Language API is enabled.

5.  **Add Legal Documents:**
    *   Place your relevant legal PDF documents (texts, codes, templates) into the `backend/data/legal_docs/` directory.

6.  **Index Documents for RAG:**
    *   Run the indexing script from the project root (`Malas/`). This needs to be done once initially and whenever you add/update documents.
    ```bash
    python scripts/index_documents.py
    ```
    *   This will process the PDFs, create embeddings, and store them in the ChromaDB vector store located at `backend/data/vector_db/`.

## Running the System

1.  **Start the Backend API (FastAPI):**
    *   Ensure you are in the project root directory (`Malas/`) and the virtual environment is active.
    ```bash
    uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
    ```
    *   `--reload` is useful for development; remove it for production.
    *   The API will be available at `http://localhost:8000`. You can access the Swagger UI documentation at `http://localhost:8000/docs`.

2.  **Start the Frontend (Streamlit):**
    *   Open a *new* terminal window.
    *   Navigate to the project root directory (`cd Malas`).
    *   Activate the virtual environment (`source venv/bin/activate`).
    *   Run:
    ```bash
    streamlit run frontend/app.py
    ```
    *   The Streamlit app will open in your browser, usually at `http://localhost:8501`.

3.  **Interact:**
    *   Use the chat interface in the Streamlit app to ask your legal query.
    *   Select the desired output document type in the sidebar.
    *   The system will engage the CrewAI agents, use the RAG system, and provide the final drafted document.


# Quick Start Steps
Install: pip install -r requirements.txt
Configure: Create and fill in your .env file.
Add Docs: Put PDFs in backend/data/legal_docs/.
Index: Run python scripts/index_documents.py.
Run Backend: uvicorn backend.app.main:app --reload --port 8000
Run Frontend: streamlit run frontend/app.py
Access: Open http://localhost:8501 in your browser.



## Disclaimer

This system provides AI-generated legal information based on the provided documents and LLM capabilities. It is **NOT** a substitute for professional legal advice from a qualified human lawyer. Use with caution and always consult a legal professional for critical matters.

