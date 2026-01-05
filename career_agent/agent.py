"""
Career Guidance Agent Pipeline.

Main entry point that orchestrates all agents.
"""

from career_agent.models import (
    Event,
    EventType,
    UserProfileInput,
    SkillSnapshot,
    HorizonOutput,
    ProfileAnalysis,
    SkillAnalysis,
    CareerAnalysis,
)
from career_agent.supervisor import Supervisor
from career_agent.profile_agent import ProfileAgent
from career_agent.skill_agent import SkillAgent
from career_agent.career_recommendation_agent import CareerRecommendationAgent
from career_agent.reasoning_agent import ReasoningAgent


class CareerGuidancePipeline:
    """
    Main orchestrator for the career guidance system.
    
    Coordinates all agents based on events:
    - Supervisor decides which agents to run
    - Agents execute in deterministic order
    - Reasoning Agent produces final HorizonOutput
    """
    
    def __init__(self):
        self.supervisor = Supervisor()
        self.profile_agent = ProfileAgent()
        self.skill_agent = SkillAgent()
        self.career_agent = CareerRecommendationAgent()
        self.reasoning_agent = ReasoningAgent()
        
        # Cached agent outputs (would be persisted in production)
        self._profile_cache: dict[str, ProfileAnalysis] = {}
        self._skill_cache: dict[str, SkillAnalysis] = {}
        self._career_cache: dict[str, CareerAnalysis] = {}
    
    def process_event(
        self,
        event: Event,
        user_profile: UserProfileInput,
        skill_snapshot: SkillSnapshot | None = None,
    ) -> HorizonOutput:
        """
        Process an event through the agent pipeline.
        
        Args:
            event: The triggering event
            user_profile: User profile data
            skill_snapshot: Skill data
        
        Returns:
            HorizonOutput: The final synthesized output
        """
        user_id = user_profile.user_id
        
        # 1. Supervisor decides execution plan
        plan = self.supervisor.plan_execution(event)
        
        # 2. Get cached results or use defaults
        profile_result = self._profile_cache.get(user_id)
        skill_result = self._skill_cache.get(user_id)
        career_result = self._career_cache.get(user_id)
        
        try:
            # Profile Agent
            if plan.run_profile:
                profile_result = self.profile_agent.analyze(user_profile)
                self._profile_cache[user_id] = profile_result
            
            # Skill Agent
            if plan.run_skill and skill_snapshot:
                direction = None
                if career_result:
                    direction = career_result.primaryDirection.role
                skill_result = self.skill_agent.analyze(skill_snapshot, direction)
                self._skill_cache[user_id] = skill_result
            
            # Career Recommendation Agent
            if plan.run_career and profile_result:
                # Need skill analysis for career recommendation
                if not skill_result and skill_snapshot:
                    skill_result = self.skill_agent.analyze(skill_snapshot)
                    self._skill_cache[user_id] = skill_result
                elif not skill_result:
                    skill_result = SkillAnalysis(
                        skillsCompleted=[],
                        skillsInProgress=[],
                        skillsPlanned=[],
                        gaps=[],
                        strengths=[],
                        emergingSkills=[],
                    )
                
                # Pass user's explicit interests and goals for priority matching
                career_result = self.career_agent.recommend(
                    profile=profile_result,
                    skill_analysis=skill_result,
                    user_interests=user_profile.interests,
                    user_goals=user_profile.goals,
                )
                self._career_cache[user_id] = career_result
            
            # Reasoning Agent
            if plan.run_reasoning:
                # Ensure we have all required outputs
                if not profile_result:
                    profile_result = self.profile_agent.analyze(user_profile)
                    self._profile_cache[user_id] = profile_result
                
                if not skill_result:
                    if skill_snapshot:
                        skill_result = self.skill_agent.analyze(skill_snapshot)
                    else:
                        skill_result = SkillAnalysis(
                            skillsCompleted=[],
                            skillsInProgress=[],
                            skillsPlanned=[],
                            gaps=[],
                            strengths=[],
                            emergingSkills=[],
                        )
                    self._skill_cache[user_id] = skill_result
                
                if not career_result:
                    career_result = self.career_agent.recommend(
                        profile=profile_result,
                        skill_analysis=skill_result,
                        user_interests=user_profile.interests,
                        user_goals=user_profile.goals,
                    )
                    self._career_cache[user_id] = career_result
                
                return self.reasoning_agent.synthesize(
                    user_id=user_id,
                    profile=profile_result,
                    skill_analysis=skill_result,
                    career=career_result,
                )
            
            # Shouldn't reach here, but return a default
            raise ValueError("No reasoning step in execution plan")
        
        except Exception as e:
            if self.supervisor.should_abort(True):
                raise RuntimeError(f"Pipeline aborted: {e}") from e
            raise


def run_pipeline(
    event_type: EventType,
    user_profile: UserProfileInput,
    skill_snapshot: SkillSnapshot | None = None,
    payload: dict | None = None,
) -> HorizonOutput:
    """Run the career guidance pipeline for an event."""
    pipeline = CareerGuidancePipeline()
    event = Event(event_type=event_type, payload=payload or {})
    return pipeline.process_event(event, user_profile, skill_snapshot)
