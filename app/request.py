# app/requests.py

from pydantic import BaseModel, Field

# ==========================================
# 1. CORE ORCHESTRATION SCHEMA
# ==========================================
class ChatRequest(BaseModel):
    """
    Schema for the main POST /api/v1/request endpoint.
    Validates the incoming message before passing it to the LangGraph engine.
    """
    employee_id: str = Field(
        ..., 
        description="Unique identifier for the user or session (e.g., 'EMP_123')."
    )
    message: str = Field(
        ..., 
        description="The natural language request from the user."
    )


# ==========================================
# 2. MEMORY MANAGEMENT SCHEMA
# ==========================================
class MemoryPayload(BaseModel):
    """
    Schema for the POST /api/v1/memory endpoint.
    Used for manual injection of context into the user's history.
    """
    session_id: str = Field(
        ..., 
        description="Unique identifier matching the user's active session."
    )
    memory_tier: str = Field(
        ..., 
        description="Must be strictly 'STM' (Short-Term Memory) or 'LTM' (Long-Term Memory).",
        pattern="^(STM|LTM)$"  # FastAPI will automatically reject anything else
    )
    content: str = Field(
        ..., 
        description="The actual context, preference, or fact to store in memory."
    )