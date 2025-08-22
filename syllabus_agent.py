import os
import json
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph
from typing import TypedDict, List, Dict, Any
from dotenv import load_dotenv


load_dotenv()

llm = ChatGroq(temperature=0.2, model_name="openai/gpt-oss-120b")

syllabus_text = """
Class 11 Physics Syllabus Unit 1: Physical World and Measurement Physical World: Nature of physical laws. Scope and excitement of physics. Physics, technology, and society. Units and Measurements: Need for measurement. Systems of units: SI units, Fundamental and derived units. Dimensions of physical quantities. Accuracy, precision, and errors in measurement. Unit 2: Kinematics Motion in a Straight Line: Position, displacement, and distance. Speed and velocity. Acceleration. Equations of motion. Uniform and non-uniform motion. Motion in a Plane: Scalars and vectors. Vector addition and subtraction. Relative velocity. Uniform circular motion. Unit 3: Laws of Motion Force and Inertia: Newton’s First Law of Motion. Concept of force. Momentum and Impulse: Newton’s Second Law of Motion. Momentum and impulse. Conservation of Momentum: Newton’s Third Law of Motion. Applications of third law. Friction: Types of friction: static, kinetic. Laws of friction. Limiting friction. Circular Motion: Centripetal force. Banked curves. Unit 4: Work, Energy, and Power Work: Work done by a force. Work-energy theorem. Energy: Kinetic energy, potential energy. Conservation of energy. Power: Concept of power. Rate of doing work. Unit 5: Motion of System of Particles and Rigid Body Centre of Mass: Motion of centre of mass. Translational motion. Rigid Body: Moment of inertia. Rotational motion. Torque. Unit 6: Gravitation Universal Law of Gravitation: Gravitational force and its properties. Acceleration due to gravity. Kepler’s laws of planetary motion. Gravitational Potential Energy: Escape velocity. Orbital velocity. Earth and Satellites: Artificial satellites and their uses. Unit 7: Properties of Bulk Matter Elasticity: Hooke’s law. Stress-strain relationship. Fluid Mechanics: Pressure in fluids. Pascal’s law. Buoyancy and Archimedes’ principle. Thermal Properties of Matter: Specific heat. Calorimetry. Heat transfer methods. Unit 8: Thermodynamics Thermodynamic Systems: Types of systems: Open, closed, isolated. Laws of Thermodynamics: First law of thermodynamics (conservation of energy). Second law of thermodynamics (entropy). Heat engines and refrigerators. Unit 9: Behaviour of Perfect Gas and Kinetic Theory Kinetic Theory of Gases: Gas laws and molecular interpretation. Kinetic energy of gas molecules. Ideal gas equation. Unit 10: Oscillations and Waves Oscillations: Simple harmonic motion. Restoring force. Time period and frequency. Waves: Types of waves: Transverse and longitudinal. Wave motion, speed, and amplitude. Sound waves and Doppler effect. Practical Syllabus Measurement of Length, Mass, Time: Measurement using a meter scale, vernier caliper, micrometer screw gauge. Vector Addition: Using graphical method. Acceleration Due to Gravity: Using a simple pendulum. Work and Energy: Experiment with simple machines. Properties of Fluids: Determining the coefficient of viscosity. Heat Transfer: Specific heat of a solid and liquid.
"""

class RoadmapState(TypedDict):
    syllabus_text: str
    structured_roadmap: List[Dict[str, Any]]


def generate_roadmap(state):
    print("NODE: Generating Structured Roadmap")
    syllabus_text = state["syllabus_text"]
    
    prompt = f"""
    You are an expert curriculum designer for an LMS. Your task is to analyze the following syllabus text and convert it into a structured JSON object.

    The JSON should be an array of "modules," where each module represents a week.
    Each module object should have the following keys:
    - "week" (integer)
    - "title" (a string for the week's topic)
    - "learning_materials" (a list of strings, e.g., readings)
    - "assessments" (a list of strings, e.g., assignments, quizzes, projects)

    Syllabus Text:
    {syllabus_text}
    

    Structured JSON Output:
    """
    
    response = llm.invoke(prompt)
    cleaned_response = response.content.strip().replace("```json", "").replace("```", "")
    roadmap = json.loads(cleaned_response)
    
    print("SUCCESS: Roadmap Generated")
    return {"structured_roadmap": roadmap}

roadmap_workflow = StateGraph(RoadmapState)
roadmap_workflow.add_node("generate_roadmap", generate_roadmap)
roadmap_workflow.set_entry_point("generate_roadmap")
roadmap_workflow.add_edge("generate_roadmap", END)
roadmap_app = roadmap_workflow.compile()


inputs = {"syllabus_text": syllabus_text}
result = roadmap_app.invoke(inputs)

print("\n--- FINAL STRUCTURED ROADMAP")
print(json.dumps(result['structured_roadmap'], indent=2))