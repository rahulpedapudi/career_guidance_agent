"""
FastAPI Backend for Career Guidance Agent.

Supports DEV_MODE for local development without auth.
In production, set DEV_MODE=false to require Google OAuth.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict

from career_agent.models import (
    UserProfileInput,
    SkillSnapshot,
    SkillEntry,
    HorizonOutput,
    Event,
    EventType,
    Stage,
    ExposureLevel,
    TimeCommitment,
)
from career_agent.agent import CareerGuidancePipeline
from career_agent.database import db

# ============================================================================
# Configuration
# ============================================================================

# Set DEV_MODE=false in production to require Google OAuth
# DEV_MODE = os.getenv("DEV_MODE", "true").lower() == "true"
DEV_MODE=False


# ============================================================================
# App State
# ============================================================================

user_profiles: dict[str, UserProfileInput] = {}
skill_snapshots: dict[str, SkillSnapshot] = {}
horizon_outputs: dict[str, HorizonOutput] = {}
pipeline = CareerGuidancePipeline()

# Chat agent for conversational AI
from career_agent.chat_agent import ChatAgent
chat_agent = ChatAgent()


# ============================================================================
# Request Models (DEV_MODE: user_id in body)
# ============================================================================

class OnboardingRequest(BaseModel):
    # Accept both user_id and userId
    user_id: str | None = Field(default=None)
    userId: str | None = Field(default=None)
    name: str | None = Field(default="User")
    stage: str | None = Field(default="first_year")
    graduation_year: int | None = None
    exposure_level: str | None = Field(default=None, alias="exposureLevel")
    exposureLevel: str | None = Field(default=None)
    learning_preferences: list[str] = Field(default_factory=list, alias="learningPreferences")
    learningPreferences: list[str] = Field(default_factory=list)
    weekly_time_commitment: str | None = Field(default="10-15", alias="weeklyTimeCommitment")
    weeklyTimeCommitment: str | None = Field(default=None)
    constraints: list[str] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    
    def get_user_id(self) -> str:
        return self.user_id or self.userId or "unknown"
    
    def get_exposure_level(self) -> str:
        return self.exposure_level or self.exposureLevel or "coursework"
    
    def get_time_commitment(self) -> str:
        return self.weekly_time_commitment or self.weeklyTimeCommitment or "10-15"
    
    def get_learning_preferences(self) -> list[str]:
        return self.learning_preferences or self.learningPreferences or []
    
    def get_name(self) -> str:
        return self.name or "User"
    
    def get_stage(self) -> str:
        return self.stage or "first_year"


class SkillUpdateRequest(BaseModel):
    user_id: str
    skills: list[SkillEntry]


class EventRequest(BaseModel):
    user_id: str
    event_type: EventType
    payload: dict = Field(default_factory=dict)


class HealthResponse(BaseModel):
    status: str
    message: str
    dev_mode: bool


# ============================================================================
# FastAPI App
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to DB
    await db.connect()
    
    if DEV_MODE:
        print("⚠️  DEV_MODE enabled - Auth is BYPASSED")
    else:
        print("🔒 Production mode - Google OAuth required")
    print("🚀 Career Guidance API starting...")
    
    yield
    
    # Close DB connection
    await db.close()
    print("👋 Career Guidance API shutting down...")


app = FastAPI(
    title="Career Guidance Agent API",
    description="Multi-agent career reasoning pipeline",
    version="2.3.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Helpers
# ============================================================================

def parse_time_commitment(value: str):
    """Map various time commitment formats to enum."""
    mapping = {
        "<5": TimeCommitment.UNDER_5,
        "5-10": TimeCommitment.FIVE_TO_TEN,
        "10-15": TimeCommitment.TEN_TO_FIFTEEN,
        "15+": TimeCommitment.OVER_15,
        "under_5": TimeCommitment.UNDER_5,
        "five_to_ten": TimeCommitment.FIVE_TO_TEN,
        "ten_to_fifteen": TimeCommitment.TEN_TO_FIFTEEN,
        "over_15": TimeCommitment.OVER_15,
    }
    return mapping.get(value, TimeCommitment.TEN_TO_FIFTEEN)


def parse_stage(value: str) -> Stage:
    try:
        return Stage(value)
    except ValueError:
        # Fallback mapping
        mapping = {
            "first year": Stage.FIRST_YEAR,
            "1st year": Stage.FIRST_YEAR,
            "second year": Stage.SECOND_YEAR,
            "2nd year": Stage.SECOND_YEAR,
            "third year": Stage.THIRD_YEAR,
            "3rd year": Stage.THIRD_YEAR,
            "final year": Stage.FINAL_YEAR,
            "4th year": Stage.FINAL_YEAR,
            "graduate": Stage.GRADUATE,
        }
        return mapping.get(value.lower(), Stage.FIRST_YEAR)


def parse_exposure(value: str) -> ExposureLevel:
    try:
        return ExposureLevel(value)
    except ValueError:
        # Fallback mapping
        mapping = {
            "just exploring": ExposureLevel.COURSEWORK,
            "built small projects": ExposureLevel.SMALL_PROJECTS,
            "built multiple projects": ExposureLevel.SERIOUS_PROJECTS,
            "professional experience": ExposureLevel.PROFESSIONAL,
            "coursework": ExposureLevel.COURSEWORK,
        }
        # Try partial matching
        val = value.lower()
        if "explor" in val: return ExposureLevel.COURSEWORK
        if "small" in val: return ExposureLevel.SMALL_PROJECTS
        if "multiple" in val or "serious" in val: return ExposureLevel.SERIOUS_PROJECTS
        if "prof" in val: return ExposureLevel.PROFESSIONAL
        return ExposureLevel.COURSEWORK


# ============================================================================
# Endpoints (No auth in DEV_MODE)
# ============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        message="Career Guidance API is running",
        dev_mode=DEV_MODE,
    )


@app.post("/api/onboard-debug")
async def onboard_debug(request: dict):
    """Debug endpoint - logs raw request body."""
    print(f"🔍 RAW REQUEST BODY: {request}")
    return {"received": request, "keys": list(request.keys())}


@app.post("/api/onboard", response_model=HorizonOutput)
async def onboard_user(request: OnboardingRequest):
    """Submit onboarding form."""
    try:
        user_id = request.get_user_id()
        name = request.get_name()
        stage = request.get_stage()
        exposure = request.get_exposure_level()
        time_commitment = request.get_time_commitment()
        learning_prefs = request.get_learning_preferences()
        
        print(f"📥 Onboard Request: user_id={user_id}, name={name}, stage={stage}, exposure={exposure}")
        
        profile = UserProfileInput(
            user_id=user_id,
            name=name,
            stage=parse_stage(stage),
            graduation_year=request.graduation_year,
            exposure_level=parse_exposure(exposure),
            learning_preferences=learning_prefs,
            weekly_time_commitment=parse_time_commitment(time_commitment),
            constraints=request.constraints,
            goals=request.goals,
            interests=request.interests,
        )
        
        user_profiles[user_id] = profile
        
        if user_id not in skill_snapshots:
            skill_snapshots[user_id] = SkillSnapshot(skills=[])
        
        event = Event(event_type=EventType.ONBOARDING_COMPLETED)
        
        result = pipeline.process_event(
            event=event,
            user_profile=profile,
            skill_snapshot=skill_snapshots[user_id],
        )
        horizon_outputs[user_id] = result
        print(f"✅ Horizon Output for {user_id}:\n{result.model_dump_json(indent=2)}")
        return result
        
    except Exception as e:
        print(f"❌ Onboarding Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/skills", response_model=HorizonOutput)
async def update_skills(request: SkillUpdateRequest):
    """Update user's skill snapshot."""
    if request.user_id not in user_profiles:
        raise HTTPException(status_code=404, detail="Complete onboarding first.")
    
    snapshot = SkillSnapshot(skills=request.skills)
    skill_snapshots[request.user_id] = snapshot
    
    event = Event(event_type=EventType.SKILL_UPDATED)
    
    try:
        result = pipeline.process_event(
            event=event,
            user_profile=user_profiles[request.user_id],
            skill_snapshot=snapshot,
        )
        horizon_outputs[request.user_id] = result
        print(f"✅ Horizon Output for {request.user_id}:\n{result.model_dump_json(indent=2)}")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/events", response_model=HorizonOutput)
