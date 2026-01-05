# Career Guidance Agent — Technical Documentation

## Overview

A **multi-agent career reasoning system** that produces actionable career guidance for students and early-career professionals. The system uses a centralized reasoning architecture with specialized agents coordinated by a supervisor.

### Core Principles

1. **Single source of truth** — All reasoning outputs are stored; chat history is not state
2. **Deterministic orchestration** — Agent execution order is fixed by the Supervisor
3. **Structured I/O only** — Agents exchange JSON-compatible Pydantic objects
4. **Separation of concerns** — Each agent owns exactly one responsibility

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Action                             │
│              (onboarding, skill update, check-in)               │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Event (normalized)                         │
│         { event_type, payload }                                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SUPERVISOR AGENT                            │
│                   (Pure Logic, No LLM)                          │
│                                                                 │
│   Input:  Event                                                 │
│   Output: ExecutionPlan { run_profile, run_skill, run_career,   │
│                           run_reasoning }                       │
└─────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
                ▼               ▼               ▼
┌───────────────────┐ ┌─────────────────┐ ┌─────────────────────┐
│   PROFILE AGENT   │ │   SKILL AGENT   │ │  CAREER REC AGENT   │
│   (Rule-Based)    │ │  (Graph-Based)  │ │   (LLM-Assisted)    │
│                   │ │                 │ │                     │
│ → Stage bucket    │ │ → Blocking gaps │ │ → Direction         │
│ → Risk factors    │ │ → Helpful gaps  │ │ → Leaning           │
│ → Strength biases │ │                 │ │ → Confidence        │
│ → Time pressure   │ │                 │ │                     │
└───────────────────┘ └─────────────────┘ └─────────────────────┘
                │               │               │
                └───────────────┼───────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     REASONING AGENT                             │
│                 (LLM with Hard Constraints)                     │
│                                                                 │
│   Synthesizes all agent outputs into HorizonOutput              │
│   The ONLY agent allowed to "think"                             │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       HorizonOutput                             │
│                  (Frontend-Consumed JSON)                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Models

All models are defined in `career_agent/models.py`.

### Input Models

#### UserProfile

```python
{
    "user_id": "string",
    "stage": "first_year | second_year | third_year | final_year | graduate",
    "graduation_year": "number | null",
    "exposure_level": "coursework | small_projects | serious_projects | professional",
    "learning_preferences": ["string"],  # max 2
    "weekly_time_commitment": "<5 | 5-10 | 10-15 | 15+",
    "constraints": ["string"]
}
```

#### SkillSnapshot

```python
{
    "skills": [
        { "skill": "python", "level": "aware | used_a_bit | comfortable" }
    ]
}
```

#### Event

```python
{
    "event_type": "onboarding_completed | skill_updated | direction_changed | check_in",
    "payload": {}
}
```

### Agent Output Models

#### ExecutionPlan (Supervisor)

```python
{
    "run_profile": true,
    "run_skill": true,
    "run_career": false,
    "run_reasoning": true
}
```

#### ProfileAnalysis (Profile Agent)

```python
{
    "stage_bucket": "early | mid | late",
    "risk_factors": ["unfocused_exploration", "late_start", ...],
    "strength_biases": ["building_oriented", "theory_oriented", ...],
    "time_pressure": "low | moderate | high"
}
```

#### SkillGapAnalysis (Skill Agent)

```python
{
    "blocking": [{ "skill": "data_structures", "why": "Required for..." }],
    "helpful": [{ "skill": "git", "why": "Expected for..." }]
}
```

#### CareerRecommendation (Career Agent)

```python
{
    "suggested_direction": {
        "direction": "Software Development",
        "leaning": "Backend",
        "confidence": "moderate"
    }
}
```

### Final Output

#### HorizonOutput

```python
{
    "current_direction": { "direction": "...", "leaning": "...", "confidence": "..." },
    "focus_now": [
        { "title": "Learn X", "rationale": "Because Y" }
    ],
    "blocking_gaps": {
        "blocking": [...],
        "helpful": [...]
    }
}
```

---

## Agent Specifications

### 1. Supervisor Agent

**File:** `career_agent/supervisor.py`

| Property | Value               |
| -------- | ------------------- |
| Type     | Pure logic (no LLM) |
| Input    | `Event`             |
| Output   | `ExecutionPlan`     |

**Event Routing Rules:**

| Event                  | Profile | Skill | Career | Reasoning |
| ---------------------- | ------- | ----- | ------ | --------- |
| `onboarding_completed` | ✓       | ✓     | ✓      | ✓         |
| `skill_updated`        |         | ✓     |        | ✓         |
| `direction_changed`    |         |       | ✓      | ✓         |
| `check_in`             |         |       |        | ✓         |

---

### 2. Profile Agent

**File:** `career_agent/profile_agent.py`

| Property | Value               |
| -------- | ------------------- |
| Type     | Rule-based (no LLM) |
| Input    | `UserProfile`       |
| Output   | `ProfileAnalysis`   |

