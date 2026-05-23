# HR Automation Platform: Multi-Agent Task Routing Engine

## Project Overview
This project is an enterprise-grade multi-agent task routing and memory engine designed for an HR automation platform. It utilizes a central **Orchestrator Agent** to process natural language requests from employees, classify their intents, and dynamically route them to domain-expert sub-agents. 

The system integrates real-time database queries, a two-tier conversational memory system, and an immutable audit log to ensure compliance, accuracy, and a seamless employee experience.

## Technical Stack
* **Language:** Python 3.11+
* **Framework:** FastAPI (RESTful API architecture)
* **Orchestration:** LangGraph (State management and agent routing)
* **AI/LLM:** Google Gemini API (`gemini-3.5-flash`) via LangChain
* **Database:** Embedded SQLite (Corporate records, memory, and audit logs)
* **Frontend:** HTML/JS/CSS (Interactive technical sandbox UI)

## Core System Features

### 1. Intelligent Orchestration & Routing
* **Intent Classification:** Evaluates user messages to determine intent (LEAVE, SCHEDULE, POLICY, UNKNOWN) with calculated confidence scores.
* **Specialist Sub-Agents:** * **Leave Agent:** Manages vacation/PTO balances and requests.
  * **Schedule Agent:** Coordinates calendar events and shifts.
  * **Policy Agent:** Acts as an interactive employee handbook.
  * **Clarification Agent:** Handles fallback routing with polite clarification requests.

### 2. Contextual Memory System
* **Two-Tier Architecture:** Features Short-Term Memory (STM) for active session context and Long-Term Memory (LTM) for persistent user preferences.
* **Context Injection:** Agents automatically retrieve and inject historical memory into their prompts to avoid repetitive user inputs.

### 3. Compliance & Audit Logging
* **Append-Only Ledger:** An immutable `audit_logs` database table enforces strict compliance.
* **Comprehensive Tracking:** Automatically records timestamps, employee IDs, raw queries, classified intents, confidence scores, and final drafted responses.

---

## Implementation & Project Structure

```text
hr-orchestrator-engine/
│
├── app/                        # Main Application Package
│   ├── agents.py               # Specialist execution nodes & Gemini LLM integration
│   ├── graph.py                # LangGraph workflow, edges, and routing logic
│   ├── main.py                 # FastAPI application initialization & lifespan management
│   ├── request.py              # Pydantic schemas for API payload validation
│   ├── router.py               # REST API endpoints and database transaction logic
│   ├── state.py                # Shared HRState dictionary and Orchestrator node
│   └── database/               # Database Layer
│       ├── database.py         # SQLite client, schemas, and query methods
│       └── hr_database.db      # Embedded SQLite database instance
│
├── frontend_ui/                # Client Interface
│   └── index.html              # Interactive chat sandbox and developer dashboard
│
├── help-docs/                  # Documentation & Notes
│   ├── dev_setup_notes.txt     
│   ├── report.txt              
│   └── sql_code.txt            
│
├── .env                        # Environment variables (API Keys)
├── .gitignore
├── requirements.txt            # Project dependencies
└── README.md

```

<div align="center">
  <img width="1215" height="754" alt="Screenshot 2026-05-23 at 21 06 39" src="https://github.com/user-attachments/assets/540a953c-cd73-474b-8475-c964b35ed6a2" />
  <br>
  <img width="1218" height="753" alt="Screenshot 2026-05-23 at 21 06 29" src="https://github.com/user-attachments/assets/bb52a040-8d5b-4d5c-b223-ff7346101fce" />
</div>


## Setup & Execution

**1. Clone the repository and navigate to the root directory:**

```bash
cd hr-orchestrator-engine

```

**2. Create and activate a Python virtual environment:**

```bash
python3 -m venv .venv
source .venv/bin/activate

```

**3. Install required dependencies:**

```bash
pip install -r requirements.txt

```

**4. Configure Environment Variables:**
Create a `.env` file in the root directory and add your LLM API Key:

```env
GEMINI_API_KEY=your_google_gemini_api_key_here

```

**5. Run the FastAPI Application:**

```bash
uvicorn app.main:app --reload

```

**6. Access the System:**

* **Frontend UI Sandbox:** Open `http://127.0.0.1:8000/` in your browser.
* **API Documentation (Swagger):** Navigate to `http://127.0.0.1:8000/docs`.
* **Health Check:** Navigate to `http://127.0.0.1:8000/health`.

## REST API Endpoints Overview

* `POST /api/v1/request`: Primary gateway for natural language HR queries.
* `GET /api/v1/memory/{employee_id}`: Retrieves active session memory context.
* `POST /api/v1/memory`: Manual injection gateway for STM/LTM context.
* `GET /api/v1/audit`: Retrieves complete transaction logs for compliance.
* `GET /api/v1/employees`: Directory listing for the active database.

```

```
