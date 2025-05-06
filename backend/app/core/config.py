import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

class Settings:
    # LLM
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    GEMINI_MODEL_NAME: str = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-pro-preview-03-25")

    # RAG
    LEGAL_DOCS_PATH: str = os.getenv("LEGAL_DOCS_PATH", "./backend/data/legal_docs")
    VECTOR_DB_PATH: str = os.getenv("VECTOR_DB_PATH", "./backend/data/vector_db")
    EMBEDDING_MODEL_TYPE: str = os.getenv("EMBEDDING_MODEL_TYPE", "local") # 'local' or 'google'
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2") # Or Google model name
    GOOGLE_EMBEDDING_MODEL_NAME: str = os.getenv("GOOGLE_EMBEDDING_MODEL_NAME", "models/text-embedding-004")


    # API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", 8000))

    # CrewAI
    CREWAI_VERBOSE: int = int(os.getenv("CREWAI_VERBOSE", 2))

settings = Settings()

# Basic validation
if not settings.GOOGLE_API_KEY or settings.GOOGLE_API_KEY == "YOUR_GOOGLE_API_KEY_HERE":
    raise ValueError("GOOGLE_API_KEY is not set in the .env file.")
if settings.EMBEDDING_MODEL_TYPE not in ["local", "google"]:
     raise ValueError("EMBEDDING_MODEL_TYPE must be 'local' or 'google' in .env")