**Classification Logic:**

- **Stage Bucket:**

  - `early`: 1st/2nd year
  - `mid`: 3rd year
  - `late`: final year / graduate

- **Risk Factors:**

  - `late_start`: Final year with only coursework exposure
  - `unfocused_exploration`: No learning preferences set
  - `insufficient_commitment`: Low time commitment in late stage
  - `over_constrained`: More than 2 constraints

- **Strength Biases:**
  - `building_oriented`: Has project/professional experience
  - `theory_oriented`: Only coursework exposure
  - `visual_learner` / `documentation_oriented`: Based on preferences

---

### 3. Skill Agent

**Files:** `career_agent/skill_agent.py`, `career_agent/skill_graph.py`

| Property | Value                               |
| -------- | ----------------------------------- |
| Type     | Graph-based (no LLM)                |
| Input    | `SkillSnapshot`, optional direction |
| Output   | `SkillGapAnalysis`                  |

**Skill Dependency Graph:**

```
algorithms ← data_structures ← programming_basics
system_design ← algorithms, databases, networking
frontend_frameworks ← html_css, javascript
machine_learning ← python, statistics, linear_algebra
```

**Gap Classification:**

- **Blocking:** Prerequisites the user lacks for skills they're learning
- **Helpful:** Common foundational skills (git, linux) not yet mastered

---

### 4. Career Recommendation Agent

**File:** `career_agent/career_recommendation_agent.py`

| Property | Value                                                 |
| -------- | ----------------------------------------------------- |
| Type     | LLM-assisted (with fallback)                          |
| Input    | `ProfileAnalysis`, `SkillSnapshot`, curiosity signals |
| Output   | `CareerRecommendation`                                |

**Behavior:**

1. Builds context from profile and skills
2. Uses LLM to infer plausible direction
3. Falls back to rule-based heuristics if LLM unavailable

**Confidence Guidelines:**

- `high`: Strong signals + clear preferences + relevant skills
- `moderate`: Some signals but incomplete picture
- `low`: Limited information, exploratory only

---

### 5. Reasoning Agent

**File:** `career_agent/reasoning_agent.py`

| Property | Value                     |
| -------- | ------------------------- |
| Type     | LLM with hard constraints |
| Input    | All agent outputs         |
| Output   | `HorizonOutput`           |

**Responsibilities:**

1. Choose one direction (or null)
2. Decide 2-3 focus priorities
3. Surface only currently-blocking gaps
4. Produce calm, explainable rationale

**Constraints:**

- Never predict trends
- Never add recommendations beyond inputs
- Never violate rule-based constraints
- Prioritize actions that compound

---

## Pipeline Orchestration

**File:** `career_agent/agent.py`

### CareerGuidancePipeline

Main orchestrator that:

1. Receives an event
2. Asks Supervisor for execution plan
3. Runs agents in order
4. Caches intermediate results
5. Returns `HorizonOutput`

### Usage

```python
from career_agent import run_pipeline, UserProfile, SkillSnapshot, EventType

result = await run_pipeline(
    event_type=EventType.ONBOARDING_COMPLETED,
    user_profile=profile,
    skill_snapshot=skills,
)
# result is HorizonOutput
```

---

## State Ownership

| Data               | Owner                            |
| ------------------ | -------------------------------- |
| `UserProfile`      | External (onboarding system)     |
| `ProfileAnalysis`  | Profile Agent                    |
| `SkillSnapshot`    | External (skill tracking system) |
| `SkillGapAnalysis` | Skill Agent                      |
| `CareerDirection`  | Reasoning Agent                  |
| `HorizonOutput`    | Reasoning Agent                  |

---

## Failure Handling

- If any agent fails, Supervisor aborts the pipeline
- Previous valid `HorizonOutput` remains in effect
- System never returns partial reasoning

---

## File Structure

```
career_agent/
├── __init__.py              # Package exports
├── agent.py                 # Pipeline orchestrator
├── models.py                # All Pydantic schemas
├── supervisor.py            # Event router
├── profile_agent.py         # Human model classifier
├── skill_agent.py           # Gap analyzer
├── skill_graph.py           # Skill dependencies
├── career_recommendation_agent.py  # Direction suggester
└── reasoning_agent.py       # Final synthesizer
```

---

## Integration Notes

### Chat Integration

Chat is **not an agent**. It can:

- ✅ Trigger events
- ✅ Ask for explanations of stored HorizonOutput
- ❌ Run reasoning directly
- ❌ Modify HorizonOutput

### Frontend Integration

Frontend only:

- ✅ Sends events on user actions
- ✅ Renders HorizonOutput directly
- ❌ Interprets or transforms output
- ❌ Stores reasoning state

### Suggested API Endpoints

```
POST /api/events
  Body: { event_type, user_profile, skill_snapshot }
  Response: HorizonOutput

GET /api/horizon/{user_id}
  Response: Cached HorizonOutput
```
