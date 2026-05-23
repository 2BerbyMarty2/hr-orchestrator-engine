"""
HR Orchestrator Graph Construction Module.

This module defines the architectural graph workflow for routing employee inquiries
to specific domain-expert agents using LangGraph. The orchestrator node classifies
intents and passes the state to conditional routing functions to reach specialized agents.
"""

from langgraph.graph import StateGraph, END

from app.state import HRState, orchestrator_node
from app.agents import (
    leave_agent_node,
    schedule_agent_node,
    policy_agent_node,       # renamed from compliance_agent_node
    unknown_agent_node,
)

# Immutable set of authorized downstream agent node identifiers
_AGENT_NODES = frozenset({"leave_agent", "schedule_agent", "policy_agent", "unknown_agent"})


def route_to_agent(state: HRState) -> str:
    """
    Conditional router function that maps classified intents to downstream graph nodes.

    Args:
        state (HRState): The active shared state dictionary containing the classified intent.

    Returns:
        str: The registered node name of the target specialist agent. Defaults to "unknown_agent".
    """
    intent = state.get("intent")

    # Map state classification outputs strictly to target LangGraph node names
    routes = {
        "LEAVE": "leave_agent",
        "SCHEDULE": "schedule_agent",
        "POLICY": "policy_agent",    # matches orchestrator classification key exactly
        "UNKNOWN": "unknown_agent",
    }

    return routes.get(intent, "unknown_agent")


# ── LangGraph Workflow Construction ──────────────────────────────────────────

# Initialize StateGraph with the custom HRState blueprint
workflow = StateGraph(HRState)

# Register workflow nodes corresponding to execution handlers
workflow.add_node("orchestrator", orchestrator_node)
workflow.add_node("leave_agent", leave_agent_node)
workflow.add_node("schedule_agent", schedule_agent_node)
workflow.add_node("policy_agent", policy_agent_node)
workflow.add_node("unknown_agent", unknown_agent_node)

# Set the central orchestrator classification node as the primary entry point
workflow.set_entry_point("orchestrator")

# Construct conditional routing transitions from orchestrator based on intent
workflow.add_conditional_edges("orchestrator", route_to_agent, _AGENT_NODES)

# Bind all terminal agent nodes directly to the End node
for agent_node in _AGENT_NODES:
    workflow.add_edge(agent_node, END)

# Compile compiled runnable graph interface
hr_engine = workflow.compile()