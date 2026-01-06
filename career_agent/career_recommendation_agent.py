"""
Career Recommendation Agent — Directional Hypotheses.

Produces rich career analysis with primaryRole, matchScore, alternatives.
NOW POWERED BY GEMINI 2.5 FLASH (with rule-based fallback).
"""

import os
import json
import google.generativeai as genai

from career_agent.models import (
    ProfileAnalysis,
    SkillAnalysis,
    CareerAnalysis,
    CareerMatch,
    MarketInsights,
    Level,
)


# Career role definitions with requirements and market insights
# (Kept as fallback and for reference)
CAREER_ROLES = {
    "ml_engineer": {
        "title": "Machine Learning Engineer",
        "required_skills": ["python", "machine_learning", "statistics", "linear_algebra"],
        "helpful_skills": ["deep_learning", "data_structures", "algorithms"],
        "keywords": ["ml", "machine learning", "ai", "artificial intelligence", "deep learning"],
        "market": MarketInsights(
            demandTrend="increasing",
            salaryRange="12-30 LPA",
            topCompanies=["Google", "Microsoft", "Amazon", "Meta", "Startups"],
        ),
        "time_to_ready": {"beginner": "18-24 months", "intermediate": "6-12 months", "advanced": "Ready now"},
    },
    "data_scientist": {
        "title": "Data Scientist",
        "required_skills": ["python", "statistics", "sql", "data_analysis"],
        "helpful_skills": ["machine_learning", "data_structures"],
        "keywords": ["data", "analytics", "statistics", "insights"],
        "market": MarketInsights(
            demandTrend="stable",
            salaryRange="10-25 LPA",
            topCompanies=["Amazon", "Flipkart", "Swiggy", "Analytics firms"],
        ),
        "time_to_ready": {"beginner": "12-18 months", "intermediate": "6-9 months", "advanced": "Ready now"},
    },
    "backend_developer": {
        "title": "Backend Developer",
        "required_skills": ["programming_basics", "databases", "backend_frameworks"],
        "helpful_skills": ["system_design", "docker", "cloud_services"],
        "keywords": ["backend", "api", "server", "microservices"],
        "market": MarketInsights(
            demandTrend="stable",
            salaryRange="8-20 LPA",
            topCompanies=["Product companies", "Startups", "Service companies"],
        ),
        "time_to_ready": {"beginner": "8-12 months", "intermediate": "3-6 months", "advanced": "Ready now"},
    },
    "frontend_developer": {
        "title": "Frontend Developer",
        "required_skills": ["html_css", "javascript", "react"],
        "helpful_skills": ["typescript", "frontend_frameworks"],
        "keywords": ["frontend", "react", "ui", "ux", "web"],
        "market": MarketInsights(
            demandTrend="stable",
            salaryRange="6-18 LPA",
            topCompanies=["Product companies", "Startups", "Agencies"],
        ),
        "time_to_ready": {"beginner": "6-10 months", "intermediate": "2-4 months", "advanced": "Ready now"},
    },
    "fullstack_developer": {
        "title": "Full Stack Developer",
        "required_skills": ["html_css", "javascript", "backend_frameworks", "databases"],
        "helpful_skills": ["react", "docker", "cloud_services"],
        "keywords": ["fullstack", "full stack", "web development"],
        "market": MarketInsights(
            demandTrend="increasing",
            salaryRange="8-22 LPA",
            topCompanies=["Startups", "Product companies"],
        ),
        "time_to_ready": {"beginner": "12-18 months", "intermediate": "6-9 months", "advanced": "Ready now"},
    },
    "devops_engineer": {
        "title": "DevOps Engineer",
        "required_skills": ["linux", "docker", "cloud_services", "git"],
        "helpful_skills": ["kubernetes", "networking", "devops"],
        "keywords": ["devops", "cloud", "infrastructure", "ci/cd", "aws", "gcp"],
        "market": MarketInsights(
            demandTrend="increasing",
            salaryRange="10-28 LPA",
            topCompanies=["Cloud companies", "Large enterprises", "Startups"],
        ),
        "time_to_ready": {"beginner": "12-15 months", "intermediate": "6-9 months", "advanced": "Ready now"},
    },
    "product_manager": {
        "title": "Product Manager",
        "required_skills": ["product_thinking", "user_research", "analytics"],
        "helpful_skills": ["programming_basics", "sql", "data_analysis"],
        "keywords": ["product", "pm", "product manager", "roadmap", "strategy", "user experience"],
        "market": MarketInsights(
            demandTrend="stable",
            salaryRange="15-40 LPA",
            topCompanies=["Google", "Amazon", "Flipkart", "Startups"],
        ),
        "time_to_ready": {"beginner": "12-18 months", "intermediate": "6-9 months", "advanced": "Ready now"},
    },
    "technical_marketer": {
        "title": "Technical Marketer",
        "required_skills": ["marketing_fundamentals", "analytics", "content_creation"],
        "helpful_skills": ["seo", "programming_basics", "data_analysis"],
        "keywords": ["marketing", "technical marketing", "growth", "seo", "content", "digital marketing"],
        "market": MarketInsights(
            demandTrend="increasing",
            salaryRange="8-25 LPA",
            topCompanies=["Tech startups", "SaaS companies", "Agencies"],
        ),
        "time_to_ready": {"beginner": "6-12 months", "intermediate": "3-6 months", "advanced": "Ready now"},
    },
    "growth_hacker": {
        "title": "Growth Hacker",
        "required_skills": ["analytics", "marketing_fundamentals", "experimentation"],
        "helpful_skills": ["programming_basics", "sql", "data_analysis"],
        "keywords": ["growth", "growth hacking", "acquisition", "retention", "viral", "funnel"],
        "market": MarketInsights(
            demandTrend="increasing",
            salaryRange="10-30 LPA",
            topCompanies=["Startups", "Scale-ups", "Consumer tech"],
        ),
        "time_to_ready": {"beginner": "8-12 months", "intermediate": "4-6 months", "advanced": "Ready now"},
    },
    "technical_writer": {
        "title": "Technical Writer",
        "required_skills": ["technical_writing", "documentation", "content_creation"],
        "helpful_skills": ["programming_basics", "git", "developer_experience"],
        "keywords": ["technical writing", "documentation", "docs", "writer", "content"],
        "market": MarketInsights(
            demandTrend="stable",
            salaryRange="6-18 LPA",
            topCompanies=["Developer tools", "Enterprise software", "Open source"],
        ),
        "time_to_ready": {"beginner": "6-10 months", "intermediate": "3-5 months", "advanced": "Ready now"},
    },
    "ux_designer": {
        "title": "UX Designer",
        "required_skills": ["ux_design", "user_research", "prototyping"],
        "helpful_skills": ["html_css", "figma", "analytics"],
        "keywords": ["ux", "user experience", "design", "ui", "interface", "figma", "prototype"],
        "market": MarketInsights(
            demandTrend="stable",
            salaryRange="8-25 LPA",
            topCompanies=["Product companies", "Design agencies", "Startups"],
        ),
        "time_to_ready": {"beginner": "8-12 months", "intermediate": "4-6 months", "advanced": "Ready now"},
    },
}


