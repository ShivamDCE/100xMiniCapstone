#0. Loading libraries
from pydantic import BaseModel #to have data checks in place #Library ensures that the data inputs are in place
from fastapi import FastAPI    #Python library to create APIs
import csv
import os
from datetime import datetime


#1. Initialize FastAPI app
app = FastAPI()

#2. Define the data model
class User(BaseModel):
    username: str
    email: str
    password: str

#3. Building the API endpoints
#3.1. Signup endpoint
@app.post("/signup")
def signup(user: User):
    # Create users.csv if it doesn't exist
    csv_file = "users.csv"
    file_exists = os.path.isfile(csv_file)
    
    # Open the CSV file in append mode
    with open(csv_file, mode='a', newline='') as file:
        fieldnames = ['username', 'email', 'password', 'signup_date']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        # Write header if file is new
        if not file_exists:
            writer.writeheader()
        
        # Write user data
        writer.writerow({
            'username': user.username,
            'email': user.email,
            'password': user.password,  # Note: In a real application, you should hash the password
            'signup_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    return {"message": "User registered successfully", "user": user}


    
