from fastapi import FastAPI

app = FastAPI()


@app.get("/user_request")
def user_request():
    return {"message": "HR Orchestrator Engine Running"}

@app.get("/health")
def health():
    return {"status": "ok"}
