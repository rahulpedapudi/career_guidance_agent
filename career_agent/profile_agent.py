"""
Profile Agent — Human Model Classifier.

Uses LLM (Gemini) to infer user persona, level, and detailed background.
Falls back to rule-based logic if no API key is configured.
"""

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load env from current directory or specific path
load_dotenv()
load_dotenv("career_agent/.env")  # Try specific location if needed

from career_agent.models import (
    UserProfileInput,
    ProfileAnalysis,
    ProfileBackground,
    ProfilePreferences,
    Level,
    Stage,
    ExposureLevel,
    TimeCommitment,
)


# ============================================================================
# Rule-Based Helpers (Fallback)
# ============================================================================

def determine_level(exposure: ExposureLevel, stage: Stage) -> Level:
    """Determine user's current level based on exposure and stage."""
    if exposure == ExposureLevel.PROFESSIONAL:
        return Level.ADVANCED
    if exposure == ExposureLevel.SERIOUS_PROJECTS:
        return Level.INTERMEDIATE
    if exposure == ExposureLevel.SMALL_PROJECTS:
        if stage in (Stage.THIRD_YEAR, Stage.FINAL_YEAR, Stage.GRADUATE):
            return Level.INTERMEDIATE
        return Level.BEGINNER
    return Level.BEGINNER


def get_next_level(current: Level) -> Level | None:
    """Get the next level to progress to."""
    if current == Level.BEGINNER:
        return Level.INTERMEDIATE
    if current == Level.INTERMEDIATE:
        return Level.ADVANCED
    return None


def estimate_progress(exposure: ExposureLevel, stage: Stage) -> int:
    """Estimate progress toward next level (0-100)."""
    base = 0
    if exposure == ExposureLevel.COURSEWORK:
        base = 20
    elif exposure == ExposureLevel.SMALL_PROJECTS:
        base = 40
    elif exposure == ExposureLevel.SERIOUS_PROJECTS:
        base = 65
    elif exposure == ExposureLevel.PROFESSIONAL:
        base = 85
    
    if stage in (Stage.THIRD_YEAR, Stage.FINAL_YEAR):
        base = min(base + 15, 95)
    
    return base


def format_exposure_level(exposure: ExposureLevel) -> str:
    """Human-readable exposure level."""
    mapping = {
        ExposureLevel.COURSEWORK: "Mostly coursework",
        ExposureLevel.SMALL_PROJECTS: "Built small projects",
        ExposureLevel.SERIOUS_PROJECTS: "Serious projects/internships",
        ExposureLevel.PROFESSIONAL: "Working professionally",
    }
    return mapping.get(exposure, "Learning")


def format_time_commitment(time: TimeCommitment) -> str:
    """Human-readable time commitment."""
    mapping = {
        TimeCommitment.UNDER_5: "<5 hours/week",
        TimeCommitment.FIVE_TO_TEN: "5-10 hours/week",
        TimeCommitment.TEN_TO_FIFTEEN: "10-15 hours/week",
        TimeCommitment.OVER_15: "15+ hours/week",
    }
    return mapping.get(time, "Unknown")


def format_education(stage: Stage, graduation_year: int | None) -> str:
    """Format education string."""
    stage_map = {
        Stage.FIRST_YEAR: "1st Year",
        Stage.SECOND_YEAR: "2nd Year", 
        Stage.THIRD_YEAR: "3rd Year",
        Stage.FINAL_YEAR: "Final Year",
        Stage.GRADUATE: "Graduate",
    }
    base = stage_map.get(stage, "Student")
    if graduation_year:
        return f"{base} (Graduating {graduation_year})"
    return base


def infer_role(interests: list[str], exposure: ExposureLevel) -> str:
    """Infer aspirational role from interests."""
    interests_lower = [i.lower() for i in interests]
    
    if any("ml" in i or "machine learning" in i or "ai" in i for i in interests_lower):
        return "Aspiring ML Engineer"
    if any("data" in i for i in interests_lower):
        return "Aspiring Data Scientist"
    if any("frontend" in i or "react" in i or "ui" in i for i in interests_lower):
        return "Aspiring Frontend Developer"
    if any("backend" in i or "api" in i or "server" in i for i in interests_lower):
        return "Aspiring Backend Developer"
    if any("full" in i or "web" in i for i in interests_lower):
        return "Aspiring Full Stack Developer"
    if any("devops" in i or "cloud" in i or "infra" in i for i in interests_lower):
        return "Aspiring DevOps Engineer"
    
    if exposure == ExposureLevel.PROFESSIONAL:
        return "Software Engineer"
    return "Aspiring Software Developer"


# ============================================================================
# Profile Agent
# ============================================================================

