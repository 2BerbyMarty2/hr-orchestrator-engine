"""
HR Orchestration Shared State and Classification Engine.

This module houses the global state dictionary structures (TypedDict) and execution nodes
that manage context, classified intents, and response payloads across the routing pipeline.
"""

from typing import TypedDict, Optional, List

class HRState(TypedDict):
    """
    The central shared memory state dictionary (clipboard) for the LangGraph workflow.
    
    Attributes:
        employee_id (str): The unique database identifier of the querying employee.
        user_message (str): The original plain-text request submitted by the employee.
        intent (Optional[str]): The classified category (LEAVE, SCHEDULE, POLICY, UNKNOWN).
        confidence (Optional[float]): Numerical confidence score of intent classification (0.0 to 1.0).
        final_response (Optional[str]): Final text drafted by the active target specialist agent.
        extracted_dates (Optional[List[str]]): List of target ISO dates extracted from the query.
    """
    employee_id: str
    user_message: str
    intent: Optional[str]
    confidence: Optional[float]
    final_response: Optional[str]
    extracted_dates: Optional[List[str]]


def initialize_state(employee_id: str, user_message: str) -> HRState:
    """
    Initializes the shared HRState with user credentials and inputs.

    Args:
        employee_id (str): Unique employee identifier.
        user_message (str): Plain-text query.

    Returns:
        HRState: Fresh state dictionary ready for LangGraph execution.
    """
    return HRState(
        employee_id=employee_id,
        user_message=user_message,
        intent=None,
        confidence=None,
        final_response=None,
        extracted_dates=None
    )


def orchestrator_node(state: HRState) -> HRState:
    """
    Orchestration node that parses request context and classifies query intent.
    This acts as the classification layer determining which specialized downstream agent
    the inquiry should be routed to.

    Args:
        state (HRState): Current state containing raw employee inquiry text.

    Returns:
        HRState: Mutated state updated with classified intent and confidence score.
    """
    user_message = state.get("user_message", "")

    # Structured guidance detailing intent thresholds and routing categories
    prompt = f"""
        You are the Orchestrator for an enterprise HR system. Your sole responsibility is to analyze the user's message and classify its primary intent so it can be routed to the correct sub-agent.

        Your routing must fall strictly into one of the following categories:

        1. LEAVE
           - Triggers: Requests for time off, PTO, checking vacation balances, reporting sick days, or maternity/paternity leave.
        2. SCHEDULE
           - Triggers: Booking meetings, checking calendars, shifting work hours, or setting up 1:1 reviews.
        3. COMPLIANCE
           - Triggers: Questions about the employee handbook, dress codes, HR policies, benefits, or legal workplace regulations.
        4. UNKNOWN
           - Triggers: Vague statements, friendly greetings with no request, or non-HR topics (e.g., "Fix my computer").

        SCORING RULES:
        - If the intent is obvious and contains specific details, assign a high confidence score (0.85 to 1.0).
        - If the request touches on two categories (e.g., "Schedule a meeting about my leave"), choose the primary action requested and assign a medium confidence score (0.6 to 0.8).
        - If the request is incomplete or unrelated to HR, select UNKNOWN and assign a low confidence score (0.0 to 0.4).

        User Message: "{user_message}"
        """
    
    # Mock LLM classifier output simulating classification inference
    response = {
        "intent": "LEAVE",  
        "confidence": 0.95  
    }

    # Commit classification metadata into the shared graph clipboard
    state["intent"] = response["intent"]
    state["confidence"] = response["confidence"]
    return state
