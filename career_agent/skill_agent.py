"""
Skill Agent — Structural Gap Analyzer (Rule-Based).

Produces rich skill analysis with completed/inProgress/planned/gaps.
"""

from career_agent.models import (
    SkillSnapshot,
    SkillEntry,
    SkillLevel,
    SkillAnalysis,
    SkillGap,
    EmergingSkill,
    Impact,
)
from career_agent.skill_graph import (
    get_all_prerequisites,
    get_skill_description,
    SKILL_DEPENDENCIES,
)


def categorize_skills(snapshot: SkillSnapshot) -> tuple[list[str], list[str], list[str]]:
    """Categorize skills into completed, in-progress, and planned."""
    completed = []
    in_progress = []
    planned = []
    
    for entry in snapshot.skills:
        if entry.level == SkillLevel.COMFORTABLE:
            completed.append(entry.skill)
        elif entry.level == SkillLevel.USED_A_BIT:
            in_progress.append(entry.skill)
        elif entry.level == SkillLevel.AWARE:
            planned.append(entry.skill)
    
    return completed, in_progress, planned


def find_skill_gaps(
    snapshot: SkillSnapshot,
    target_direction: str | None = None,
) -> list[SkillGap]:
    """Find skills that are blocking progress."""
    comfortable = {e.skill for e in snapshot.skills if e.level == SkillLevel.COMFORTABLE}
    learning = {e.skill for e in snapshot.skills if e.level in (SkillLevel.AWARE, SkillLevel.USED_A_BIT)}
    
    gaps = []
    
    # Get target skills based on direction
    target_skills = _direction_to_skills(target_direction) or list(learning)
    
    # Find missing prerequisites for target skills
    for target in target_skills:
        prereqs = get_all_prerequisites(target)
        for prereq in prereqs:
            if prereq not in comfortable:
                # Determine impact
                blocked = [s for s in target_skills if prereq in get_all_prerequisites(s)]
                impact = Impact.HIGH if len(blocked) >= 2 else Impact.MEDIUM
                
                # Avoid duplicates
                if not any(g.skill == prereq for g in gaps):
                    gaps.append(SkillGap(
                        skill=prereq,
                        impact=impact,
                        reason=get_skill_description(prereq),
                        blockedSkills=blocked[:3],  # Limit to 3
                    ))
    
    # Sort by impact
    gaps.sort(key=lambda g: (0 if g.impact == Impact.HIGH else 1 if g.impact == Impact.MEDIUM else 2))
    
    return gaps[:5]  # Return top 5 gaps


def identify_strengths(snapshot: SkillSnapshot) -> list[str]:
    """Identify user's strong skills."""
    return [
        entry.skill.replace("_", " ").title()
        for entry in snapshot.skills
        if entry.level == SkillLevel.COMFORTABLE
    ]


def get_emerging_skills(direction: str | None) -> list[EmergingSkill]:
    """Get emerging skills relevant to the direction."""
    emerging = []
    
    # Common emerging skills
    if direction and ("ml" in direction.lower() or "ai" in direction.lower() or "data" in direction.lower()):
        emerging.append(EmergingSkill(
            skill="Prompt Engineering",
            relevance="2-3 years",
            reason="LLM adoption increasing across industries",
        ))
        emerging.append(EmergingSkill(
            skill="MLOps",
            relevance="Now",
            reason="ML deployment becoming standardized",
        ))
    else:
        emerging.append(EmergingSkill(
            skill="AI-Assisted Development",
            relevance="Now",
            reason="AI coding tools becoming standard",
        ))
    
    return emerging


def _direction_to_skills(direction: str | None) -> list[str] | None:
    """Map career direction to relevant target skills."""
    if direction is None:
        return None
    
    direction_lower = direction.lower()
    
    mappings = {
        "backend": ["backend_frameworks", "databases", "system_design"],
        "frontend": ["frontend_frameworks", "react", "typescript"],
        "fullstack": ["frontend_frameworks", "backend_frameworks", "databases"],
        "data": ["data_analysis", "machine_learning", "sql"],
        "ml": ["machine_learning", "deep_learning", "python"],
        "machine learning": ["machine_learning", "deep_learning", "python", "statistics"],
        "devops": ["devops", "docker", "kubernetes", "cloud_services"],
        "software": ["algorithms", "system_design", "databases"],
    }
    
    for key, skills in mappings.items():
        if key in direction_lower:
            return skills
    
    return None


class SkillAgent:
    """
    Analyzes skill gaps using dependency graph.
    
    Produces:
    - Skills categorized as completed/inProgress/planned
    - Skill gaps with impact and blocked skills
    - User's strengths
    - Emerging skills to watch
    """
    
    def analyze(
        self,
        snapshot: SkillSnapshot,
        target_direction: str | None = None,
    ) -> SkillAnalysis:
        """Analyze skill snapshot and produce rich output."""
        completed, in_progress, planned = categorize_skills(snapshot)
        gaps = find_skill_gaps(snapshot, target_direction)
        strengths = identify_strengths(snapshot)
        emerging = get_emerging_skills(target_direction)
        
        return SkillAnalysis(
            skillsCompleted=completed,
            skillsInProgress=in_progress,
            skillsPlanned=planned,
            gaps=gaps,
            strengths=strengths,
            emergingSkills=emerging,
        )