class ProfileAgent:
    """
    Profile Agent — Human Model Classifier.
    
    Uses LLM (Gemini) to infer user persona, level, and detailed background.
    Falls back to rule-based logic if no API key is configured.
    """
    
    def __init__(self):
        # Check for API Key
        api_key = os.getenv("GOOGLE_API_KEY")
        self.use_llm = False
        self.model = None
        
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel(
                    model_name="gemini-2.5-flash",
                    generation_config={"response_mime_type": "application/json"}
                )
                self.use_llm = True
                print("✨ ProfileAgent: LLM Enabled (Gemini 2.5 Flash)")
            except Exception as e:
                print(f"⚠️ ProfileAgent: Failed to configure LLM: {e}")
        else:
            print("⚠️ ProfileAgent: LLM Disabled (No API Key) - Using Rule-Based Fallback")

    def analyze(self, user_profile: UserProfileInput) -> ProfileAnalysis:
        """Analyze user profile to determine persona and detailed attributes."""
        if self.use_llm and self.model:
            try:
                return self._analyze_with_llm(user_profile)
            except Exception as e:
                print(f"❌ LLM Analysis Failed: {e}. Falling back to rules.")
        
        return self._analyze_rule_based(user_profile)

    def _analyze_with_llm(self, user: UserProfileInput) -> ProfileAnalysis:
        """Use Gemini to infer profile details."""
        prompt = f"""
        You are an expert technical career counselor. Analyze the following student profile and infer their detailed professional persona.

        User Data:
        {user.model_dump_json(indent=2)}

        Task:
        1. Infer their specific technical 'role' (e.g. "Aspiring Full Stack Dev", "Data Science Enthusiast") based on interests and goals.
        2. Determine their 'level' (beginner, intermediate, or advanced) based on stage and exposure.
        3. Estimate 'progressToNextLevel' (0-100).
        4. Summarize their 'background' (education, experience context, current focus).
        5. Infer 'preferences' (learning style nuances, time management).

        Output JSON strictly matching this schema:
        {{
            "name": "{user.name}",
            "role": "string",
            "level": "beginner|intermediate|advanced",
            "nextLevel": "string (optional value from beginner|intermediate|advanced)",
            "progressToNextLevel": int,
            "exposureLevel": "string (human readable)",
            "learningStyle": "string",
            "background": {{
                "education": "string",
                "experience": "string",
                "currentFocus": "string"
            }},
            "preferences": {{
                "learningStyle": ["string"],
                "timeAvailable": "string",
                "goals": ["string"]
            }}
        }}
        """
        
        response = self.model.generate_content(prompt)
        data = json.loads(response.text)
        
        # Helper to parse level safely
        def parse_level(val):
            try:
                if not val: return Level.BEGINNER
                return Level(val.lower())
            except:
                return Level.BEGINNER
        
        level = parse_level(data.get("level", "beginner"))
        next_level_str = data.get("nextLevel")
        next_level = parse_level(next_level_str) if next_level_str else None
            
        return ProfileAnalysis(
            name=user.name,
            role=data.get("role", "Aspiring Technologist"),
            level=level,
            nextLevel=next_level,
            progressToNextLevel=data.get("progressToNextLevel", 0),
            exposureLevel=data.get("exposureLevel", format_exposure_level(user.exposure_level)),
            learningStyle=data.get("learningStyle", "Flexible"),
            background=ProfileBackground(**data.get("background", {
                "education": format_education(user.stage, user.graduation_year),
                "experience": format_exposure_level(user.exposure_level),
                "currentFocus": "Building core skills"
            })),
            preferences=ProfilePreferences(**data.get("preferences", {
                "learningStyle": user.learning_preferences,
                "timeAvailable": format_time_commitment(user.weekly_time_commitment),
                "goals": user.goals
            }))
        )

    def _analyze_rule_based(self, profile: UserProfileInput) -> ProfileAnalysis:
        """Fallback rule-based analysis."""
        level = determine_level(profile.exposure_level, profile.stage)
        next_level = get_next_level(level)
        progress = estimate_progress(profile.exposure_level, profile.stage)
        
        role = infer_role(
            profile.interests + profile.goals,
            profile.exposure_level
        )
        
        learning_style = "Self-paced"
        if profile.learning_preferences:
            learning_style = profile.learning_preferences[0]
        
        return ProfileAnalysis(
            name=profile.name,
            role=role,
            level=level,
            nextLevel=next_level,
            progressToNextLevel=progress,
            exposureLevel=format_exposure_level(profile.exposure_level),
            learningStyle=learning_style,
            background=ProfileBackground(
                education=format_education(profile.stage, profile.graduation_year),
                experience=format_exposure_level(profile.exposure_level),
                currentFocus="Learning fundamentals" if level == Level.BEGINNER else "Building expertise",
            ),
            preferences=ProfilePreferences(
                learningStyle=profile.learning_preferences or ["Self-paced"],
                timeAvailable=format_time_commitment(profile.weekly_time_commitment),
                goals=profile.goals or ["Build skills", "Get opportunities"],
            ),
        )
