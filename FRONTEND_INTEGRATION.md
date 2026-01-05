# Frontend Integration Guide

## Base URL

```
http://localhost:8000
```

---

## Architecture Notes

> [!IMPORTANT] > **LLM-Powered Profile Analysis**: The `ProfileAgent` uses **Gemini 2.5 Flash** to dynamically infer user personas (role, level, background) based on their interests and goals. This produces more nuanced results than static rule-based logic.
>
> If no `GOOGLE_API_KEY` is configured in the environment, the system gracefully falls back to rule-based analysis.

The backend consists of 4 specialized agents:
| Agent | Purpose | LLM |
|-------|---------|-----|
| **ProfileAgent** | Analyzes user profile, infers role & level | ✅ Gemini 2.5 Flash |
| **SkillAgent** | Identifies skill gaps & dependencies | ❌ Rule-based |
| **CareerAgent** | Recommends career directions | ❌ Rule-based |
| **ReasoningAgent** | Synthesizes final HorizonOutput | ❌ Rule-based |

---

## Endpoints

### 1. Health Check

```http
GET /health
```

**Response:**

```json
{
  "status": "ok",
  "message": "Career Guidance API is running",
  "dev_mode": true
}
```

---

### 2. Submit Onboarding

```http
POST /api/onboard
Content-Type: application/json
```

**Request Body:**

```json
{
  "user_id": "string (required)",
  "name": "string (required)",
  "stage": "first_year | second_year | third_year | final_year | graduate",
  "graduation_year": 2026,
  "exposure_level": "coursework | small_projects | serious_projects | professional",
  "learning_preferences": ["hands-on projects"],
  "weekly_time_commitment": "<5 | 5-10 | 10-15 | 15+",
  "constraints": [],
  "goals": ["Get a job at FAANG"],
  "interests": ["AI/ML", "Backend Development"]
}
```

> [!TIP]
> The API is flexible with `stage` and `exposure_level` values. It accepts both enum values (`third_year`) and human-readable strings (`Third Year`). The `user_id` field also accepts the alias `userId`.

**Response:** `HorizonOutput` (see below)

**Example:**

```javascript
const response = await fetch("http://localhost:8000/api/onboard", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    user_id: "user_123",
    name: "John Doe",
    stage: "third_year",
    graduation_year: 2026,
    exposure_level: "small_projects",
    learning_preferences: ["hands-on projects"],
    weekly_time_commitment: "10-15",
    constraints: [],
    goals: ["Get internship"],
    interests: ["Backend", "AI/ML"],
  }),
});
const horizonOutput = await response.json();
```

---

### 3. Update Skills

```http
POST /api/skills
Content-Type: application/json
```

**Request Body:**

```json
{
  "user_id": "string (required)",
  "skills": [
    { "skill": "python", "level": "comfortable" },
    { "skill": "git", "level": "used_a_bit" },
    { "skill": "data_structures", "level": "aware" }
  ]
}
```

**Skill Levels:**
| Level | Meaning |
|-------|---------|
| `aware` | Heard of it, haven't used it |
| `used_a_bit` | Tried it, not confident |
| `comfortable` | Can use it independently |

**Available Skills:**

```
programming_basics, python, java, javascript, typescript
html_css, react, nodejs, frontend_frameworks, backend_frameworks
data_structures, algorithms, system_design
databases, sql, nosql
git, linux, networking, docker, kubernetes, cloud_services, devops
statistics, linear_algebra, data_analysis, machine_learning, deep_learning
```

**Response:** `HorizonOutput`

---

### 4. Trigger Event

```http
POST /api/events
Content-Type: application/json
```

**Request Body:**

```json
{
  "user_id": "string (required)",
  "event_type": "direction_changed | check_in",
  "payload": {}
}
```

**Event Types:**
| Event | When to Use |
|-------|-------------|
| `onboarding_completed` | After onboarding form (use `/api/onboard` instead) |
| `skill_updated` | After skill changes (use `/api/skills` instead) |
| `direction_changed` | User picks a new career direction |
| `check_in` | Periodic refresh (e.g., dashboard open) |

