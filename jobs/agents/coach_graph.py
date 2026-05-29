from .coach_nodes import analyzer_node, scorer_node, strategist_node
from .coach_state import CoachState

from langgraph.graph import END, StateGraph

workflow = StateGraph(CoachState)

workflow.add_node("analyze", analyzer_node)
workflow.add_node("score", scorer_node)
workflow.add_node("strategize", strategist_node)

# Set the flow: Analyze -> Score -> Strategize -> Finish
workflow.set_entry_point("analyze")
workflow.add_edge("analyze", "score")
workflow.add_edge("score", "strategize")
workflow.add_edge("strategize", END)

interview_coach = workflow.compile()
