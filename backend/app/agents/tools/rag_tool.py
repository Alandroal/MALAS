# backend/app/agents/tools/rag_tool.py
from langchain.tools import BaseTool
from typing import Type, Any
# Corrected import for Pydantic v2 (assuming v2 is installed)
from pydantic import BaseModel, Field # Use standard Pydantic v2 import
from backend.app.rag.retriever import search_knowledge_base

class SearchInput(BaseModel):
    query: str = Field(description="The search query string to find relevant legal information in the knowledge base")

class KnowledgeBaseSearchTool(BaseTool):
    name: str = "Legal Knowledge Base Search"
    description: str = (
        "Searches a specialized knowledge base containing legal texts, regulations, "
        "and document templates. Use this tool to find specific legal information, "
        "clauses, precedents, or relevant sections of codes based on the case details."
    )
    args_schema: Type[BaseModel] = SearchInput # This should still work with Pydantic v2 BaseModel

    def _run(self, query: str, **kwargs: Any) -> Any:
        """Use the tool."""
        # Ensure search_knowledge_base is available and working
        try:
            results = search_knowledge_base(query=query)
            # Handle potential error messages from search_knowledge_base
            if isinstance(results, list) and results and "Error:" in results[0]:
                return f"Failed to search knowledge base: {results[0]}"
            return results
        except Exception as e:
            return f"Error executing search tool: {e}"


    async def _arun(self, query: str, **kwargs: Any) -> Any:
        """Use the tool asynchronously."""
        # For simplicity, using the sync version. Implement async search if needed.
        # Add error handling similar to _run
        try:
            results = search_knowledge_base(query=query)
            if isinstance(results, list) and results and "Error:" in results[0]:
                return f"Failed to search knowledge base: {results[0]}"
            return results
        except Exception as e:
            return f"Error executing search tool asynchronously: {e}"


# Instantiate the tool
knowledge_search_tool = KnowledgeBaseSearchTool()