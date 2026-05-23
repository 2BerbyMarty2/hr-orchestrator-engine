# app/main.py

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from app.router import main_router 


# from app.database import init_db


# ==========================================
# 1. LIFESPAN (replaces deprecated @app.on_event)
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown logic."""
    print("Starting HR Orchestrator Engine...")
    # init_db()  # Uncomment once database.py is fully set up
    yield
    print("HR Orchestrator Engine shutting down.")


# ==========================================
# 2. APP INITIALIZATION
# ==========================================
app = FastAPI(
    title="Enterprise HR Agent Routing Engine",
    description="Multi-agent task routing and memory engine powered by LangGraph.",
    version="1.0.0",
    lifespan=lifespan,
)


# ==========================================
# 3. GLOBAL EXCEPTION HANDLER
# ==========================================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    print(f"main.py MA-001 error: System Error Captured: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "main.py MA-002 error: Internal System Error",
            "message": (
                "The HR orchestration engine encountered an unexpected issue "
                "processing your request. Please try again later."
            ),
        },
    )


# ==========================================
# 4. ROUTER & STATIC FILES
# ==========================================
app.include_router(main_router)

app.mount("/frontend_ui", StaticFiles(directory="frontend_ui"), name="frontend_ui")


@app.get("/", tags=["UI"])
async def serve_frontend() -> FileResponse:
    return FileResponse("frontend_ui/index.html")


# ==========================================
# 5. LOCAL EXECUTION
# ==========================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)