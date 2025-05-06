# backend/app/crew/legal_crew.py

from crewai import Crew, Process
# Import Agents
from backend.app.agents.legal_agents import (
    legal_advisor,
    labour_law_expert,
    civil_law_expert,
    fiscal_law_expert
    # legal_drafter import removed
)
# Import Task creators
from backend.app.tasks.legal_tasks import (
    create_client_consultation_task,
    create_labour_law_analysis_task,
    create_civil_law_analysis_task,
    create_fiscal_law_analysis_task,
    # create_document_drafting_task import removed
    create_final_consolidation_task # Added for the new final task
)
from backend.app.core.config import settings
import traceback # For error logging

def create_legal_crew(client_query: str, document_type: str):
    """
    Creates and configures the legal advisory crew.

    Args:
        client_query: The initial query from the user.
        document_type: The desired output document type (e.g., "Legal Opinion").

    Returns:
        A configured Crew instance.
    """
    print(f"--- Creating Legal Crew for Query: '{client_query[:70]}...' ---") # Log query
    # 1. Create Tasks
    print("Instantiating tasks...")
    consultation_task = create_client_consultation_task()
    labour_analysis_task = create_labour_law_analysis_task()
    civil_analysis_task = create_civil_law_analysis_task()
    fiscal_analysis_task = create_fiscal_law_analysis_task()
    consolidation_task = create_final_consolidation_task() # New final task
    print("Tasks instantiated.")

    # Define the sequence of tasks
    tasks_in_sequence = [
        consultation_task,
        labour_analysis_task,
        civil_analysis_task,
        fiscal_analysis_task,
        consolidation_task, # Legal Advisor consolidates at the end
    ]

    # Define the agents involved in this crew
    # Note: Even if an agent only performs one task, they need to be in the agents list.
    # The Lead Legal Advisor performs the first and last tasks.
    current_agents = [
        legal_advisor,
        labour_law_expert,
        civil_law_expert,
        fiscal_law_expert,
    ]

    # 2. Define Task Dependencies (Context Passing)
    # For Process.sequential, context is usually passed implicitly.
    # Explicit context can be set if specific outputs from non-adjacent tasks are needed.
    # For this linear flow, explicit context for each step is generally not required
    # as CrewAI handles passing the output of task N as context to task N+1.
    # The placeholders in task descriptions (e.g., {client_query}) will be filled
    # from the initial 'inputs' to crew.kickoff() or from the context of previous tasks.

    # Example of explicit context setting (if needed for specific versions/flows):
    # labour_analysis_task.context = [consultation_task]
    # civil_analysis_task.context = [consultation_task]
    # fiscal_analysis_task.context = [consultation_task]
    # consolidation_task.context = [
    #     consultation_task, # For initial query & summary
    #     labour_analysis_task,
    #     civil_analysis_task,
    #     fiscal_analysis_task
    # ]
    # print("Task contexts (if explicit) are notionally set.")


    # 3. Instantiate the Crew
    print("Instantiating crew...")
    legal_crew = Crew(
        agents=current_agents,
        tasks=tasks_in_sequence,
        process=Process.sequential,
        verbose=settings.CREWAI_VERBOSE,
        # memory=True, # Consider enabling memory for more conversational context between tasks
        # cache=True,  # Consider enabling caching for task results (speeds up reruns with same inputs)
    )
    print("Crew instantiated.")
    return legal_crew

def run_crew(client_query: str, document_type: str = "Legal Opinion") -> str:
    """
    Initializes and runs the legal crew.
    """
    crew = create_legal_crew(client_query, document_type)

    # Inputs for the kickoff method. These are primarily used by the first task(s)
    # or any task that explicitly uses these top-level input keys in its description.
    inputs = {
        "client_query": client_query,
        "document_type": document_type
    }

    print(f"--- Kicking off Crew for Query: '{client_query[:70]}...' ---")
    try:
        result = crew.kickoff(inputs=inputs)
        print(f"--- Crew execution finished for Query: '{client_query[:70]}...' ---")
        if not result:
             print("Warning: Crew execution resulted in an empty or None result.")
             # Provide a more user-friendly message for the frontend
             return "The legal advisory crew processed the request but did not produce a final consolidated output. Please check the logs or try refining the query."
        return result
    except Exception as e:
         print(f"!!! ERROR during crew kickoff/execution: {e} !!!")
         traceback.print_exc() # Log full traceback for debugging
         # Provide a more user-friendly message for the frontend
         return f"An error occurred during the legal analysis process. Details: {str(e)[:200]}" # Truncate long errors