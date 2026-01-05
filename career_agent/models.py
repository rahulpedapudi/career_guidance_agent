"""
Core data models for the Career Guidance Agent pipeline.
Schema matches frontend-expected HorizonOutput format.
"""

from datetime import datetime
from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field


# ============================================================================
# Enums
# ============================================================================

class Stage(str, Enum):
    FIRST_YEAR = "first_year"
    SECOND_YEAR = "second_year"
    THIRD_YEAR = "third_year"
    FINAL_YEAR = "final_year"
    GRADUATE = "graduate"


class ExposureLevel(str, Enum):
    COURSEWORK = "coursework"
    SMALL_PROJECTS = "small_projects"
    SERIOUS_PROJECTS = "serious_projects"
    PROFESSIONAL = "professional"


class TimeCommitment(str, Enum):
    UNDER_5 = "<5"
    FIVE_TO_TEN = "5-10"
    TEN_TO_FIFTEEN = "10-15"
    OVER_15 = "15+"


class SkillLevel(str, Enum):
    AWARE = "aware"
    USED_A_BIT = "used_a_bit"
    COMFORTABLE = "comfortable"


class EventType(str, Enum):
    ONBOARDING_COMPLETED = "onboarding_completed"
    SKILL_UPDATED = "skill_updated"
    DIRECTION_CHANGED = "direction_changed"
    CHECK_IN = "check_in"


