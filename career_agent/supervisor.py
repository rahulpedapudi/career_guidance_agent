"""
Supervisor Agent — Event Router (Pure Logic).

Decides which agents to run for a given event.
No LLM, deterministic execution.
"""

from career_agent.models import Event, EventType, ExecutionPlan


def route_event(event: Event) -> ExecutionPlan:
    """
    Route an event to the appropriate agents.
    
    Rules:
    - onboarding_completed: Run all agents (full pipeline)
    - skill_updated: Run skill + reasoning (skip profile/career)
    - direction_changed: Run career + reasoning (skip profile/skill)  
    - check_in: Run reasoning only (use cached data)
    """
    match event.event_type:
        case EventType.ONBOARDING_COMPLETED:
            return ExecutionPlan(
                run_profile=True,
                run_skill=True,
                run_career=True,
                run_reasoning=True,
            )
        
        case EventType.SKILL_UPDATED:
            return ExecutionPlan(
                run_profile=False,
                run_skill=True,
                run_career=False,
                run_reasoning=True,
            )
        
        case EventType.DIRECTION_CHANGED:
            return ExecutionPlan(
                run_profile=False,
                run_skill=False,
                run_career=True,
                run_reasoning=True,
            )
        
        case EventType.CHECK_IN:
            return ExecutionPlan(
                run_profile=False,
                run_skill=False,
                run_career=False,
                run_reasoning=True,
            )
        
        case _:
            # Unknown event: do nothing
            return ExecutionPlan()


class Supervisor:
    """
    Orchestrator for the agent pipeline.
    
    Responsibilities:
    - Interpret normalized event intent
    - Select agents to execute
    - Enforce correct execution order
    - Prevent unnecessary recomputation
    """
    
    def plan_execution(self, event: Event) -> ExecutionPlan:
        """Determine which agents to run for this event."""
        return route_event(event)
    
    def should_abort(self, previous_agent_failed: bool) -> bool:
        """If any agent fails, abort the entire pipeline."""
        return previous_agent_failed