async def trigger_event(request: EventRequest):
    """Trigger a generic event."""
    if request.user_id not in user_profiles:
        raise HTTPException(status_code=404, detail="Complete onboarding first.")
    
    event = Event(event_type=request.event_type, payload=request.payload)
    
    try:
        result = pipeline.process_event(
            event=event,
            user_profile=user_profiles[request.user_id],
            skill_snapshot=skill_snapshots.get(request.user_id, SkillSnapshot(skills=[])),
        )
        horizon_outputs[request.user_id] = result
        print(f"✅ Horizon Output for {request.user_id}:\n{result.model_dump_json(indent=2)}")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/horizon/{user_id}", response_model=HorizonOutput)
async def get_horizon(user_id: str):
    """Get cached HorizonOutput for a user."""
    if user_id not in horizon_outputs:
        raise HTTPException(status_code=404, detail="Complete onboarding first.")
    return horizon_outputs[user_id]


@app.get("/api/profile/{user_id}", response_model=UserProfileInput)
async def get_profile(user_id: str):
    """Get user's profile."""
    if user_id not in user_profiles:
        raise HTTPException(status_code=404, detail="User not found.")
    return user_profiles[user_id]


@app.get("/api/skills/{user_id}", response_model=SkillSnapshot)
async def get_skills(user_id: str):
    """Get user's skill snapshot."""
    if user_id not in skill_snapshots:
        raise HTTPException(status_code=404, detail="Skills not found.")
    return skill_snapshots[user_id]


# ============================================================================
# Chat Endpoint
# ============================================================================

class ChatRequest(BaseModel):
    user_id: str
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    response: str
    suggestions: list[str] = Field(default_factory=list)


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Conversational career guidance chat.
    
    Uses the user's HorizonOutput as context for personalized responses.
    Supports multi-turn conversations via session_id.
    """
    if request.user_id not in horizon_outputs:
        raise HTTPException(
            status_code=404, 
            detail="Complete onboarding first to use chat."
        )
    
    horizon = horizon_outputs[request.user_id]
    
    try:
        result = await chat_agent.chat(
            message=request.message,
            horizon=horizon,
            session_id=request.session_id,
            user_id=request.user_id,
        )
        return ChatResponse(**result)
    except Exception as e:
        print(f"❌ Chat Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/chat/session/{session_id}")
async def clear_chat_session(session_id: str):
    """Clear conversation history for a session."""
    await chat_agent.clear_session(session_id)
    return {"status": "ok", "message": f"Session {session_id} cleared"}
