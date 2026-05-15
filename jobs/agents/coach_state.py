from typing import TypedDict


class CoachState(TypedDict):
    job_description: str
    resume_text: str
    technical_gaps: list[str]
    match_score: int
    interview_strategy: str
