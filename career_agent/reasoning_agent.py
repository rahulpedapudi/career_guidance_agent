"""
Reasoning Agent — Final Synthesizer.

Produces the complete HorizonOutput for frontend consumption.
"""

from datetime import datetime

from career_agent.models import (
    ProfileAnalysis,
    SkillAnalysis,
    CareerAnalysis,
    HorizonOutput,
    ProfileSection,
    CareerDirection,
    ImmediateFocus,
    SkillsSnapshot,
    SkillGapOutput,
    ActiveInterest,
    NextAction,
    Insight,
    Roadmap,
    RoadmapPhase,
    RoadmapSkill,
    SkillResource,
    Confidence,
    Priority,
    PhaseStatus,
    InsightType,
    Impact,
    Stats,
    DailyInsight,
    ActivityItem,
)


def build_profile_section(profile: ProfileAnalysis) -> ProfileSection:
    """Convert ProfileAnalysis to frontend ProfileSection."""
    return ProfileSection(
        name=profile.name,
        role=profile.role,
        level=profile.level.value.capitalize(),
        nextLevel=profile.nextLevel.value.capitalize() if profile.nextLevel else None,
        progressToNextLevel=profile.progressToNextLevel,
        exposureLevel=profile.exposureLevel,
        learningStyle=profile.learningStyle,
    )


def build_career_direction(career: CareerAnalysis) -> CareerDirection:
    """Convert CareerAnalysis to frontend CareerDirection."""
    primary = career.primaryDirection
    
    # Determine confidence based on match score
    if primary.matchScore >= 70:
        confidence = Confidence.HIGH
    elif primary.matchScore >= 50:
        confidence = Confidence.MODERATE
    else:
        confidence = Confidence.LOW
    
    secondary_roles = [alt.role for alt in career.alternativeDirections[:2]]
    
    return CareerDirection(
        primaryRole=primary.role,
        secondaryRoles=secondary_roles,
        matchScore=primary.matchScore,
        confidence=confidence,
        reasoning=primary.reason or f"Based on your skills and interests, {primary.role} aligns with your trajectory.",
    )


def build_immediate_focus(skill_analysis: SkillAnalysis) -> ImmediateFocus:
    """Determine the most important skill to focus on now."""
    if skill_analysis.gaps:
        top_gap = skill_analysis.gaps[0]
        return ImmediateFocus(
            skill=top_gap.skill.replace("_", " ").title(),
            reason=top_gap.reason,
            timeWindow="Next 30 days",
            priority=Priority.HIGH if top_gap.impact == Impact.HIGH else Priority.MEDIUM,
        )
    
    # If no gaps, focus on first in-progress skill
    if skill_analysis.skillsInProgress:
        return ImmediateFocus(
            skill=skill_analysis.skillsInProgress[0].replace("_", " ").title(),
            reason="Continue building proficiency",
            timeWindow="Next 30 days",
            priority=Priority.MEDIUM,
        )
    
    # Default
    return ImmediateFocus(
        skill="Programming Fundamentals",
        reason="Foundation for all technical paths",
        timeWindow="Next 30 days",
        priority=Priority.HIGH,
    )


def build_skills_snapshot(skill_analysis: SkillAnalysis) -> SkillsSnapshot:
    """Convert SkillAnalysis to frontend SkillsSnapshot."""
    gaps = [
        SkillGapOutput(
            skill=g.skill.replace("_", " ").title(),
            impact=g.impact.value,
            reason=g.reason,
        )
        for g in skill_analysis.gaps[:4]
    ]
    
    return SkillsSnapshot(
        completed=[s.replace("_", " ").title() for s in skill_analysis.skillsCompleted],
        inProgress=[s.replace("_", " ").title() for s in skill_analysis.skillsInProgress],
        planned=[s.replace("_", " ").title() for s in skill_analysis.skillsPlanned],
        gaps=gaps,
    )


