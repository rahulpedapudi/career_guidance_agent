1. Supervisor
2. Profile Agent
3. Skill Agent
4. Career Recommendation Agent
5. Reasoning Agent

## Data Model

```
UserProfile {
  user_id: string,
  stage: "first_year" | "second_year" | "third_year" | "final_year" | "graduate",
  graduation_year: number | null,
  exposure_level: "coursework" | "small_projects" | "serious_projects" | "professional",
  learning_preferences: string[],   // max 2
  weekly_time_commitment: "<5" | "5-10" | "10-15" | "15+",
  constraints: string[]             // optional
}
```

### What frontend consumes

```
HorizonOutput {
  current_direction: CareerDirection | null,
  focus_now: {
    title: string,
    rationale: string
  }[],
  blocking_gaps: {
    blocking: {
      skill: string,
      why: string
    }[],
    helpful: {
      skill: string,
      why: string
    }[]
  }
}


```
