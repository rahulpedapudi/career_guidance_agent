"""
Career Recommendation Agent — Directional Hypotheses.

Produces rich career analysis with primaryRole, matchScore, alternatives.
"""

from career_agent.models import (
    ProfileAnalysis,
    SkillAnalysis,
    CareerAnalysis,
    CareerMatch,
    MarketInsights,
    Level,
)


# Career role definitions with requirements and market insights
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
    
    Produces:
    - Primary career direction with match score
    - Alternative directions
    - Market insights
    """
    
    def recommend(
        self,
        profile: ProfileAnalysis,
        skill_analysis: SkillAnalysis,
        user_interests: list[str] | None = None,
        user_goals: list[str] | None = None,
    ) -> CareerAnalysis:
        """Generate career recommendations.
        
        Args:
            profile: Analyzed profile from ProfileAgent
            skill_analysis: Skill analysis from SkillAgent
            user_interests: Raw interests from user input (e.g., ["AI/ML", "Backend"])
            user_goals: Raw goals from user input (e.g., ["Get job at FAANG"])
        """
        completed = skill_analysis.skillsCompleted
        in_progress = skill_analysis.skillsInProgress
        
        # Prioritize explicit user interests over inferred ones
        interests = user_interests or []
        goals = user_goals or []
        
        # Fallback to profile preferences if no explicit interests
        if not interests:
            interests = profile.preferences.goals
        
        # Combine everything for matching
        all_inputs = interests + goals + [profile.role]
        
        # Find matching roles based on user preferences
        matched_roles = match_interests_to_roles(interests, goals)
        
        # Calculate scores for all matched roles (user preferences get priority)
        scored_roles = []
        for role_key in matched_roles:
            score = calculate_match_score(role_key, completed, in_progress)
            # Boost score for explicitly matched interests
            score = min(100, score + 20)
            scored_roles.append((role_key, score))
        
        # Also score other roles for alternatives
        for role_key in CAREER_ROLES:
            if role_key not in matched_roles:
                score = calculate_match_score(role_key, completed, in_progress)
                if score >= 30:  # Only include if reasonable fit
                    scored_roles.append((role_key, score))
        
        # Sort by score
        scored_roles.sort(key=lambda x: x[1], reverse=True)
        
        if not scored_roles:
            # Default fallback
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
        
        # Alternative roles
        alternatives = []
        for role_key, score in scored_roles[1:4]:  # Up to 3 alternatives
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