**Response:** `HorizonOutput`

---

### 5. Get Cached Horizon

```http
GET /api/horizon/{user_id}
```

**Response:** `HorizonOutput`

**Note:** Does NOT re-run the pipeline. Returns the last computed output.

---

### 6. Get User Profile

```http
GET /api/profile/{user_id}
```

**Response:**

```json
{
  "user_id": "user_123",
  "name": "John Doe",
  "stage": "third_year",
  "graduation_year": 2026,
  "exposure_level": "small_projects",
  "learning_preferences": ["hands-on projects"],
  "weekly_time_commitment": "10-15",
  "constraints": [],
  "goals": ["Get internship"],
  "interests": ["Backend", "AI/ML"]
}
```

---

### 7. Get User Skills

```http
GET /api/skills/{user_id}
```

**Response:**

```json
{
  "skills": [
    { "skill": "python", "level": "comfortable" },
    { "skill": "git", "level": "used_a_bit" }
  ]
}
```

---

## Response Schema: HorizonOutput

This is the main response your dashboard should render.

```typescript
interface HorizonOutput {
  version: string;
  generatedAt: string;
  userId: string;

  profile: ProfileSection;
  stats: Stats;
  dailyInsight: DailyInsight;
  careerDirection: CareerDirection;
  immediateFocus: ImmediateFocus;
  skillsSnapshot: SkillsSnapshot;
  activeInterests: ActiveInterest[];
  nextAction: NextAction;
  recentActivity: ActivityItem[];
  insights: Insight[];
  roadmap: Roadmap;
}

interface ProfileSection {
  name: string;
  role: string; // e.g., "Aspiring ML Engineer"
  level: string; // "Beginner" | "Intermediate" | "Advanced"
  nextLevel: string | null;
  progressToNextLevel: number; // 0-100
  exposureLevel: string;
  learningStyle: string;
}

interface Stats {
  skillsLearned: number;
  learningHours: number;
  roadmapCompletion: number; // 0-100
  domainsExplored: number;
}

interface DailyInsight {
  message: string;
  type: string; // "motivation" | "tip" | "reminder"
  author?: string;
}

interface CareerDirection {
  primaryRole: string;
  secondaryRoles: string[];
  matchScore: number; // 0-100
  confidence: "low" | "moderate" | "high";
  reasoning: string;
}

interface ImmediateFocus {
  skill: string;
  reason: string;
  timeWindow: string;
  priority: "low" | "medium" | "high";
}

interface SkillsSnapshot {
  completed: string[];
  inProgress: string[];
  planned: string[];
  gaps: SkillGapOutput[];
}

interface SkillGapOutput {
  skill: string;
  impact: "low" | "medium" | "high";
  reason: string;
}

interface ActiveInterest {
  id: string;
  title: string;
  progress: number; // 0-100
  status: string; // "Active" | "Planned" | "Paused" | "Completed"
  color: string; // Tailwind gradient, e.g., "from-blue-500 to-cyan-500"
  modulesRemaining: number;
  icon: string; // "star" or other icon identifier
}

interface NextAction {
  title: string;
  subtitle: string;
  duration: string;
  type: string; // "learning" | "project" | "practice"
  actionUrl?: string;
}

interface ActivityItem {
  id: string;
  title: string;
  time: string; // "Just now", "2 hours ago", etc.
  xp: number;
}

interface Insight {
  type: "opportunity" | "risk" | "trend";
  message: string;
  confidence: "low" | "moderate" | "high";
}

interface Roadmap {
  id: string;
  title: string;
  totalPhases: number;
  currentPhase: number;
  overallProgress: number; // 0-100
  phases: RoadmapPhase[];
}

interface RoadmapPhase {
  id: string;
  title: string;
  status: "not-started" | "in-progress" | "completed";
  progress: number;
  skills: RoadmapSkill[];
}

interface RoadmapSkill {
  id: string;
  name: string;
  status: string;
}
```

---

## Example Response

