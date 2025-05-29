#0. Loading libraries
from pydantic import BaseModel #to have data checks in place #Library ensures that the data inputs are in place
from fastapi import FastAPI    #Python library to create APIs
import csv
import os
from groq import Groq
import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

app = FastAPI()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

#1. Define the data model
class ikigai_user(BaseModel):
    user_id: Optional[str] = None
    username: str
    love: str
    good: str
    paid: str
    worldneeds: str
    genai_summary: Optional[str] = None
    genai_keywords: Optional[str] = None


def generate_summary(love: str, good: str, paid: str, worldneeds: str):
    """
    Generate a summary based on what the user loves and what they're good at using Groq LLM.
    """
    prompt = f"""Based on the following information about a person:
    What they love: {love}
    What they're good at: {good}
    What they're paid for: {paid}
    What the world needs: {worldneeds}
    
    Generate a thoughtful and inspiring summary that:
    1. Provides clear roles or career paths that aligns with their love, good, paid and world needs. 
    2. Keep the response concise but meaningful.
    3. Don't add new lines character"""

    completion = client.chat.completions.create(
        model="gemma2-9b-it",
        messages=[
            {"role": "system", "content": "You are a helpful career and life purpose advisor."},
            {"role": "user", "content": prompt}
        ],
        #temperature=0.7,
        max_tokens=150
    )
    summary = completion.choices[0].message.content 
    return summary

def generate_keywords(summary: str):
    """
    Generate a list of keywords based on what the user's summary is.
    """
    prompt = f"""Based on the following {summary} about a person
    Generate a list of keywords that are relevant to the summary:
    1. Output should be a list of keywords e.g. ["writer", "teacher", "developer", "designer"]
    """

    completion = client.chat.completions.create(
        model="gemma2-9b-it",
        messages=[
            {"role": "system", "content": "You are a helpful career and life purpose advisor. Always respond with a Python list format only."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150
    )
    
    # Get the response and clean it up
    keywords_str = completion.choices[0].message.content.strip()
    
    # Remove any extra text before or after the list
    start_idx = keywords_str.find('[')
    end_idx = keywords_str.rfind(']') + 1
    
    if start_idx != -1 and end_idx != -1:
        keywords_str = keywords_str[start_idx:end_idx]
    
    # Convert string representation of list to actual list
    try:
        # Use eval to convert string representation of list to actual list
        keywords = eval(keywords_str)
        # Ensure it's a list
        if not isinstance(keywords, list):
            keywords = [keywords]
        return keywords
    except:
        # Fallback: split by comma and clean up if eval fails
        keywords = [k.strip().strip('"\'[]') for k in keywords_str.split(',')]
        return keywords


#2. Building the API endpoints
#2.1. Create a user
@app.post("/create_ikigai")
def create_ikigai(user: ikigai_user):
    # Generate summary based on love and good inputs
    user.genai_summary = generate_summary(user.love, user.good, user.paid, user.worldneeds)
    user.genai_keywords = generate_keywords(user.genai_summary)
    
    # Create CSV file with headers if it doesn't exist
    csv_file = "ikigai_users.csv"
    file_exists = os.path.isfile(csv_file)
    
    with open(csv_file, "a", newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            # Write headers
            writer.writerow(["user_id", "username", "love", "good", "paid", "worldneeds", "genai_summary", "genai_keywords"])
        
        # Generate user_id if not provided
        if not user.user_id:
            # Count existing rows to generate new user_id
            with open(csv_file, 'r') as f:
                row_count = sum(1 for _ in f)
            user.user_id = f"user_{row_count}"
        
        writer.writerow([user.user_id, user.username, user.love, user.good, user.paid, user.worldneeds, user.genai_summary, user.genai_keywords])
    
    return {"message": "User created successfully!", "summary": user.genai_summary, "keywords": user.genai_keywords}