def calculate_match_score(
    role_key: str,
    completed_skills: list[str],
    in_progress_skills: list[str],
) -> int:
    """Calculate match score (0-100) for a role."""
    role = CAREER_ROLES[role_key]
    required = role["required_skills"]
    helpful = role["helpful_skills"]
    
    # Required skills contribute 70% of score
    required_score = 0
    for skill in required:
        if skill in completed_skills:
            required_score += 70 / len(required)
        elif skill in in_progress_skills:
            required_score += 35 / len(required)  # Half credit for in-progress
    
    # Helpful skills contribute 30% of score
    helpful_score = 0
    for skill in helpful:
        if skill in completed_skills:
            helpful_score += 30 / len(helpful)
        elif skill in in_progress_skills:
            helpful_score += 15 / len(helpful)
    
    return int(required_score + helpful_score)


def match_interests_to_roles(interests: list[str], goals: list[str]) -> list[str]:
    """Find roles that match user interests and goals."""
    all_keywords = [w.lower() for w in interests + goals]
    text = " ".join(all_keywords)
    
    matches = []
    for role_key, role in CAREER_ROLES.items():
        if any(kw in text for kw in role["keywords"]):
            matches.append(role_key)
    
    return matches if matches else ["backend_developer", "fullstack_developer"]  # Default


