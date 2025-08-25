import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict


class StudentProfile(BaseModel):
    student_id: int
    skills: List[str]
    interests: str
    performance_summary: str
    
class Job(BaseModel):
    id: int
    title: str
    company: str
    required_skills: List[str]

class Course(BaseModel):
    id: int
    title: str
    skill_taught: str

class CareerPathResponse(BaseModel):
    top_match: Job
    skill_gap: List[str]
    course_recommendations: Dict[str, List[Course]]
    summary: str


JOBS_FILE = "jobs.json"
JOBS_DB = {} 
ALL_JOBS_LIST = [] 

try:
    with open(JOBS_FILE, 'r') as f:
        ALL_JOBS_LIST = json.load(f)
        for job in ALL_JOBS_LIST:
            JOBS_DB[int(job['id'])] = Job(**job)
    print(f"Successfully loaded {len(JOBS_DB)} jobs from '{JOBS_FILE}'.")
except FileNotFoundError:
    print(f"WARNING: '{JOBS_FILE}' not found. The API will not have job data.")
    print("Please run the 'ingest_jobs.py' script first to create it.")
except Exception as e:
    print(f"An error occurred while loading {JOBS_FILE}: {e}")

# Mock courses database 
MOCK_COURSES_DB: List[Course] = [
    Course(id=201, title="Advanced Machine Learning with TensorFlow", skill_taught="TensorFlow"),
    Course(id=202, title="Introduction to AWS for Developers", skill_taught="AWS"),
    Course(id=203, title="Mastering Docker and Kubernetes", skill_taught="Kubernetes"),
    Course(id=204, title="Web Development with Django", skill_taught="Django"),
]

app = FastAPI(title="BrainFog AI Career Pathfinder")


def query_semantic_job_search(profile_text: str) -> List[int]:
    """
    MODIFIED MOCK FUNCTION: Simulates semantic search against the loaded file data.
    """
    print(f"--- Simulating semantic search over {len(ALL_JOBS_LIST)} loaded jobs... ---")
    search_terms = profile_text.lower().split()
    scores = {}
    for job in ALL_JOBS_LIST:
        score = 0
        for term in search_terms:
            if term in job['description'].lower():
                score += 1
        if score > 0:
            scores[int(job['id'])] = score
    
    # Sort by score, highest first
    sorted_job_ids = sorted(scores, key=scores.get, reverse=True)
    return sorted_job_ids[:10] # Return top 10 matches

def fetch_job_details_from_db(job_id: int) -> Job:
    """Fetches job details from the in-memory dictionary."""
    return JOBS_DB.get(job_id)

def fetch_courses_for_skill(skill: str) -> List[Course]:
    """Finds courses from the mock course DB."""
    return [course for course in MOCK_COURSES_DB if course.skill_taught.lower() == skill.lower()]


@app.post("/match-careers", response_model=CareerPathResponse)
async def match_careers(profile: StudentProfile):
    if not JOBS_DB:
        raise HTTPException(status_code=503, detail="Job data is not available. Please run the ingestion script.")

    profile_text = f"{' '.join(profile.skills)} {profile.interests} {profile.performance_summary}"
    matching_job_ids = query_semantic_job_search(profile_text)
    
    if not matching_job_ids:
        raise HTTPException(status_code=404, detail="Could not find any matching careers for this profile.")
    
    top_match = fetch_job_details_from_db(matching_job_ids[0])

    student_skills_set = set(skill.lower() for skill in profile.skills)
    required_skills_set = set(skill.lower() for skill in top_match.required_skills)
    
    missing_skills = list(required_skills_set - student_skills_set)
    strong_skills = list(student_skills_set.intersection(required_skills_set))

    course_recommendations = {}
    for skill in missing_skills:
        recommended_courses = fetch_courses_for_skill(skill.capitalize())
        if recommended_courses:
            course_recommendations[skill.capitalize()] = recommended_courses

    summary = (
        f"Based on your profile, you are a strong candidate for a role like '{top_match.title}' at {top_match.company}. "
        f"Your skills in {', '.join(s.capitalize() for s in strong_skills)} are highly relevant. "
        f"To be even more competitive, focus on developing these skills: {', '.join(s.capitalize() for s in missing_skills)}."
    )

    return CareerPathResponse(
        top_match=top_match,
        skill_gap=missing_skills,
        course_recommendations=course_recommendations,
        summary=summary
    )