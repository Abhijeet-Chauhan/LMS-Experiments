from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict

class StudentProfile(BaseModel):
    """
    This model defines the data we expect to receive about the student.
    In a real application, this might be fetched from a user database.
    """
    student_id: int
    skills: List[str] = ["Python", "Data Analysis", "SQL"]
    interests: str = "Interested in machine learning and cloud computing."
    performance_summary: str = "Strong performance in programming courses, average in advanced mathematics."
    
class Job(BaseModel):
    """Defines the structure of a job listing."""
    id: int
    title: str
    company: str
    required_skills: List[str]

class Course(BaseModel):
    """Defines the structure of a course on the BrainFog LMS."""
    id: int
    title: str
    skill_taught: str

class CareerPathResponse(BaseModel):
    """Defines the final, detailed response sent back to the user."""
    top_match: Job
    skill_gap: List[str]
    course_recommendations: Dict[str, List[Course]]
    summary: str



app = FastAPI(
    title="BrainFog AI Career Pathfinder",
    description="An API for matching students with career paths and providing skill gap analysis."
)


# --- Mock Database and External Services ---
# In a real application, these functions would make network requests to your
# databases (PostgreSQL, ChromaDB) and the NestJS Core LMS service.

MOCK_JOBS_DB: Dict[int, Job] = {
    101: Job(id=101, title="Data Scientist", company="InnovateAI", required_skills=["Python", "R", "SQL", "TensorFlow", "Scikit-learn"]),
    102: Job(id=102, title="Cloud DevOps Engineer", company="CloudServe", required_skills=["AWS", "Docker", "Kubernetes", "Python", "CI/CD"]),
    103: Job(id=103, title="Backend Developer", company="CodeFoundry", required_skills=["Python", "Django", "SQL", "REST APIs", "Docker"]),
    104: Job(id=104, title="Machine Learning Engineer", company="AI Solutions", required_skills=["Python", "PyTorch", "SQL", "Data Analysis", "AWS"]),
}

MOCK_COURSES_DB: List[Course] = [
    Course(id=201, title="Advanced Machine Learning with TensorFlow", skill_taught="TensorFlow"),
    Course(id=202, title="Introduction to AWS for Developers", skill_taught="AWS"),
    Course(id=203, title="Mastering Docker and Kubernetes", skill_taught="Kubernetes"),
    Course(id=204, title="Web Development with Django", skill_taught="Django"),
]

def query_semantic_job_search(profile_text: str) -> List[int]:
    """
    MOCK FUNCTION: Simulates a semantic search query.
    
    PRODUCTION: This function would use a sentence-transformer model to encode
    the profile_text into a vector, then query a vector database (like ChromaDB)
    to find the IDs of the most semantically similar job descriptions.
    """
    print(f"--- Simulating semantic search for profile: '{profile_text[:50]}...' ---")
    # Simple logic for the mock: find jobs with the most overlapping skills
    # In reality, this would be a sophisticated vector similarity search.
    if "machine learning" in profile_text or "data scientist" in profile_text:
        return [104, 101, 103] # Return job IDs, best match first
    if "cloud" in profile_text or "aws" in profile_text:
        return [102, 104, 103]
    return [103, 102, 101]

def fetch_job_details_from_db(job_ids: List[int]) -> List[Job]:
    """
    MOCK FUNCTION: Simulates fetching full job details from a primary database.
    
    PRODUCTION: This would execute a `SELECT * FROM jobs WHERE id IN (...)`
    query against your PostgreSQL database.
    """
    print(f"--- Simulating fetching job details for IDs: {job_ids} from PostgreSQL ---")
    return [MOCK_JOBS_DB[job_id] for job_id in job_ids if job_id in MOCK_JOBS_DB]

def fetch_courses_for_skill(skill: str) -> List[Course]:
    """
    MOCK FUNCTION: Simulates calling the NestJS Core LMS API.
    
    PRODUCTION: This would make an HTTP GET request, e.g.,
    `requests.get(f"http://lms-api/courses?skill={skill}")`
    """
    print(f"--- Simulating API call to NestJS to find courses for skill: '{skill}' ---")
    return [course for course in MOCK_COURSES_DB if course.skill_taught.lower() == skill.lower()]


@app.post("/match-careers", response_model=CareerPathResponse)
async def match_careers(profile: StudentProfile):
    """
    This is the main endpoint. It takes a student's profile and returns a
    detailed career path analysis.
    """
    profile_text = (
        f"Skills: {', '.join(profile.skills)}. "
        f"Interests: {profile.interests}. "
        f"Performance Summary: {profile.performance_summary}"
    )

    matching_job_ids = query_semantic_job_search(profile_text)

    matching_jobs = fetch_job_details_from_db(matching_job_ids)
    if not matching_jobs:
        return {"error": "Could not find any matching careers at this time."}
    
    top_match = matching_jobs[0]

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
        f"Excellent progress! Based on your profile, you are a strong candidate for a role like '{top_match.title}'. "
        f"Your skills in {', '.join(s.capitalize() for s in strong_skills)} are highly relevant. "
        f"To become an even more competitive applicant, focus on developing these skills: {', '.join(s.capitalize() for s in missing_skills)}. "
        f"You can start your journey right here on BrainFog with the recommended courses."
    )

    return CareerPathResponse(
        top_match=top_match,
        skill_gap=missing_skills,
        course_recommendations=course_recommendations,
        summary=summary
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)