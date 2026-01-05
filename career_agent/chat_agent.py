"""
Chat Agent — Conversational Career Guidance.

Uses Gemini to answer user questions with their HorizonOutput as context.
"""

import os
from dotenv import load_dotenv

load_dotenv()

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from career_agent.models import HorizonOutput


# Configure Gemini
API_KEY = os.getenv("GOOGLE_API_KEY")
if GEMINI_AVAILABLE and API_KEY:
    genai.configure(api_key=API_KEY)
    print("✨ ChatAgent: LLM Enabled (Gemini 2.5 Flash)")
else:
    print("⚠️ ChatAgent: LLM Disabled (no API key)")


# System prompt for the chatbot
SYSTEM_PROMPT = """You are a friendly and knowledgeable career guidance assistant called "Horizon AI".

Your role is to help users navigate their career journey based on their personalized profile, skills, and roadmap.

Guidelines:
- Be encouraging and supportive, but realistic
- Give specific, actionable advice based on the user's current progress
- Reference their roadmap phases, skills, and career direction when relevant
- Keep responses concise (2-4 sentences for simple questions, more for complex ones)
- Use emojis sparingly to keep it friendly 🎯
- If asked about something outside career guidance, gently redirect

You have access to the user's complete career profile below. Use this context to personalize your responses.
"""


def build_context_from_horizon(horizon: HorizonOutput) -> str:
    """Build context string from HorizonOutput for the LLM."""
    
    # Profile summary
    profile = horizon.profile
    context = f"""
USER PROFILE:
- Name: {profile.name}
- Role: {profile.role}
- Level: {profile.level} (Progress to next: {profile.progressToNextLevel}%)
- Learning Style: {profile.learningStyle}

CAREER DIRECTION:
- Primary: {horizon.careerDirection.primaryRole if horizon.careerDirection else 'Not set'}
- Secondary: {', '.join(horizon.careerDirection.secondaryRoles) if horizon.careerDirection else 'None'}
- Match Score: {horizon.careerDirection.matchScore if horizon.careerDirection else 0}%

SKILLS SNAPSHOT:
- Completed: {', '.join(horizon.skillsSnapshot.completed) if horizon.skillsSnapshot.completed else 'None yet'}
- In Progress: {', '.join(horizon.skillsSnapshot.inProgress) if horizon.skillsSnapshot.inProgress else 'None'}
- Planned: {', '.join(horizon.skillsSnapshot.planned) if horizon.skillsSnapshot.planned else 'None'}
- Gaps: {', '.join([g.skill for g in horizon.skillsSnapshot.gaps]) if horizon.skillsSnapshot.gaps else 'None identified'}

IMMEDIATE FOCUS:
- Skill: {horizon.immediateFocus.skill if horizon.immediateFocus else 'Not set'}
- Reason: {horizon.immediateFocus.reason if horizon.immediateFocus else 'N/A'}
- Priority: {horizon.immediateFocus.priority if horizon.immediateFocus else 'N/A'}

ACTIVE INTERESTS:
"""
    
    for interest in horizon.activeInterests:
        context += f"- {interest.title}: {interest.progress}% complete, {interest.modulesRemaining} modules remaining\n"
    
    # Roadmap summary
    if horizon.roadmaps:
        context += "\nROADMAPS:\n"
        for roadmap in horizon.roadmaps:
            context += f"- {roadmap.title}: Phase {roadmap.currentPhase}/{roadmap.totalPhases}, {roadmap.overallProgress}% complete\n"
            for phase in roadmap.phases[:2]:  # First 2 phases for brevity
                context += f"  • {phase.title} ({phase.status}): {', '.join([s.name for s in phase.skills])}\n"
    
    # Stats
    context += f"""
STATS:
- Skills Learned: {horizon.stats.skillsLearned}
- Learning Hours: {horizon.stats.learningHours}
- Roadmap Completion: {horizon.stats.roadmapCompletion}%
- Domains Explored: {horizon.stats.domainsExplored}
"""
    
    return context


class ChatAgent:
    """
    Conversational agent for career guidance.
    
    Uses the user's HorizonOutput as context for personalized responses.
    """
    
import datetime
from career_agent.database import db

# ... imports ...