class Level(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Confidence(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class Impact(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PhaseStatus(str, Enum):
    NOT_STARTED = "not-started"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"


class InsightType(str, Enum):
    OPPORTUNITY = "opportunity"
    RISK = "risk"
    TREND = "trend"


# ============================================================================
# Input Models
# ============================================================================

class UserProfileInput(BaseModel):
    """Raw onboarding data from user."""
    user_id: str
    name: str
    stage: Stage
    graduation_year: int | None = None
    exposure_level: ExposureLevel
    learning_preferences: list[str] = Field(default_factory=list, max_length=2)
    weekly_time_commitment: TimeCommitment
    constraints: list[str] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)


class SkillEntry(BaseModel):
    """Single skill with proficiency level."""
    skill: str
    level: SkillLevel


class SkillSnapshot(BaseModel):
    """User's current skill state."""
    skills: list[SkillEntry]


class Event(BaseModel):
    """Normalized event that triggers reasoning."""
    event_type: EventType
    payload: dict = Field(default_factory=dict)


# ============================================================================
# Agent Output Models (Individual Agents)
# ============================================================================

class ExecutionPlan(BaseModel):
    """Supervisor output: which agents to run."""
    run_profile: bool = False
    run_skill: bool = False
    run_career: bool = False
    run_reasoning: bool = False


# Profile Agent Output
class ProfileBackground(BaseModel):
    education: str
    experience: str
    currentFocus: str


class ProfilePreferences(BaseModel):
    learningStyle: list[str]
    timeAvailable: str
    goals: list[str]


class ProfileAnalysis(BaseModel):
    """Profile Agent output."""
    name: str
    role: str
    level: Level
    nextLevel: Level | None = None
    progressToNextLevel: int = 0  # 0-100
    exposureLevel: str
    learningStyle: str
    background: ProfileBackground
    preferences: ProfilePreferences


# Skill Agent Output
class SkillGap(BaseModel):
    skill: str
    impact: Impact
    reason: str
    blockedSkills: list[str] = Field(default_factory=list)


class EmergingSkill(BaseModel):
    skill: str
    relevance: str
    reason: str


class SkillAnalysis(BaseModel):
    """Skill Agent output."""
    skillsCompleted: list[str] = Field(default_factory=list)
    skillsInProgress: list[str] = Field(default_factory=list)
    skillsPlanned: list[str] = Field(default_factory=list)
    gaps: list[SkillGap] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    emergingSkills: list[EmergingSkill] = Field(default_factory=list)


# Career Agent Output
class CareerMatch(BaseModel):
    role: str
    matchScore: int  # 0-100
    reason: str | None = None
    timeToReady: str | None = None


class MarketInsights(BaseModel):
    demandTrend: str
    salaryRange: str
    topCompanies: list[str]


class CareerAnalysis(BaseModel):
    """Career Agent output."""
    primaryDirection: CareerMatch
    alternativeDirections: list[CareerMatch] = Field(default_factory=list)
    marketInsights: MarketInsights | None = None


# ============================================================================
# HorizonOutput Components (Frontend-Consumed)
# ============================================================================

class ProfileSection(BaseModel):
    name: str
    role: str
    level: str
    nextLevel: str | None = None
    progressToNextLevel: int = 0
    exposureLevel: str
    learningStyle: str


class CareerDirection(BaseModel):
    primaryRole: str
    secondaryRoles: list[str] = Field(default_factory=list)
    matchScore: int
    confidence: Confidence
    reasoning: str


class ImmediateFocus(BaseModel):
    skill: str
    reason: str
    timeWindow: str
    priority: Priority


class SkillGapOutput(BaseModel):
    skill: str
    impact: str
    reason: str


class SkillsSnapshot(BaseModel):
    completed: list[str] = Field(default_factory=list)
    inProgress: list[str] = Field(default_factory=list)
    planned: list[str] = Field(default_factory=list)
    gaps: list[SkillGapOutput] = Field(default_factory=list)


class ActiveInterest(BaseModel):
    id: str
    title: str
    progress: int  # 0-100
    status: str  # Active | Planned | Completed | Paused
    color: str
    modulesRemaining: int = 0
    icon: str = "star"



class NextAction(BaseModel):
    title: str
    subtitle: str
    duration: str
    type: str  # learning | project | practice
    actionUrl: str | None = None


class Insight(BaseModel):
    type: InsightType
    message: str
    confidence: Confidence


class SkillResource(BaseModel):
    type: str  # course | article | video | tool
    title: str
    link: str | None = None
    level: str = "Beginner"


class RoadmapSkill(BaseModel):
    id: str
    name: str
    status: str
    description: str = ""
    resources: list[SkillResource] = Field(default_factory=list)
    practice: list[str] = Field(default_factory=list)


class RoadmapPhase(BaseModel):
    id: str
    title: str
    status: PhaseStatus
    progress: int  # 0-100
    timeRange: str = ""  # e.g., "Weeks 1-4"
    skills: list[RoadmapSkill] = Field(default_factory=list)


class Roadmap(BaseModel):
    id: str
    title: str
    totalPhases: int
    currentPhase: int
    overallProgress: int  # 0-100
    phases: list[RoadmapPhase] = Field(default_factory=list)


# ============================================================================
# Final Output (Frontend-Consumed)
# ============================================================================

class ActivityItem(BaseModel):
    id: str
    title: str
    time: str
    xp: int


class Stats(BaseModel):
    skillsLearned: int
    learningHours: int
    roadmapCompletion: int  # Renamed from roadmapProgress
    domainsExplored: int    # Renamed from domains


class DailyInsight(BaseModel):
    message: str  # Renamed from text
    type: str = "motivation"
    author: str | None = None


class HorizonOutput(BaseModel):
    """
    The ONLY output consumed by the frontend.
    Produced exclusively by the Reasoning Agent.
    """
    version: str = "1.0"
    generatedAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    userId: str
    
    profile: ProfileSection
    stats: Stats
    dailyInsight: DailyInsight
    careerDirection: CareerDirection = None
    immediateFocus: ImmediateFocus = None
    skillsSnapshot: SkillsSnapshot
    activeInterests: list[ActiveInterest] = Field(default_factory=list)
    nextAction: NextAction
    recentActivity: list[ActivityItem] = Field(default_factory=list)
    
    insights: list[Insight] = Field(default_factory=list)
    roadmaps: list[Roadmap] = Field(default_factory=list)  # One per active interest
