from fastapi import FastAPI
from backend.app.api.v1 import endpoints as v1_endpoints
from backend.app.core.config import settings
import uvicorn

app = FastAPI(
    title="Multi-Agent Legal Advisory System API",
    description="API for interacting with the CrewAI-based legal advisory system.",
    version="1.0.0"
)

# Include API routers
app.include_router(v1_endpoints.router, prefix="/api/v1", tags=["Legal Advisory"])

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Legal Advisory System API. See /docs for details."}

# Allow CORS for Streamlit frontend (adjust origins in production)
from fastapi.middleware.cors import CORSMiddleware
origins = [
    "http://localhost",
    "http://localhost:8501", # Default Streamlit port
    # Add deployed frontend URL here if applicable
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# This block allows running directly with `python backend/app/main.py`
if __name__ == "__main__":
    print(f"Starting API server on {settings.API_HOST}:{settings.API_PORT}")
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)