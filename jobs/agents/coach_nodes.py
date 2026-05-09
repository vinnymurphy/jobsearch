
from .coach_state import CoachState


def analyzer_node(state: CoachState):
    # Logic to extract key skills from job_description
    return {"technical_gaps": ["Bazel", "Distributed Systems"]}

def scorer_node(state: CoachState):
    # Logic to compare resume vs job and calculate score
    return {"match_score": 85}

def strategist_node(state: CoachState):
    # Logic to generate specific talking points for you
    return {"interview_strategy": "Focus on your Django/Celery scaling experience."}