"""
HR Specialist Agent Execution Nodes.

This module houses the specialist execution nodes that handle inquiries routed
from the central orchestrator. Each agent connects to specific databases,
applies unique prompt instructions, and calls Google Gemini API to draft professional,
domain-expert responses.
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from app.state import HRState
from app.database.database import DatabaseClient, EmployeeNotFoundError

# Load environment configuration variables
load_dotenv()

# Initialize global LLM client with fallback configurations
llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    temperature=0.3,
    api_key=os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"),
)

# Connect global database coordinator client
db = DatabaseClient()


def leave_agent_node(state: HRState) -> dict:
    """
    Leave specialist node that manages vacation balances, PTO, and sick days.
    Queries the database directory to retrieve actual live employee leave metrics.

    Args:
        state (HRState): Current state containing employee ID and raw request.

    Returns:
        dict: State update dictionary containing the drafted 'final_response'.
    """
    employee_id = state.get("employee_id", "Unknown")
    user_message = state.get("user_message", "")
    memory_context = state.get("memory_context", "No prior context.")

    try:
        # Fetch remaining leave balances directly from database records
        vac_left, vac_alloc, sick_left, sick_alloc = db.fetch_leave_data(employee_id)
        db_context = (
            f"Vacation Remaining: {vac_left} (out of {vac_alloc}). "
            f"Sick Days Remaining: {sick_left} (out of {sick_alloc})."
        )
    except EmployeeNotFoundError:
        db_context = f"agents.py AG-001 error: No leave records found in the database for employee ID: {employee_id}."

    # Specialist prompt incorporating live database state and instructions
    prompt = f"""You are the HR Leave & Time-Off Specialist Agent.
Your responsibility is to process employee requests regarding vacation, PTO, sick days, and other forms of leave.

CURRENT DATABASE RECORDS FOR {employee_id}:
{db_context}

CURRENT MEMORY CONTEXT:
{memory_context}

USER MESSAGE:
"{user_message}"

INSTRUCTIONS:
1. Analyze the user's request against the memory context to see if dates or leave balances have already been established.
2. If the user is requesting specific dates, extract them and confirm. If dates are missing, politely ask for them.
3. If the user is reporting sick leave, respond with empathy and inform them that their manager will be notified.
4. Do not invent or hallucinate vacation balances. Use only the database records provided above.

OUTPUT:
Provide a direct, helpful, and professional HR response to the employee."""

    # Invoke Gemini LLM directly to obtain the response body
    response = llm.invoke(prompt)
    return {"final_response": response.content}


def schedule_agent_node(state: HRState) -> dict:
    """
    Calendar coordinator node that manages work schedules and 1:1 meeting sessions.
    Queries the database directory to retrieve upcoming shifts.

    Args:
        state (HRState): Current state containing employee ID and raw request.

    Returns:
        dict: State update dictionary containing the drafted 'final_response'.
    """
    employee_id = state.get("employee_id", "Unknown")
    user_message = state.get("user_message", "")
    memory_context = state.get("memory_context", "No prior context.")

    # Retrieve upcoming shifts ordered by date ascending and format as a Markdown table
    schedule_rows = db.fetch_schedule_data(employee_id)
    if schedule_rows:
        db_context = "| Date | Start Time | End Time |\n| :--- | :--- | :--- |\n" + "\n".join(
            [f"| {row[0]} | {row[1]} | {row[2]} |" for row in schedule_rows]
        )
    else:
        db_context = "No upcoming shifts scheduled."

    # Specialist prompt incorporating schedule rows
    prompt = f"""You are the HR Scheduling Coordinator Agent.
Your responsibility is to assist employees with booking meetings, shifting work schedules, and checking calendar availability.

CURRENT UPCOMING SCHEDULE FOR {employee_id}:
{db_context}

CURRENT MEMORY CONTEXT:
{memory_context}

USER MESSAGE:
"{user_message}"

INSTRUCTIONS:
1. Identify the core scheduling action: Is the user booking a new meeting, canceling an existing one, or changing their working hours?
2. Extract any mentioned participants, times, and dates.
3. Check the memory context for previously mentioned preferences (e.g., "I only work mornings") and apply them.
4. If essential details (like time or participant names) are missing, ask the user to clarify those specific details.
5. When presenting or listing scheduled shifts to the employee, always format them as a clean Markdown data table with columns for Date, Start Time, and End Time.

OUTPUT:
Provide a clear, concise response confirming the scheduling action or requesting the missing parameters."""

    # Invoke LLM
    response = llm.invoke(prompt)
    return {"final_response": response.content}


def policy_agent_node(state: HRState) -> dict:
    """
    Compliance and policy specialist node that answers handbook, dress code, and benefit queries.
    Relies on standard compliance guidelines.

    Args:
        state (HRState): Current state containing employee ID and raw request.

    Returns:
        dict: State update dictionary containing the drafted 'final_response'.
    """
    user_message = state.get("user_message", "")
    memory_context = state.get("memory_context", "No prior context.")

    # Specialist prompt
    prompt = f"""You are the HR Policy & Compliance Expert Agent.
Your responsibility is to answer employee questions regarding company policies, the employee handbook, benefits, and workplace regulations.

CURRENT MEMORY CONTEXT:
{memory_context}

USER MESSAGE:
"{user_message}"

INSTRUCTIONS:
1. Identify the specific policy, benefit, or rule the employee is asking about.
2. Rely strictly on standard corporate compliance knowledge and any relevant details found in the memory context.
3. Do not provide binding legal advice. If a situation sounds like a serious grievance, advise the employee to speak directly with an HR Business Partner.
4. Keep your explanations clear, objective, and easy to understand, avoiding overly dense corporate jargon.

OUTPUT:
Provide a factual, policy-driven response. If you lack the exact company document, state that you will flag this for a human HR representative to follow up."""

    # Invoke LLM
    response = llm.invoke(prompt)
    return {"final_response": response.content}


def unknown_agent_node(state: HRState) -> dict:
    """
    Fallback reception node that handles vague, ambiguous, or out-of-scope inquiries.
    Requests clarifications or directs employees politely.

    Args:
        state (HRState): Current state containing employee ID and raw request.

    Returns:
        dict: State update dictionary containing the drafted 'final_response'.
    """
    user_message = state.get("user_message", "")
    memory_context = state.get("memory_context", "No prior context.")

    # Specialist prompt
    prompt = f"""You are the HR Reception & Clarification Agent.
The orchestrator routed this user to you because their request was either ambiguous, lacked sufficient detail, or fell outside standard HR categories (Leave, Scheduling, Policy).

CURRENT MEMORY CONTEXT:
{memory_context}

USER MESSAGE:
"{user_message}"

INSTRUCTIONS:
1. Do not expose internal system errors, confidence scores, or routing mechanics to the user.
2. Acknowledge their message politely.
3. If the request is completely unrelated to HR (e.g., IT support, casual chit-chat), gently remind the user that this portal is for HR requests (Leave, Scheduling, and Policies) and direct them to the appropriate department if obvious.
4. If the request seems HR-related but is too vague, ask a clarifying question to help them narrow down what they need (e.g., "Are you looking to schedule a meeting, or do you have a question about our time-off policy?").

OUTPUT:
Provide a brief, polite response that guides the user back on track or requests the specific details needed to assist them properly."""

    # Invoke LLM
    response = llm.invoke(prompt)
    return {"final_response": response.content}