def _role_to_interest(role: str) -> str:
    """Map role to interest area."""
    if "ml" in role.lower() or "machine learning" in role.lower():
        return "AI & Machine Learning"
    if "data" in role.lower():
        return "Data Science"
    if "backend" in role.lower():
        return "Backend Development"
    if "frontend" in role.lower():
        return "Frontend Development"
    if "full" in role.lower():
        return "Full Stack Development"
    if "devops" in role.lower():
        return "Cloud & DevOps"
    if any(k in role.lower() for k in ["blockchain", "smart contract", "dapp", "web3", "crypto"]):
        return "Blockchain & Web3"
    return "Software Development"


def _get_interest_color(role: str) -> str:
    """Get gradient color for interest."""
    if "ml" in role.lower() or "machine learning" in role.lower():
        return "from-emerald-500 to-teal-500"
    if "data" in role.lower():
        return "from-purple-500 to-pink-500"
    if "backend" in role.lower():
        return "from-blue-500 to-cyan-500"
    if "frontend" in role.lower():
        return "from-orange-500 to-amber-500"
    if "devops" in role.lower():
        return "from-red-500 to-rose-500"
    return "from-indigo-500 to-violet-500"


def _get_interest_icon(role: str) -> str:
    """Get icon identifier for interest."""
    return "star"  # Default icon for now as per screenshot


def build_active_interests(career: CareerAnalysis, roadmap: Roadmap | None = None) -> list[ActiveInterest]:
    """Generate active interests based on career direction."""
    interests = []
    
    # Primary interest
    primary = career.primaryDirection
    
    # Calculate modules remaining for primary from roadmap
    primary_modules = 6
    if roadmap:
        primary_modules = sum(
            1 for phase in roadmap.phases 
            for skill in phase.skills 
            if skill.status != "completed"
        )
        # If granular roadmap not available, fallback to phase count or 4
        if primary_modules == 0 and roadmap.overallProgress < 100:
            primary_modules = 4

    interests.append(ActiveInterest(
        id=primary.role.lower().replace(" ", "-"),
        title=_role_to_interest(primary.role),
        progress=primary.matchScore,
        status="Active",
        color=_get_interest_color(primary.role),
        modulesRemaining=primary_modules,
        icon=_get_interest_icon(primary.role),
    ))
    
    # Secondary interests from alternatives
    for alt in career.alternativeDirections[:2]:
        interests.append(ActiveInterest(
            id=alt.role.lower().replace(" ", "-"),
            title=_role_to_interest(alt.role),

            progress=0,
            status="Planned",
            color=_get_interest_color(alt.role),
            modulesRemaining=4,  # Placeholder for alternates
            icon=_get_interest_icon(alt.role),
        ))
    
    return interests


def build_next_action(
    immediate_focus: ImmediateFocus,
    skill_analysis: SkillAnalysis,
) -> NextAction:
    """Generate the next recommended action."""
    skill = immediate_focus.skill.lower()
    
    # Map skills to resources
    resources = {
        "linear algebra": ("Complete Linear Algebra Basics", "Khan Academy - Vectors & Matrices", "2 hours"),
        "statistics": ("Learn Statistics Fundamentals", "Khan Academy - Statistics", "2 hours"),
        "python": ("Python Practice", "LeetCode Easy Problems", "1 hour"),
        "data structures": ("Data Structures Deep Dive", "NeetCode - Arrays & Hashing", "2 hours"),
        "algorithms": ("Algorithm Practice", "LeetCode - Top Interview Questions", "2 hours"),
        "machine learning": ("ML Fundamentals", "Andrew Ng's ML Course - Week 1", "3 hours"),
        "databases": ("SQL Practice", "SQLZoo - Basic Queries", "1 hour"),
        "git": ("Git Essentials", "Learn Git Branching", "1 hour"),
    }
    
    for key, (title, subtitle, duration) in resources.items():
        if key in skill:
            return NextAction(
                title=title,
                subtitle=subtitle,
                duration=duration,
                type="learning",
                actionUrl=None,
            )
    
    # Default
    return NextAction(
        title=f"Learn {immediate_focus.skill}",
        subtitle="Find a tutorial or course",
        duration="1-2 hours",
        type="learning",
        actionUrl=None,
    )