class CareerRecommendationAgent:
    """
    Determines career direction based on profile and skills.
    
    Uses Gemini 2.5 Flash to infer career paths, falling back to static rules.
    """
    
    def __init__(self):
        self.model = None
        api_key = os.getenv("GOOGLE_API_KEY")
        
        if api_key:
            genai.configure(api_key=api_key)
            try:
                self.model = genai.GenerativeModel(
                    model_name="gemini-2.5-flash",
                    generation_config={
                        "temperature": 0.3,
                        "response_mime_type": "application/json"
                    },
                    system_instruction="""You are a Career Guidance Expert.
Analyze user profiles and suggest the best 3 technical career roles.
Output strictly in JSON format matching the schema provided."""
                )
                print("✨ CareerAgent: LLM Enabled (Gemini 2.5 Flash)")
            except Exception as e:
                print(f"⚠️ CareerAgent: Model init failed: {e}")
                self.model = None
        else:
            print("⚠️ CareerAgent: No API Key - using rule-based fallback")
    
    async def recommend(
        self,
        profile: ProfileAnalysis,
        skill_analysis: SkillAnalysis,
        user_interests: list[str] | None = None,
        user_goals: list[str] | None = None,
    ) -> CareerAnalysis:
        """Generate career recommendations."""
        
        # Try LLM first
        if self.model:
            try:
                # We can't await synchronous genai calls, but usually they are fast enough for simple tasks
                # or we run them in executor. For now, since api is async, let's just call it.
                # However, to be safe and avoid blocking event loop, we should use run_in_executor if possible,
                # but standard practice for this quick prototype is direct call.
                return self._recommend_with_llm(
                    profile, skill_analysis, user_interests, user_goals
                )
            except Exception as e:
                print(f"⚠️ CareerAgent LLM Failure: {e.__class__.__name__}: {e}")
                print("🔄 Falling back to rule-based logic...")
        
        return self._recommend_fallback(
            profile, skill_analysis, user_interests, user_goals
        )

    def _recommend_with_llm(
        self,
        profile: ProfileAnalysis,
        skill_analysis: SkillAnalysis,
        user_interests: list[str] | None,
        user_goals: list[str] | None,
    ) -> CareerAnalysis:
        """Construct prompt and parse LLM response."""
        
        interests = user_interests or profile.preferences.goals
        goals = user_goals or []
        
        prompt = f"""
USER PROFILE:
- Name: {profile.name}
- Stage: {profile.background.education}
- Exp Level: {profile.level.value}

SKILLS:
- Completed: {', '.join(skill_analysis.skillsCompleted)}
- In Progress: {', '.join(skill_analysis.skillsInProgress)}

INTERESTS: {', '.join(interests)}
GOALS: {', '.join(goals)}

TASK:
Suggest 1 Primary Career Role and 3 Alternative Roles based on this profile.
For the Primary Role, provide market insights (salary in Lakhs Per Annum - LPA for India market, trend, companies).

Output strictly valid JSON with this structure:
{{
  "primary": {{ 
    "role": "string (Job Title)", 
    "score": int (0-100 match), 
    "reason": "string (Why this fits)", 
    "timeToReady": "string (e.g. '6-9 months')" 
  }},
  "market": {{ 
    "demandTrend": "increasing" | "stable" | "decreasing", 
    "salaryRange": "string (e.g. '12-25 LPA')", 
    "topCompanies": ["string", "string"] 
  }},
  "alternatives": [
    {{ "role": "string", "score": int, "reason": "string" }}
  ]
}}
"""
        response = self.model.generate_content(prompt)
        data = json.loads(response.text)
        
        # Map to Pydantic models
        primary_data = data["primary"]
        market_data = data["market"]
        
        primary_match = CareerMatch(
            role=primary_data["role"],
            matchScore=primary_data["score"],
            reason=primary_data["reason"],
            timeToReady=primary_data["timeToReady"]
        )
        
        alternatives = [
            CareerMatch(
                role=alt["role"],
                matchScore=alt["score"],
                reason=alt["reason"],
                timeToReady="N/A" # Default
            ) for alt in data.get("alternatives", [])
        ]
        
        market_insights = MarketInsights(
            demandTrend=market_data["demandTrend"],
            salaryRange=market_data["salaryRange"],
            topCompanies=market_data["topCompanies"]
        )
        
        return CareerAnalysis(
            primaryDirection=primary_match,
            alternativeDirections=alternatives,
            marketInsights=market_insights
        )

    def _recommend_fallback(
        self,
        profile: ProfileAnalysis,
        skill_analysis: SkillAnalysis,
        user_interests: list[str] | None = None,
        user_goals: list[str] | None = None,
    ) -> CareerAnalysis:
        """Legacy rule-based recommendation logic."""
        completed = skill_analysis.skillsCompleted
        in_progress = skill_analysis.skillsInProgress
        
        interests = user_interests or []
        goals = user_goals or []
        
        if not interests:
            interests = profile.preferences.goals
        
        # Find matching roles based on user preferences
        matched_roles = match_interests_to_roles(interests, goals)
        
        # Calculate scores
        scored_roles = []
        for role_key in matched_roles:
            score = calculate_match_score(role_key, completed, in_progress)
            score = min(100, score + 20)
            scored_roles.append((role_key, score))
        
        # Also score other roles for alternatives
        for role_key in CAREER_ROLES:
            if role_key not in matched_roles:
                score = calculate_match_score(role_key, completed, in_progress)
                if score >= 30:
                    scored_roles.append((role_key, score))
        
        scored_roles.sort(key=lambda x: x[1], reverse=True)
        
        if not scored_roles:
            scored_roles = [("backend_developer", 40)]
        
        # Primary role
        primary_key = scored_roles[0][0]
        primary_role = CAREER_ROLES[primary_key]
        level_key = profile.level.value
        
        primary = CareerMatch(
            role=primary_role["title"],
            matchScore=scored_roles[0][1],
            reason=f"Based on your interest in {', '.join(interests[:2]) if interests else profile.role}",
            timeToReady=primary_role["time_to_ready"].get(level_key, "12 months"),
        )
        
        # Alternative roles (max 3)
        alternatives = []
        for role_key, score in scored_roles[1:4]:
            role = CAREER_ROLES[role_key]
            alternatives.append(CareerMatch(
                role=role["title"],
                matchScore=score,
                reason=f"Matches your interest in related areas",
            ))
        
        return CareerAnalysis(
            primaryDirection=primary,
            alternativeDirections=alternatives,
            marketInsights=primary_role["market"],
        )
