"""
FastAPI Route Handlers and Controller Layer.

This module exposes the REST API endpoints supporting the HR Orchestrator Engine.
It maps HTTP requests to the underlying LangGraph engine, implements persistent database
logging for audit tracks, and serves authorized employee directories and context memory states.
"""

import sqlite3
from fastapi import APIRouter, HTTPException, Query
from app.request import ChatRequest, MemoryPayload
from app.graph import hr_engine
from app.database.database import DatabaseClient

# Initialize the central APIRouter controller
main_router = APIRouter()

# Instantiate the SQLite Database client helper
db = DatabaseClient()


@main_router.get("/health", tags=["Monitoring"])
async def health_check():
    """
    Service health check endpoint verifying database connectivity and engine readiness.

    Returns:
        dict: Active system health metadata including connected tables.
    """
    try:
        tables = db.get_table_names()
        return {
            "status": "healthy",
            "database": "connected",
            "tables": tables,
            "engine": "ready",
        }
    except Exception:
        return {
            "status": "degraded",
            "database": "disconnected",
            "engine": "ready",
        }


@main_router.post("/api/v1/request", tags=["Orchestration"])
async def process_request(payload: ChatRequest):
    """
    Primary API transaction gateway that invokes the LangGraph HR orchestration flow.
    Enforces payload schemas, safely extracts formatted string responses from model structures,
    and commits a new transaction record directly into the SQLite audit log database.

    Args:
        payload (ChatRequest): Incoming Pydantic payload enclosing employee ID and natural query.

    Returns:
        dict: Transaction records enclosing intent classification, confidence scores, and drafted response.
    
    Raises:
        HTTPException: 429 Error if daily Gemini API quota is reached; 500 Error for general engine crashes.
    """
    initial_state = {
        "employee_id": payload.employee_id,
        "user_message": payload.message,
        "extracted_dates": [],
    }
    try:
        # Execute the compiled workflow pipeline with initial state inputs
        final_state = hr_engine.invoke(initial_state)
        
        # Safely extract plain text response from wrapped model list structures
        final_response = final_state.get("final_response", "")
        if isinstance(final_response, list):
            final_response = "".join(
                item.get("text", "") if isinstance(item, dict) else str(item)
                for item in final_response
            )
        elif not isinstance(final_response, str):
            final_response = str(final_response) if final_response is not None else ""
        final_response = final_response.strip()

        # Safely attempt to commit transaction logging entry
        try:
            with sqlite3.connect(db.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO audit_logs (timestamp, employee_id, user_message, classified_intent, confidence_score, final_response)
                    VALUES (datetime('now', 'localtime'), ?, ?, ?, ?, ?)
                    """,
                    (
                        payload.employee_id,
                        payload.message,
                        final_state.get("intent", "UNKNOWN"),
                        final_state.get("confidence", 0.0),
                        final_response,
                    ),
                )
                conn.commit()
        except Exception as e:
            # Enforce fault-tolerance: database logging anomalies must not crash the primary flow
            print(f"Failed to write to audit_logs: {e}")

        return {
            "employee_id": final_state.get("employee_id"),
            "intent":      final_state.get("intent"),
            "confidence":  final_state.get("confidence"),
            "final_response": final_response,
        }
    except Exception as e:
        err_str = str(e)
        # Intercept and return a detailed 429 status code if Gemini API quota is reached
        if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str or "quota" in err_str.lower():
            raise HTTPException(
                status_code=429,
                detail="router.py RO-001 error: Google Gemini API quota/rate limit exceeded (429 RESOURCE_EXHAUSTED). The free-tier limit is 20 requests per day. Please wait for the quota to reset or verify your API key.",
            )
        raise HTTPException(
            status_code=500,
            detail=f"router.py RO-001 error: The HR Orchestration Engine encountered an unexpected issue ({type(e).__name__}). Please try rephrasing.",
        )


@main_router.get("/api/v1/audit", tags=["Compliance"])
async def get_audit_logs(employee_id: str = Query(..., description="Filter logs by employee ID")):
    """
    Audit registry retrieval endpoint filtering logged transactions by employee.

    Args:
        employee_id (str): target Employee ID query parameter.

    Returns:
        List[dict]: Sorted array of logged transactional records.
    """
    try:
        with sqlite3.connect(db.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM audit_logs WHERE employee_id = ? ORDER BY timestamp DESC",
                (employee_id,),
            )
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.OperationalError:
        return []
    except Exception:
        raise HTTPException(status_code=500, detail="router.py RO-002 error: Failed to retrieve audit logs.")


@main_router.get("/api/v1/memory/{employee_id}", tags=["Memory System"])
async def get_memory(employee_id: str):
    """
    Memory store retrieval endpoint returning active Short/Long-Term context.

    Args:
        employee_id (str): Target Employee ID path parameter.

    Returns:
        List[dict]: Chronologically ordered active memories.
    """
    try:
        with sqlite3.connect(db.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM memory_store WHERE employee_id = ? ORDER BY timestamp DESC",
                (employee_id,),
            )
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.OperationalError:
        return []
    except Exception:
        raise HTTPException(status_code=500, detail="router.py RO-003 error: Failed to retrieve memory context.")


@main_router.post("/api/v1/memory", tags=["Memory System"])
async def manual_memory_injection(payload: MemoryPayload):
    """
    Manual context injection gateway into Short/Long Term memory registers.

    Args:
        payload (MemoryPayload): Payload enclosing tier, target session, and content.

    Returns:
        dict: Commit status.
    """
    if payload.memory_tier not in ("STM", "LTM"):
        raise HTTPException(status_code=400, detail="router.py RO-004 error: Memory tier must be 'STM' or 'LTM'.")
    try:
        with sqlite3.connect(db.db_path) as conn:
            conn.execute(
                """
                INSERT INTO memory_store (employee_id, memory_tier, content, significance_score)
                VALUES (?, ?, ?, ?)
                """,
                (payload.session_id, payload.memory_tier, payload.content, 1.0),
            )
            conn.commit()
        return {"status": "success", "message": "Memory committed successfully."}
    except Exception:
        raise HTTPException(status_code=500, detail="router.py RO-005 error: Failed to write memory.")


@main_router.get("/api/v1/employees", tags=["Monitoring"])
async def get_all_employees():
    """
    Authorized directory listing retrieval endpoint for active directory table rendering.

    Returns:
        List[dict]: Array of active database registered employee details.
    """
    try:
        employees = db.fetch_all_employees()
        return [
            {
                "employee_id": emp[0],
                "name": f"{emp[1]} {emp[2]}",
                "department": emp[3],
            }
            for emp in employees
        ]
    except Exception:
        raise HTTPException(status_code=500, detail="router.py RO-006 error: Failed to retrieve employees.")