def build_insights(
    profile: ProfileAnalysis,
    skill_analysis: SkillAnalysis,
    career: CareerAnalysis,
) -> list[Insight]:
    """Generate personalized insights."""
    insights = []
    
    # Opportunity insight
    if skill_analysis.skillsCompleted:
        strengths = ", ".join(skill_analysis.skillsCompleted[:2])
        insights.append(Insight(
            type=InsightType.OPPORTUNITY,
            message=f"Your {strengths} skills position you well for {career.primaryDirection.role}. Focus on filling gaps next.",
            confidence=Confidence.HIGH,
        ))
    
    # Risk insight
    if skill_analysis.gaps:
        top_gap = skill_analysis.gaps[0]
        blocked = ", ".join(top_gap.blockedSkills[:2]) if top_gap.blockedSkills else "advanced topics"
        insights.append(Insight(
            type=InsightType.RISK,
            message=f"Skipping {top_gap.skill.replace('_', ' ').title()} will create gaps in {blocked}.",
            confidence=Confidence.HIGH,
        ))
    
    # Trend insight
    if skill_analysis.emergingSkills:
        emerging = skill_analysis.emergingSkills[0]
        insights.append(Insight(
            type=InsightType.TREND,
            message=f"{emerging.skill} is emerging fast. {emerging.reason}",
            confidence=Confidence.MODERATE,
        ))
    
    return insights[:3]


def build_roadmap(
    career: CareerAnalysis,
    skill_analysis: SkillAnalysis,
    profile: ProfileAnalysis,
) -> Roadmap:
    """Generate a learning roadmap for the primary career direction."""
    return build_roadmap_for_role(career.primaryDirection.role, skill_analysis)


def build_roadmap_for_role(role: str, skill_analysis: SkillAnalysis) -> Roadmap:
    """Generate a learning roadmap for a specific role."""
    # Define phases based on role
    phases = _get_roadmap_phases(role, skill_analysis)
    
    # Calculate current phase and progress
    current_phase = 1
    for i, phase in enumerate(phases):
        if phase.status == PhaseStatus.IN_PROGRESS:
            current_phase = i + 1
            break
        if phase.status == PhaseStatus.COMPLETED:
            current_phase = i + 2
    
    # Calculate overall progress
    total_progress = sum(p.progress for p in phases)
    overall_progress = total_progress // len(phases) if phases else 0
    
    return Roadmap(
        id=role.lower().replace(" ", "-") + "-path",
        title=role,
        totalPhases=len(phases),
        currentPhase=min(current_phase, len(phases)),
        overallProgress=overall_progress,
        phases=phases,
    )


