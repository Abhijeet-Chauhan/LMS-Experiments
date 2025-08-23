# ingest_jobs.py
import requests
import os
import json
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()

# --- Configuration ---
API_URL = "http://api.adzuna.com/v1/api/jobs/us/search/1" # Using 'us' for United States jobs
APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

# A list of job titles to search for to get a diverse dataset
SEARCH_QUERIES = [
    "data scientist",
    "machine learning engineer",
    "cloud devops engineer",
    "backend developer python",
    "data analyst sql"
]
RESULTS_PER_PAGE = 50 # Adzuna's max is 50
OUTPUT_FILE = "jobs.json"

def extract_skills_from_description(description: str) -> list:
    """A simple placeholder for skill extraction."""
    # In a real system, this would use a more sophisticated NLP model.
    known_skills = ["python", "r", "sql", "tensorflow", "scikit-learn", "aws", "docker", "kubernetes", "ci/cd", "django", "rest apis", "data analysis", "pytorch"]
    found_skills = {skill.capitalize() for skill in known_skills if skill in description.lower()}
    return list(found_skills)

def fetch_and_save_jobs():
    """
    Connects to the Adzuna API for each query, processes the results,
    and saves them to a JSON file.
    """
    if not APP_ID or not APP_KEY:
        print("ERROR: Adzuna App ID or Key not found in .env file.")
        print("Please create a .env file with your credentials.")
        return

    all_jobs = []
    print("Starting job ingestion from Adzuna...")

    for query in SEARCH_QUERIES:
        print(f"Fetching jobs for query: '{query}'...")
        params = {
            'app_id': APP_ID,
            'app_key': APP_KEY,
            'results_per_page': RESULTS_PER_PAGE,
            'what': query,
            'content-type': 'application/json'
        }

        try:
            response = requests.get(API_URL, params=params)
            response.raise_for_status()  # Raises an exception for bad status codes (4xx or 5xx)
            data = response.json()
            
            for job_data in data.get('results', []):
                processed_job = {
                    "id": job_data.get('id'),
                    "title": job_data.get('title'),
                    "company": job_data.get('company', {}).get('display_name'),
                    # We need to extract skills from the description
                    "required_skills": extract_skills_from_description(job_data.get('description', '')),
                    # Storing the full description is useful for semantic search
                    "description": job_data.get('description') 
                }
                all_jobs.append(processed_job)

        except requests.exceptions.RequestException as e:
            print(f"ERROR: Could not fetch data for query '{query}'. Reason: {e}")
            continue

    print(f"\nFetched a total of {len(all_jobs)} jobs.")

    # Save the processed data to a local file
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(all_jobs, f, indent=2)
    
    print(f"Successfully saved jobs to '{OUTPUT_FILE}'.")


if __name__ == "__main__":
    fetch_and_save_jobs()