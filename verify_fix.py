
from career_agent.reasoning_agent import ReasoningAgent, build_active_interests, _role_to_interest
from career_agent.models import CareerAnalysis, CareerMatch, Confidence

def test_fixes():
    # Test 1: Title Generation
    print("Testing Title Generation...")
    roles = [
        "Blockchain Developer",
        "Smart Contract Engineer",
        "DApp Developer",
        "Web3 Specialist",
        "Crypto Analyst", 
        "Software Engineer"
    ]
    
    for role in roles:
        title = _role_to_interest(role)
        print(f"Role: {role} -> Title: {title}")
        if "Block" in role or "Smart" in role or "Web3" in role or "Crypto" in role or "DApp" in role:
             assert title == "Blockchain & Web3", f"Failed for {role}"
    
    # Test 2: Progress Calculation
    print("\nTesting Progress Calculation...")
    career = CareerAnalysis(
        primaryDirection=CareerMatch(role="Blockchain Developer", matchScore=95, confidence=Confidence.HIGH, reasoning="Test"),
        alternativeDirections=[
            CareerMatch(role="Smart Contract Developer", matchScore=80, confidence=Confidence.HIGH, reasoning="Test"),
            CareerMatch(role="Backend Developer", matchScore=70, confidence=Confidence.MODERATE, reasoning="Test")
        ]
    )
    
    interests = build_active_interests(career)
    
    for interest in interests:
        print(f"Interest ID: {interest.id}, Title: {interest.title}, Progress: {interest.progress}, Status: {interest.status}")
        
        if interest.status == "Planned": # Secondary interests
            assert interest.progress == 0, f"Progress should be 0 for {interest.id}, got {interest.progress}"
            
    print("\nAll tests passed!")

if __name__ == "__main__":
    try:
        test_fixes()
    except AssertionError as e:
        print(f"Test Failed: {e}")
    except Exception as e:
        print(f"Error: {e}")