def _get_roadmap_phases(role: str, skill_analysis: SkillAnalysis) -> list[RoadmapPhase]:
    """Generate roadmap phases based on role."""
    from career_agent.skill_graph import (
        get_skill_description, 
        get_skill_resources, 
        get_skill_practice
    )
    
    completed = set(skill_analysis.skillsCompleted)
    in_progress = set(skill_analysis.skillsInProgress)
    
    # Common roadmap structure
    if "ml" in role.lower() or "machine learning" in role.lower():
        phases_def = [
            ("Programming Foundations", ["python", "programming_basics", "git"]),
            ("Math for ML", ["linear_algebra", "statistics"]),
            ("ML Fundamentals", ["machine_learning", "data_analysis"]),
            ("Deep Learning", ["deep_learning"]),
            ("ML Engineering", ["docker", "cloud_services"]),
            ("Specialization", ["mlops"]),
        ]
    elif "data" in role.lower():
        phases_def = [
            ("Programming Foundations", ["python", "programming_basics"]),
            ("Data Fundamentals", ["sql", "data_analysis", "statistics"]),
            ("Advanced Analytics", ["machine_learning"]),
            ("Visualization & Storytelling", ["data_visualization"]),
        ]
    elif "backend" in role.lower():
        phases_def = [
            ("Programming Foundations", ["programming_basics", "git"]),
            ("Backend Basics", ["databases", "sql", "backend_frameworks"]),
            ("Advanced Backend", ["system_design", "docker"]),
            ("Production Skills", ["cloud_services", "devops"]),
        ]
    elif "product" in role.lower() or "pm" in role.lower():
        phases_def = [
            ("Product Fundamentals", ["product_thinking", "user_research"]),
            ("Technical Literacy", ["programming_basics", "sql"]),
            ("Analytics & Metrics", ["analytics", "data_analysis"]),
            ("Strategy & Execution", ["roadmapping", "stakeholder_management"]),
        ]
    elif "marketing" in role.lower() or "growth" in role.lower():
        phases_def = [
            ("Marketing Fundamentals", ["marketing_fundamentals", "content_creation"]),
            ("Analytics & Data", ["analytics", "data_analysis"]),
            ("Growth Tactics", ["seo", "experimentation"]),
            ("Technical Skills", ["programming_basics", "sql"]),
        ]
    elif "ux" in role.lower() or "design" in role.lower():
        phases_def = [
            ("Design Fundamentals", ["ux_design", "prototyping"]),
            ("User Research", ["user_research", "analytics"]),
            ("Technical Skills", ["html_css", "figma"]),
            ("Advanced Design", ["design_systems", "accessibility"]),
        ]
    elif "writer" in role.lower() or "documentation" in role.lower():
        phases_def = [
            ("Writing Fundamentals", ["technical_writing", "content_creation"]),
            ("Technical Literacy", ["programming_basics", "git"]),
            ("Documentation Tools", ["documentation", "developer_experience"]),
            ("Advanced Topics", ["api_documentation", "style_guides"]),
        ]
    elif "frontend" in role.lower():
        phases_def = [
            ("Web Fundamentals", ["html_css", "javascript"]),
            ("React & Frameworks", ["react", "typescript"]),
            ("Advanced Frontend", ["frontend_frameworks", "performance"]),
            ("Production Skills", ["git", "testing"]),
        ]
    elif "devops" in role.lower():
        phases_def = [
            ("Linux & CLI", ["linux", "git"]),
            ("Containers", ["docker", "kubernetes"]),
            ("Cloud Infrastructure", ["cloud_services", "networking"]),
            ("CI/CD & Automation", ["devops", "monitoring"]),
        ]
    else:
        phases_def = [
            ("Programming Foundations", ["programming_basics", "git"]),
            ("Core Skills", ["data_structures", "algorithms"]),
            ("Specialization", ["databases", "system_design"]),
            ("Production Ready", ["docker", "cloud_services"]),
        ]
    
    phases = []
    weeks_elapsed = 0
    
    for i, (title, skills) in enumerate(phases_def):
        phase_skills = []
        completed_count = 0
        
        # Calculate time range for phase (2 weeks per skill average)
        weeks_for_phase = len(skills) * 2
        time_range = f"Weeks {weeks_elapsed + 1}-{weeks_elapsed + weeks_for_phase}"
        weeks_elapsed += weeks_for_phase
        
        for skill in skills:
            if skill in completed:
                status = "completed"
                completed_count += 1
            elif skill in in_progress:
                status = "in-progress"
            else:
                status = "not-started"
            
            # Get skill details from skill_graph
            description = get_skill_description(skill)
            raw_resources = get_skill_resources(skill)
            practice = get_skill_practice(skill)
            
            # Convert to SkillResource objects
            resources = [
                SkillResource(
                    type=r.get("type", "course"),
                    title=r.get("title", ""),
                    link=r.get("link"),
                    level=r.get("level", "Beginner"),
                )
                for r in raw_resources
            ]
            
            phase_skills.append(RoadmapSkill(
                id=skill,
                name=skill.replace("_", " ").title(),
                status=status,
                description=description,
                resources=resources,
                practice=practice,
            ))
        
        # Determine phase status and progress
        if completed_count == len(skills):
            phase_status = PhaseStatus.COMPLETED
            progress = 100
        elif completed_count > 0 or any(s in in_progress for s in skills):
            phase_status = PhaseStatus.IN_PROGRESS
            progress = int((completed_count / len(skills)) * 100)
        else:
            phase_status = PhaseStatus.NOT_STARTED
            progress = 0
        
        phases.append(RoadmapPhase(
            id=f"phase-{i+1}",
            title=title,
            status=phase_status,
            progress=progress,
            timeRange=time_range,
            skills=phase_skills,
        ))
    
    return phases


