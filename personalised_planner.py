import os
import json
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph
from typing import TypedDict, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(temperature=0.8, model_name="openai/gpt-oss-120b")

#would be set by student
student_profile = {
    "name": "Alex Johnson",
    "learning_goal": "Ace the upcoming midterm exam.",
    "performance_data": {
        "course": "American History",
        "overall_grade": "B- (78%)",
        "topics_mastered": ["Colonial Beginnings", "The Constitution"],
        "topics_struggling": ["The Causes of the Revolution", "The Civil War Battles"],
    },
    "course_materials": {
        "The Causes of the Revolution": ["Chapter 3 Reading", "Video: 'Road to Independence'", "Practice Quiz 2"],
        "The Civil War Battles": ["Chapter 5 Reading", "Video: 'Gettysburg Explained'", "Interactive Map Simulation"],
        "Colonial Beginnings": ["Chapter 1 Reading", "Video: 'Life in the Colonies'"],
        "The Constitution": ["Chapter 4 Reading", "Primary Source: Federalist Papers"]
    },
    "personal_calendar": {
        "Monday": ["6 PM - 8 PM: Soccer Practice"],
        "Tuesday": ["7 PM - 9 PM: Part-time Job"],
        "Wednesday": ["6 PM - 8 PM: Soccer Practice"],
        "Thursday": ["Free"],
        "Friday": ["7 PM - 10 PM: Social Outing"],
        "Saturday": ["10 AM - 1 PM: Part-time Job"],
        "Sunday": ["Free"],
    }
}

class StudyPlanState(TypedDict):
    student_profile: Dict[str, Any]
    analysis: str
    study_tasks: List[Dict[str, str]]
    final_plan: Dict[str, Any]

def analyze_profile(state):
    print("Analyzing Student Profile")
    profile = state["student_profile"]
    
    prompt = f"""
    Analyze the following student profile and create a brief, 2-sentence summary of their current academic situation.
    Focus on their goal, their overall performance, and their specific areas of weakness.

    Profile:
    {json.dumps(profile, indent=2)}

    Analysis Summary:
    """
    
    response = llm.invoke(prompt)
    analysis = response.content
    print(f"  - Analysis: {analysis}")
    return {"analysis": analysis}


def create_study_tasks(state):
    print("Creating Study Tasks")
    profile = state["student_profile"]
    struggling_topics = profile["performance_data"]["topics_struggling"]
    
    tasks = []
    for topic in struggling_topics:
        materials = profile["course_materials"][topic]
        tasks.append({"topic": topic, "task_description": f"Deeply review the '{materials[0]}' to solidify foundational knowledge."})
        tasks.append({"topic": topic, "task_description": f"Engage with the '{materials[1]}' to get a different perspective."})

    print(f"  - Generated Tasks: {tasks}")
    return {"study_tasks": tasks}


def schedule_tasks(state):
    print("Scheduling Tasks into Calendar")
    profile = state["student_profile"]
    tasks = state["study_tasks"]
    calendar = profile["personal_calendar"]

    prompt = f"""
    You are an expert academic planner. Your job is to schedule a list of study tasks into a student's weekly calendar.
    Find the best available 1-hour slots for each task. Prioritize days that are marked as "Free".
    Do not schedule tasks during times that are already busy.

    **Student's Calendar:**
    {json.dumps(calendar, indent=2)}

    **Study Tasks to Schedule:**
    {json.dumps(tasks, indent=2)}

    **Your Output:**
    Provide your response as a JSON object where the keys are the days of the week.
    The value for each day should be a list of strings, with each string describing a scheduled event (e.g., "5 PM - 6 PM: Study 'The Causes of the Revolution'").
    Only include days where you have scheduled a task.

    **Scheduled Plan (JSON):**
    """

    response = llm.invoke(prompt)
    cleaned_response = response.content.strip().replace("```json", "").replace("```", "")
    
    try:
        scheduled_plan = json.loads(cleaned_response)
    except json.JSONDecodeError:
        print("  - FAILED to decode JSON from LLM. Returning raw response.")
        scheduled_plan = {"error": "Failed to generate a valid schedule.", "raw_output": cleaned_response}
        
    print(f"  - Generated Schedule: {scheduled_plan}")
    return {"final_plan": scheduled_plan}


workflow = StateGraph(StudyPlanState)

workflow.add_node("analyze_profile", analyze_profile)
workflow.add_node("create_study_tasks", create_study_tasks)
workflow.add_node("schedule_tasks", schedule_tasks)

workflow.set_entry_point("analyze_profile")
workflow.add_edge("analyze_profile", "create_study_tasks")
workflow.add_edge("create_study_tasks", "schedule_tasks")
workflow.add_edge("schedule_tasks", END)

app = workflow.compile()


inputs = {"student_profile": student_profile}
result = app.invoke(inputs)
print(json.dumps(result['final_plan'], indent=2))