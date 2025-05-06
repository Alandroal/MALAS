# backend/app/tasks/legal_tasks.py

from crewai import Task
from backend.app.agents.legal_agents import (
    legal_advisor,
    labour_law_expert,
    civil_law_expert,
    fiscal_law_expert
)

# --- Define Task Templates ---

def create_client_consultation_task():
    """
    Task for the Legal Advisor to understand client needs and plan expert engagement.
    """
    return Task(
      description=(
          "1. Receive the client's initial query: {client_query}.\n"
          "2. If the query is unclear, formulate clarifying questions (the LLM will infer answers based on the initial query for simulation purposes).\n"
          "3. Clearly identify the core legal problem(s) presented by the client.\n"
          "4. Determine which legal domains (International Labour Law, Portuguese Civil Law, Portuguese Fiscal Law) are relevant for expert analysis. For each domain, decide if specific questions need to be posed or if the domain is not central to the core query.\n"
          "5. Formulate a concise summary of the client's situation. For each expert domain you deem relevant for analysis, outline the specific questions or areas they should address. "
          "If an expert domain (e.g., International Labour Law, Portuguese Fiscal Law) is deemed not directly relevant to the client's main query about '{client_query}', explicitly state: "
          "'No specific questions are directed to [Expert Role Name, e.g., International Labour Law Expert] for this query as their domain is not central to the core issue.'\n"
          "6. Note the required final output document type specified by the user: {document_type}."
      ),
      expected_output=(
          "A structured summary detailing:\n"
          "- The client's core legal issue(s).\n"
          "- A list of the legal domains identified for expert analysis.\n"
          "- For each domain requiring analysis: Specific questions or analytical points.\n"
          "- For domains deemed not directly relevant to the core query: An explicit statement indicating no specific questions are posed for that expert (e.g., 'No specific questions for International Labour Law Expert for this query.').\n"
          "- Confirmation of the final document type requested by the client (e.g., 'Legal Opinion').\n"
          "This summary will be passed as context to subsequent expert agents."
      ),
      agent=legal_advisor,
    )

def create_labour_law_analysis_task():
    """
    Task for the Labour Law Expert to analyze relevant aspects, if requested.
    """
    return Task(
      description=(
        "Carefully review the summary and specific instructions provided by the Lead Legal Advisor in the preceding task output. "
        "The Lead Legal Advisor's output will explicitly state if specific questions are directed to you for 'International Labour Law Expert'.\n"
        "IF the Lead Legal Advisor HAS POSED specific questions or requested analysis on international civil servant labour law aspects relevant to the client's case, then proceed with the analysis.\n"
        "   In such a case, focus on regulations and precedents applicable to international civil servants. "
        "   You MUST use the 'Legal Knowledge Base Search' tool to find and reference specific articles, rules, or relevant case law from the knowledge base provided. "
        "   Structure your analysis clearly and concisely.\n"
        "ELSE (if the Lead Legal Advisor's summary explicitly states 'No specific questions are directed to International Labour Law Expert' or similar, or provides no questions for your domain relevant to the core client query), "
        "your response should be a BRIEF statement confirming this, for example: "
        "'Based on the Lead Legal Advisor's initial assessment, specific analysis on International Labour Law is not required for the client's core query concerning divorce eligibility in Portugal.' "
        "Do not perform extensive research or LLM generation if no specific questions are posed for your domain by the Lead Advisor."
    ),
      expected_output=(
          "If specific questions were posed by the Lead Advisor: A detailed written analysis of the relevant international labour law aspects, directly addressing those points and citing sources from the knowledge base. "
          "If no specific questions were posed by the Lead Advisor for this domain: A brief statement confirming that your expertise was not deemed directly necessary for the core query, as per the Lead Advisor's initial assessment. Example: 'No specific International Labour Law analysis required for this query as per Lead Advisor's plan.'"
      ),
      agent=labour_law_expert,
    )

def create_civil_law_analysis_task():
    """
    Task for the Civil Law Expert to analyze relevant aspects.
    This agent is central to the 'divorce' query, so it will likely always receive questions.
    """
    return Task(
      description=(
        "Based on the summary and specific questions provided by the Lead Legal Advisor (from the previous task), "
        "analyze the Portuguese civil law aspects pertinent to the client's situation.\n"
        "Focus strictly on Portuguese Civil Code (Código Civil) provisions and relevant Portuguese jurisprudence.\n"
        "You MUST use the 'Legal Knowledge Base Search' tool to find and reference specific articles of the Civil Code or relevant court decisions from the knowledge base provided.\n"
        "Structure your analysis clearly and concisely."
      ),
      expected_output=(
          "A detailed written analysis of the relevant Portuguese civil law aspects, directly addressing the points raised by the Lead Legal Advisor. "
          "Cite specific articles or sources (e.g., Civil Code articles, case law summaries) found in the knowledge base. "
          "If no relevant civil law aspects are identified for this case (unlikely for a divorce query), or if the knowledge base yields no pertinent information for a specific question, clearly state this fact and the reasons."
      ),
      agent=civil_law_expert,
    )

