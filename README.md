# HR Orchestrator Engine

A multi-agent HR automation backend built with FastAPI, LangGraph, and SQLite.

This project uses a central Orchestrator Agent to classify and route natural language HR requests to specialized sub-agents such as:
- Scheduling Agent
- Leave Agent
- Compliance Agent
- Clarification Agent

## Features

- FastAPI REST API
- Multi-agent orchestration
- Intent classification with confidence scores
- Short-Term and Long-Term memory system
- Append-only audit logging
- SQLite database integration
- LangGraph workflow pipeline
- Error handling and fallback responses

## Tech Stack

- Python 3.11+
- FastAPI
- LangGraph
- SQLite
- Pydantic
- dotenv

## Project Structure

```text
app/
├── agents/
├── api/
├── database/
├── memory/
├── schemas/
├── services/
└── utils/