```json
{
  "version": "1.1",
  "generatedAt": "2026-01-05T18:30:00.000Z",
  "userId": "user_123",
  "profile": {
    "name": "John Doe",
    "role": "Aspiring ML Engineer",
    "level": "Intermediate",
    "nextLevel": "Advanced",
    "progressToNextLevel": 55,
    "exposureLevel": "Built small projects",
    "learningStyle": "hands-on projects"
  },
  "stats": {
    "skillsLearned": 5,
    "learningHours": 85,
    "roadmapCompletion": 25,
    "domainsExplored": 3
  },
  "dailyInsight": {
    "message": "Consistency is the only algorithm that matters.",
    "type": "motivation"
  },
  "careerDirection": {
    "primaryRole": "ML Engineer",
    "secondaryRoles": ["Data Scientist", "Backend Developer"],
    "matchScore": 75,
    "confidence": "moderate",
    "reasoning": "Based on your skills and interests in AI/ML"
  },
  "immediateFocus": {
    "skill": "Linear Algebra",
    "reason": "Foundation for machine learning algorithms",
    "timeWindow": "Next 30 days",
    "priority": "high"
  },
  "skillsSnapshot": {
    "completed": ["Python", "Git"],
    "inProgress": ["Data Structures"],
    "planned": ["Algorithms", "Machine Learning"],
    "gaps": [
      {
        "skill": "Linear Algebra",
        "impact": "high",
        "reason": "Required for ML fundamentals"
      }
    ]
  },
  "activeInterests": [
    {
      "id": "ml-engineer",
      "title": "AI & Machine Learning",
      "progress": 40,
      "status": "Active",
      "color": "from-emerald-500 to-teal-500",
      "modulesRemaining": 8,
      "icon": "star"
    },
    {
      "id": "backend-developer",
      "title": "Backend Development",
      "progress": 15,
      "status": "Planned",
      "color": "from-blue-500 to-cyan-500",
      "modulesRemaining": 4,
      "icon": "star"
    }
  ],
  "nextAction": {
    "title": "Complete Linear Algebra Basics",
    "subtitle": "Khan Academy - Vectors & Matrices",
    "duration": "2 hours",
    "type": "learning",
    "actionUrl": null
  },
  "recentActivity": [
    {
      "id": "act_1",
      "title": "Completed Python",
      "time": "2 hours ago",
      "xp": 50
    },
    {
      "id": "act_2",
      "title": "Started Data Structures",
      "time": "Yesterday",
      "xp": 0
    }
  ],
  "insights": [
    {
      "type": "opportunity",
      "message": "Your Python, Git skills position you well for ML Engineer.",
      "confidence": "high"
    },
    {
      "type": "trend",
      "message": "AI-Assisted Development is emerging fast.",
      "confidence": "moderate"
    }
  ],
  "roadmap": {
    "id": "ml-engineer-path",
    "title": "ML Engineer",
    "totalPhases": 6,
    "currentPhase": 2,
    "overallProgress": 25,
    "phases": [
      {
        "id": "phase-1",
        "title": "Programming Foundations",
        "status": "completed",
        "progress": 100,
        "skills": [
          { "id": "python", "name": "Python", "status": "completed" },
          { "id": "git", "name": "Git", "status": "completed" }
        ]
      },
      {
        "id": "phase-2",
        "title": "Math for ML",
        "status": "in-progress",
        "progress": 50,
        "skills": [
          {
            "id": "linear_algebra",
            "name": "Linear Algebra",
            "status": "in-progress"
          },
          { "id": "statistics", "name": "Statistics", "status": "not-started" }
        ]
      }
    ]
  }
}
```

---

## Error Responses

**404 - User Not Found:**

```json
{
  "detail": "Complete onboarding first."
}
```

**422 - Validation Error:**

```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**500 - Pipeline Error:**

```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## CORS

API allows all origins (`*`) in development. No special headers needed from frontend.

---

## Interactive API Docs

Visit `http://localhost:8000/docs` for Swagger UI with:

- Try-it-out for all endpoints
- Request/response schemas
- Example payloads
