from typing import TypedDict, List
from langgraph.graph import StateGraph, END

class CoachState(TypedDict):
    job_description: str
    resume_text: str
    technical_gaps: List[str]
    match_score: int
    interview_strategy: str