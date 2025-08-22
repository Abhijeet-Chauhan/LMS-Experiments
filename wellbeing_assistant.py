import os
import json
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph
from typing import TypedDict, Literal

from dotenv import load_dotenv


load_dotenv()

llm = ChatGroq(temperature=0.8, model_name="openai/gpt-oss-120b")

Intent = Literal["stress", "time_management", "motivation", "general_query"]

class WellbeingState(TypedDict):
    student_input: str
    classified_intent: Intent
    agent_response: str

def classify_intent(state):
    print("---NODE: Classifying Intent---")
    student_input = state["student_input"]

    prompt = f"""
    You are an expert at classifying the intent of a student's message in a wellbeing context.
    Based on the user's message, classify it into one of the following categories:
    - stress (feeling overwhelmed, anxious about exams, pressure)
    - time_management (procrastinating, struggling to balance work, feeling disorganized)
    - motivation (feeling down, lack of drive, feeling stuck)
    - general_query (a simple question or greeting)

    Respond with ONLY the category name.

    User Message: "{student_input}"
    Classification:
    """

    response = llm.invoke(prompt)
    intent = response.content.strip().lower()

    if intent not in ["stress", "time_management", "motivation", "general_query"]:
        intent = "general_query"

    print(f"  - Classified Intent: {intent}")
    return {"classified_intent": intent}

def generate_strategy_response(state):
    print("---NODE: Generating Strategy Response---")
    student_input = state["student_input"]
    intent = state["classified_intent"]

    if intent == "stress":
        strategy_prompt = "Provide a simple, actionable mindfulness or breathing exercise (like the 4-7-8 technique or box breathing) that a student can do right now to calm their anxiety."
    elif intent == "time_management":
        strategy_prompt = "Provide a simple, actionable time management technique (like the Pomodoro Technique or the 'Two-Minute Rule') that a student can use to get started on their work."
    elif intent == "motivation":
        strategy_prompt = "Provide a simple, encouraging piece of advice focused on breaking down a large task into one single, small first step to help a student overcome a motivational block."
    else: 
        strategy_prompt = "Provide a warm, friendly, and open-ended greeting. Ask how you can help them today."

    prompt = f"""
    You are 'Aura', a confidential and supportive AI wellbeing assistant for the BrainFog LMS. Your tone is always calm, empathetic, and non-judgmental. You do not give medical advice.
    A student has expressed a concern related to: {intent}.
    Your task is to respond based on the following instruction: "{strategy_prompt}"

    Keep your response concise (2-4 sentences). End by gently reassuring them that this conversation is a private and safe space.
    """

    response = llm.invoke(prompt)
    print(f"  - Generated Response: {response.content}")
    return {"agent_response": response.content}


workflow = StateGraph(WellbeingState)

workflow.add_node("classify_intent", classify_intent)
workflow.add_node("generate_strategy_response", generate_strategy_response)

workflow.set_entry_point("classify_intent")
workflow.add_edge("classify_intent", "generate_strategy_response")
workflow.add_edge("generate_strategy_response", END)

app = workflow.compile()

def run_test(student_input):
    print(f"RUNNING TEST")
    print(f"Student Input: '{student_input}'")
    inputs = {"student_input": student_input}
    result = app.invoke(inputs)
    print("\nFinal Response")
    print(result['agent_response'])

# test Cases
run_test("I have so many exams coming up, I'm freaking out and can't focus.") # 'stress'
run_test("I know I need to study for my history final but I just can't get started.") #'time_management' or 'motivation'
run_test("hey")
run_test("I'm feeling like giving up") 