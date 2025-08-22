import os
import json
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph
from typing import TypedDict, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(temperature=0.8, model_name="openai/gpt-oss-120b")

student_profiles = [
    {"name": "Alice", "strengths": ["Research", "Writing"], "weaknesses": ["Presentation", "Design"]},
    {"name": "Bob", "strengths": ["Design", "Brainstorming"], "weaknesses": ["Research", "Citations"]},
    {"name": "Charlie", "strengths": ["Presentation", "Leadership"], "weaknesses": ["Writing", "Brainstorming"]},
    {"name": "Diana", "strengths": ["Citations", "Organization"], "weaknesses": ["Leadership", "Design"]},
    {"name": "Eve", "strengths": ["Writing", "Presentation"], "weaknesses": ["Organization", "Research"]},
    {"name": "Frank", "strengths": ["Design", "Citations"], "weaknesses": ["Presentation", "Writing"]},
]

group_size = 3
prompt = f"""
You are an expert project manager and team builder. Your task is to form optimal student groups for a project.
Based on the following student profiles, create {len(student_profiles) // group_size} groups of {group_size}.

The goal is to create **balanced** groups where students' strengths can help cover their teammates' weaknesses.
Provide a brief justification for why each group is a good match.

Student Profiles:
{json.dumps(student_profiles, indent=2)}

Format your response as a JSON object. The top-level keys should be "Group 1", "Group 2", etc.
The value for each key should be an object containing "members" (a list of student names) and "justification" (a string).

JSON Output:
"""

response = llm.invoke(prompt)
cleaned_response = response.content.strip().replace("```json", "").replace("```", "")
suggested_groups = json.loads(cleaned_response)

print("--- AI-SUGGESTED GROUPS ---")
print(json.dumps(suggested_groups, indent=2))
