from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
import csv
import os
from groq import Groq
from dotenv import load_dotenv
from typing import Optional, Dict, List
import ast

# Load environment variables
load_dotenv()

app = FastAPI()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class UpskillingRequest(BaseModel):
    user_id: str
    role: str

def get_user_keywords(user_id: str) -> List[str]:
    """
    Get the user's keywords from the CSV file.
    """
    try:
        with open("ikigai_users.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["user_id"] == user_id:
                    # Convert string representation of list to actual list
                    keywords_str = row["genai_keywords"]
                    try:
                        # First try using ast.literal_eval for safer evaluation
                        keywords = ast.literal_eval(keywords_str)
                    except:
                        # Fallback to eval if ast.literal_eval fails
                        keywords = eval(keywords_str)
                    return keywords if isinstance(keywords, list) else []
        return []
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="User database not found")

def generate_upskilling_track(user_details: dict, role: str) -> dict:
    """
    Generate an upskilling track for a specific role based on user details.
    """
    prompt = f"""Based on the following user profile and desired role:
    User Profile:
    - What they love: {user_details['love']}
    - What they're good at: {user_details['good']}
    - What they can be paid for: {user_details['paid']}
    - What the world needs: {user_details['worldneeds']}
    
    Desired Role: {role}
    
    Generate a structured upskilling track that includes:
    1. Required Technical Skills (as a list)
    2. Required Soft Skills (as a list)
    3. Recommended Learning Resources (as a list)
    4. Estimated Timeline
    5. Key Milestones
    
    Format the response as a Python dictionary with these exact keys:
    {{
        "technical_skills": ["skill1", "skill2", ...],
        "soft_skills": ["skill1", "skill2", ...],
        "learning_resources": ["resource1", "resource2", ...],
        "timeline": "estimated timeline",
        "milestones": ["milestone1", "milestone2", ...]
    }}
    """

    completion = client.chat.completions.create(
        model="gemma2-9b-it",
        messages=[
            {"role": "system", "content": "You are a career development expert specializing in upskilling and professional growth. Always respond with a Python dictionary format."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )
    
    # Get the response and clean it up
    response_str = completion.choices[0].message.content.strip()
    
    # Extract the dictionary from the response
    try:
        # Find the dictionary in the response
        start_idx = response_str.find('{')
        end_idx = response_str.rfind('}') + 1
        if start_idx != -1 and end_idx != -1:
            response_str = response_str[start_idx:end_idx]
            # Convert string representation of dict to actual dict
            upskilling_track = eval(response_str)
            return upskilling_track
    except:
        return {
            "error": "Could not generate upskilling track",
            "raw_response": response_str
        }

@app.get("/get_user_roles/{user_id}")
def get_user_roles(user_id: str):
    """
    Get the list of roles (keywords) available for a user.
    """
    keywords = get_user_keywords(user_id)
    return {"user_id": user_id, "available_roles": keywords}

@app.post("/get_upskilling_track")
def get_upskilling_track(request: UpskillingRequest):
    """
    Get upskilling track for a user's desired role.
    """
    # First, get the user's available roles
    available_roles = get_user_keywords(request.user_id)
    
    # Validate that the requested role is in the available roles
    if not available_roles:
        raise HTTPException(status_code=404, detail="No roles found for this user")
    
    if request.role not in available_roles:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid role. Please select from: {', '.join(available_roles)}"
        )
    
    # Read user details from CSV
    user_details = None
    try:
        with open("ikigai_users.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["user_id"] == request.user_id:
                    user_details = row
                    break
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="User database not found")
    
    if not user_details:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate upskilling track
    upskilling_track = generate_upskilling_track(user_details, request.role)
    
    return {
        "user_id": request.user_id,
        "role": request.role,
        "upskilling_track": upskilling_track
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 