def build_stats(
    skill_analysis: SkillAnalysis,
    active_interests: list[ActiveInterest],
    roadmap: Roadmap | None,
) -> Stats:
    """Calculate dashboard statistics."""
    skills_learned = len(skill_analysis.skillsCompleted)
    
    # Estimate learning hours (15h per completed, 5h per in-progress)
    learning_hours = (len(skill_analysis.skillsCompleted) * 15) + (len(skill_analysis.skillsInProgress) * 5)
    if learning_hours == 0:
        learning_hours = 2  # Baseline for onboarding
    
    roadmap_completion = roadmap.overallProgress if roadmap else 0
        
    return Stats(
        skillsLearned=skills_learned,
        learningHours=learning_hours,
        roadmapCompletion=roadmap_completion,
        domainsExplored=len(active_interests),
    )


def get_daily_insight() -> DailyInsight:
    """Get a daily motivational quote."""
    return DailyInsight(
        message="Consistency is the only algorithm that matters.",
        type="motivation",
    )


def get_recent_activity(skill_analysis: SkillAnalysis) -> list[ActivityItem]:
    """Generate recent activity items."""
    activity = []
    
    if skill_analysis.skillsCompleted:
        activity.append(ActivityItem(
            id="act_1",
            title=f"Completed {skill_analysis.skillsCompleted[0].replace('_', ' ').title()}",
            time="2 hours ago",
            xp=50,
        ))
    
    if skill_analysis.skillsInProgress:
        activity.append(ActivityItem(
            id="act_2",
            title=f"Started {skill_analysis.skillsInProgress[0].replace('_', ' ').title()}",
            time="Yesterday",
            xp=0,
        ))
        
    if not activity:
        activity.append(ActivityItem(
            id="act_init",
            title="Joined FutureHub",
            time="Just now",
            xp=10,
        ))
        
    return activity


class ReasoningAgent:
    """
    Final synthesizer producing complete HorizonOutput.
    
    Combines all agent outputs into the frontend-expected format.
    """
    
    def synthesize(
        self,
        user_id: str,
        profile: ProfileAnalysis,
        skill_analysis: SkillAnalysis,
        career: CareerAnalysis,
    ) -> HorizonOutput:
        """Synthesize all agent outputs into HorizonOutput."""
        profile_section = build_profile_section(profile)
        career_direction = build_career_direction(career)
        immediate_focus = build_immediate_focus(skill_analysis)
        skills_snapshot = build_skills_snapshot(skill_analysis)
        next_action = build_next_action(immediate_focus, skill_analysis)
        insights = build_insights(profile, skill_analysis, career)
        
        # Build roadmaps for ALL career directions (primary + alternatives)
        roadmaps = []
        all_directions = [career.primaryDirection] + career.alternativeDirections[:2]
        
        for direction in all_directions:
            roadmap = build_roadmap_for_role(direction.role, skill_analysis)
            roadmaps.append(roadmap)
        
        # Primary roadmap is first one (for stats calculation)
        primary_roadmap = roadmaps[0] if roadmaps else None
        
        active_interests = build_active_interests(career, primary_roadmap)
        stats = build_stats(skill_analysis, active_interests, primary_roadmap)
        
        daily_insight = get_daily_insight()
        recent_activity = get_recent_activity(skill_analysis)
        
        return HorizonOutput(
            version="1.1",
            generatedAt=datetime.utcnow().isoformat() + "Z",
            userId=user_id,
            profile=profile_section,
            stats=stats,
            dailyInsight=daily_insight,
            careerDirection=career_direction,
            immediateFocus=immediate_focus,
            skillsSnapshot=skills_snapshot,
            activeInterests=active_interests,
            nextAction=next_action,
            recentActivity=recent_activity,
            insights=insights,
            roadmaps=roadmaps,
        )
