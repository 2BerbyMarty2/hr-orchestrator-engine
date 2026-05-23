<img width="1215" height="754" alt="Screenshot 2026-05-23 at 21 06 39" src="https://github.com/user-attachments/assets/540a953c-cd73-474b-8475-c964b35ed6a2" />
<img width="1218" height="753" alt="Screenshot 2026-05-23 at 21 06 29" src="https://github.com/user-attachments/assets/bb52a040-8d5b-4d5c-b223-ff7346101fce" />
# HR Automation Platform: Multi-Agent Task Routing Engine

## Project Overview
You will be developing a multi-agent task routing and memory engine for an HR automation platform, using a central Orchestrator Agent to route natural language requests to specialist sub-agents.

## Technical Requirements

### 1. Backend Stack
* Python 3.11+
* FastAPI framework implementation
* Langgraph
* SQLite database integration
* LLM APIs/Open-Source Models
* Environment configuration using a .env file

### 2. Core Functionality
**REST API endpoints for:**
* Request handling
* Audit retrieval
* Memory management
* Health monitoring

**Automated orchestration system for:**
* Intent classification with confidence scores
* Routing classified intents to appropriate sub-agents (Scheduling, Leave, Compliance, and Clarification)
* Memory retrieval to inject historical context into agent prompts
* Comprehensive audit logging system

### 3. System Modules in Intent Classification Engine
* Agent Router & Sub-Agent Stubs
* Two-tier Memory System (STM and LTM)
* Append-only Audit Log

## Evaluation Criteria

**Working System:**
* Server starts and pipeline executes end-to-end
* All 5 endpoints respond correctly

**Code Quality:**
* Modular design and separation of concerns
* Type annotations and docstrings

**Agent Architecture:**
* Clean agent boundaries
* Context injection, retry, and timeout logic

**Memory System:**
* STM and LTM functionality
* Sound and justified significance scoring logic

**Audit Log:**
* Append-only enforcement and presence of required fields

**Bug Finding & Fixes:**
* Identification and correction of starter-code bugs

**Report:**
* Explanation and honesty about trade-offs

*Note: The system includes appropriate fallback handling for uncertain requests and handles failures politely without exposing raw Python stack traces. Mock data is used for testing.*


# Implimentation

## Project Structure

app/
endpoint.py
main.py
request.py
route.py