def create_fiscal_law_analysis_task():
    """
    Task for the Fiscal Law Expert to analyze relevant aspects, if requested.
    """
    return Task(
      description=(
        "Carefully review the summary and specific instructions provided by the Lead Legal Advisor in the preceding task output. "
        "The Lead Legal Advisor's output will explicitly state if specific questions are directed to you for 'Portuguese Fiscal Law Expert'.\n"
        "IF the Lead Legal Advisor HAS POSED specific questions or requested analysis on Portuguese fiscal (tax) law implications relevant to the client's case, then proceed with the analysis.\n"
        "   In such a case, consider relevant Portuguese tax codes (IRS, IRC, IVA, etc.) and regulations. "
        "   You MUST use the 'Legal Knowledge Base Search' tool to find and reference specific tax laws or administrative guidance from the knowledge base provided. "
        "   Structure your analysis clearly and concisely.\n"
        "ELSE (if the Lead Legal Advisor's summary explicitly states 'No specific questions are directed to Portuguese Fiscal Law Expert' or similar, or provides no questions for your domain relevant to the core client query), "
        "your response should be a BRIEF statement confirming this, for example: "
        "'Based on the Lead Legal Advisor's initial assessment, specific analysis on Portuguese Fiscal Law is not required for the client's core query concerning divorce eligibility in Portugal.' "
        "Do not perform extensive research or LLM generation if no specific questions are posed for your domain by the Lead Advisor."
      ),
      expected_output=(
          "If specific questions were posed by the Lead Advisor: A detailed written analysis of the relevant Portuguese fiscal law aspects, directly addressing those points and citing sources from the knowledge base. "
          "If no specific questions were posed by the Lead Advisor for this domain: A brief statement confirming that your expertise was not deemed directly necessary for the core query, as per the Lead Advisor's initial assessment. Example: 'No specific Fiscal Law analysis required for this query as per Lead Advisor's plan.'"
      ),
      agent=fiscal_law_expert,
    )

def create_final_consolidation_task():
    """
    Task for the Lead Legal Advisor to consolidate expert analyses into a final response.
    """
    return Task(
        description=(
            "1. Review the initial client query: {client_query}.\n"
            "2. Review the initial summary and plan you (as Lead Legal Advisor) created in the first task.\n"
            "3. Synthesize and consolidate the outputs provided sequentially by the Labour Law Expert, Civil Law Expert, and Fiscal Law Expert in the preceding steps. "
            "   Note that some experts might have responded that their domain was not directly relevant and provided a brief statement to that effect; incorporate this understanding.\n"
            "4. Focus on integrating the key findings from the experts who *did* provide substantive analysis into a single, coherent response.\n"
            "5. Ensure the consolidated response directly addresses the client's initial query and incorporates the most pertinent information from the expert analyses.\n"
            "6. Structure the final output logically. If the requested document type was '{document_type}', try to adhere to a suitable structure for that type (e.g., for a 'Legal Opinion', include Introduction, Analysis based on expert input, Conclusion).\n"
            "7. Use clear, professional language suitable for a client.\n"
            "8. CRITICAL: Include a standard disclaimer at the end of the document, stating that this is AI-generated information and not a substitute for consultation with a qualified human lawyer, and that the information is based on the knowledge available up to your last update and the provided RAG documents."
        ),
        expected_output=(
            "A professionally structured and consolidated legal response (e.g., Legal Opinion, Analysis Summary, etc., based on the initial {document_type} request). "
            "This response must integrate the key findings from all contributing expert analyses (or note non-relevance if stated by an expert), directly address the client's original query {client_query}, be clearly written, and MUST include the specified disclaimer. "
            "If an expert indicated no relevant information for their domain as per your initial plan, this should be briefly noted if it provides useful context to the client (e.g., 'Fiscal implications were not analyzed as they were outside the scope of the initial query on eligibility.')."
        ),
        agent=legal_advisor,
    )