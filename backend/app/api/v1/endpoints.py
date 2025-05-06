from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from backend.app.crew.legal_crew import run_crew
import traceback # For detailed error logging

router = APIRouter()

class QueryRequest(BaseModel):
    client_query: str
    document_type: str = "Legal Opinion" # Default document type

class QueryResponse(BaseModel):
    result: str
    # Potentially add status, job_id, etc. for async handling later

@router.post("/process-query", response_model=QueryResponse)
async def process_legal_query(request: QueryRequest = Body(...)):
    """
    Receives a client query and initiates the CrewAI legal advisory process.
    """
    print(f"Received query: {request.client_query}, DocType: {request.document_type}")
    if not request.client_query:
        raise HTTPException(status_code=400, detail="Client query cannot be empty.")

    try:
        # In a production system, this should be asynchronous (e.g., using Celery)
        # For simplicity, running it synchronously here. BEWARE of long request times.
        final_result = run_crew(
            client_query=request.client_query,
            document_type=request.document_type
        )
        return QueryResponse(result=final_result)

    except Exception as e:
        print(f"Error processing query: {e}")
        traceback.print_exc() # Print full traceback to console/logs
        # Provide a more generic error to the client
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")