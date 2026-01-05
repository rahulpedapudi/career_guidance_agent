from dotenv import load_dotenv
load_dotenv()
load_dotenv("career_agent/.env")

from career_agent.models import UserProfileInput, Stage, ExposureLevel, TimeCommitment
from career_agent.profile_agent import ProfileAgent

def test():
    agent = ProfileAgent()
    user = UserProfileInput(
        user_id="debug_user",
        name="Schrodinger",
        stage=Stage.THIRD_YEAR,
        exposure_level=ExposureLevel.SMALL_PROJECTS,
        learning_preferences=["theoretical"],
        weekly_time_commitment=TimeCommitment.TEN_TO_FIFTEEN,
        goals=["Understand Qubits"],
        interests=["Quantum Computing", "Physics"]
    )
    
    print("\n--- Starting Analysis ---")
    result = agent.analyze(user)
    print("\n--- Result ---")
    print(f"Role: {result.role}")
    print(f"Level: {result.level}")
    print(f"Background: {result.background}")

if __name__ == "__main__":
    test()