class ChatAgent:
    """
    Conversational agent for career guidance.
    
    Uses the user's HorizonOutput as context for personalized responses.
    """
    
    def __init__(self):
        self.model = None
        # self.conversations removed in favor of MongoDB
        
        if GEMINI_AVAILABLE and API_KEY:
            try:
                self.model = genai.GenerativeModel(
                    model_name="gemini-2.5-flash",
                    generation_config={
                        "temperature": 0.7,
                        "max_output_tokens": 1024,
                    },
                )
            except Exception as e:
                print(f"⚠️ ChatAgent: Failed to init model: {e}")
                self.model = None
    
    async def chat(
        self,
        message: str,
        horizon: HorizonOutput,
        session_id: str | None = None,
        user_id: str | None = None,
    ) -> dict:
        """
        Generate a response to the user's message.
        """
        # Fallback if no model
        if not self.model:
            return self._fallback_response(message, horizon)
        
        try:
            # Build context
            context = build_context_from_horizon(horizon)
            
            # Get conversation history from DB
            history = []
            if session_id and user_id:
                coll = db.get_collection("conversations")
                if coll is not None:
                    # Find existing session
                    doc = await coll.find_one({"session_id": session_id, "user_id": user_id})
                    if doc:
                        history = doc.get("messages", [])
            
            # Build the full prompt
            full_prompt = f"{SYSTEM_PROMPT}\n\n{context}\n\n"
            
            # Add history
            if history:
                full_prompt += "CONVERSATION HISTORY:\n"
                for turn in history[-6:]:  # Last 3 exchanges (6 messages)
                    role = turn.get("role", "unknown")
                    content = turn.get("content", "")
                    if role == "user":
                        full_prompt += f"User: {content}\n"
                    elif role == "assistant":
                        full_prompt += f"Assistant: {content}\n"
                full_prompt += "\n"
            
            full_prompt += f"User: {message}\nAssistant:"
            
            # Generate response
            response = await self.model.generate_content_async(full_prompt)
            assistant_message = response.text.strip()
            
            # Persist to DB
            if session_id and user_id:
                coll = db.get_collection("conversations")
                if coll is not None:
                    new_messages = [
                        {"role": "user", "content": message, "timestamp": datetime.datetime.utcnow()},
                        {"role": "assistant", "content": assistant_message, "timestamp": datetime.datetime.utcnow()}
                    ]
                    
                    await coll.update_one(
                        {"session_id": session_id, "user_id": user_id},
                        {
                            "$push": {"messages": {"$each": new_messages}},
                            "$setOnInsert": {"created_at": datetime.datetime.utcnow()}
                        },
                        upsert=True
                    )
            
            # Generate suggestions based on context
            suggestions = self._generate_suggestions(message, horizon)
            
            return {
                "response": assistant_message,
                "suggestions": suggestions,
            }
        
        except Exception as e:
            print(f"❌ ChatAgent Error: {e}")
            return self._fallback_response(message, horizon)
    
    def _fallback_response(self, message: str, horizon: HorizonOutput) -> dict:
        """Generate a simple rule-based response when LLM is unavailable."""
        message_lower = message.lower()
        
        if "next" in message_lower or "focus" in message_lower:
            focus = horizon.immediateFocus
            if focus:
                response = f"Based on your roadmap, you should focus on **{focus.skill}**. {focus.reason}"
            else:
                response = "Check your roadmap for the next skill to learn!"
        
        elif "roadmap" in message_lower or "progress" in message_lower:
            if horizon.roadmaps:
                rm = horizon.roadmaps[0]
                response = f"You're on Phase {rm.currentPhase} of {rm.totalPhases} in your {rm.title} roadmap. Overall progress: {rm.overallProgress}%"
            else:
                response = "Your roadmap is being generated. Check back soon!"
        
        elif "skill" in message_lower:
            completed = len(horizon.skillsSnapshot.completed)
            in_progress = len(horizon.skillsSnapshot.inProgress)
            response = f"You've completed {completed} skills and have {in_progress} in progress. Keep it up! 🎯"
        
        elif "career" in message_lower or "job" in message_lower:
            if horizon.careerDirection:
                response = f"Your primary career direction is **{horizon.careerDirection.primaryRole}** with a {horizon.careerDirection.matchScore}% match score."
            else:
                response = "Complete your profile to get career recommendations!"
        
        else:
            response = f"I'm here to help with your career journey! You can ask about your roadmap, skills, or next steps. Your current focus is on becoming a {horizon.careerDirection.primaryRole if horizon.careerDirection else 'professional'}."
        
        return {
            "response": response,
            "suggestions": self._generate_suggestions(message, horizon),
        }
    
    def _generate_suggestions(self, message: str, horizon: HorizonOutput) -> list[str]:
        """Generate follow-up suggestions based on context."""
        suggestions = []
        
        if horizon.immediateFocus:
            suggestions.append(f"Tell me more about {horizon.immediateFocus.skill}")
        
        if horizon.roadmaps:
            suggestions.append("Show my roadmap progress")
        
        if horizon.skillsSnapshot.gaps:
            suggestions.append("What are my skill gaps?")
        
        suggestions.append("What should I learn next?")
        
        return suggestions[:3]  # Max 3 suggestions
    
    async def clear_session(self, session_id: str):
        """Clear conversation history for a session."""
        coll = db.get_collection("conversations")
        if coll is not None:
            await coll.delete_one({"session_id": session_id})

