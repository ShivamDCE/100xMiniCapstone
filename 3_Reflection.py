'''
Objective: Create a roadmap for the user based on the skillset selected!
#Steps
1. Use the dataset stored in the ikigai_users dataset and select the keywords
2. For each keyword, get a roadmap + list of key skills to work on
'''

#0. Load Libraries ------------
import pandas as pd
from groq import Groq
import os
import time
from dotenv import load_dotenv
import ast  # For safely evaluating string representation of lists
# Load environment variables
load_dotenv()

#1. Load the ikigai_users.csv dataset + filter the user_id, user_name & keywords -> Expand the keywords
user_reflection = pd.read_csv("ikigai_users.csv")
## Selecting relevant columns
temp_df = user_reflection[['user_id','username','genai_keywords']]

# Clean and expand the keywords
expanded_rows = []
for _, row in temp_df.iterrows():
    # Remove brackets and quotes, then split by comma
    keywords = row['genai_keywords'].strip('[]').replace("'", "").split(',')
    # Clean each keyword
    keywords = [k.strip() for k in keywords]
    # Create a row for each keyword
    for keyword in keywords:
        expanded_rows.append({
            'user_id': row['user_id'],
            'username': row['username'],
            'genai_keywords': keyword
        })

# Create new dataframe with expanded rows
expanded_df = pd.DataFrame(expanded_rows)

#2. Calling LLMs to give roadmap to each skill
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_roadmap(role):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful career counsellor. Return your response only in 3-4 lines"
                },
                {
                    "role": "user",
                    "content": f"Give me a roadmap to become {role}?"
                }
            ],
            model="llama3-70b-8192"
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error processing {role}: {str(e)}")
        return "Error generating roadmap"

def get_skillset(role):
    prompt = f"""Based on the following user profile and desired role:
    Desired Role: {role}
    
    1. Generate the required skillset for the role
    2. Format the response as a Python list, e.g. ["skill1", "skill2", ...]
    """
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user",
                    "content": f"Give me a the skillsets to achieve the goal of becoming a {role}?"
                }
            ],
            model="llama3-70b-8192"
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error processing {role}: {str(e)}")
        return "Error generating skillset"

# Add delay between API calls to avoid rate limiting
def process_roadmaps(df):
    roadmaps = []
    for keyword in df['genai_keywords']:
        roadmap = get_roadmap(keyword)
        roadmaps.append(roadmap)
        time.sleep(1)  # Add 1 second delay between calls
    return roadmaps

def process_skillsets(df):
    skillsets = []
    for keyword in df['genai_keywords']:
        skillset = get_skillset(keyword)
        skillsets.append(skillset)
        time.sleep(1)  # Add 1 second delay between calls
    return skillsets

# Apply the functions to get roadmaps and skillsets
print("Generating roadmaps...")
expanded_df['roadmap'] = process_roadmaps(expanded_df)
print("Generating skillsets...")
expanded_df['skillsets'] = process_skillsets(expanded_df)

# Extract the Python list from skillsets
def extract_list(skillset_str):
    try:
        # Find the first '[' and last ']' in the string
        start = skillset_str.find('[')
        end = skillset_str.rfind(']') + 1
        if start != -1 and end != 0:
            list_str = skillset_str[start:end]
            # Safely evaluate the string as a Python list
            return ast.literal_eval(list_str)
        return []
    except:
        return []

# Apply the extraction function
expanded_df['skillsets'] = expanded_df['skillsets'].apply(extract_list)

# Create final dataframe with individual skills
final_rows = []
for _, row in expanded_df.iterrows():
    # Since skillsets is already a list, we can iterate directly
    for skill in row['skillsets']:
        final_rows.append({
            'user_id': row['user_id'],
            'username': row['username'],
            'genai_keywords': row['genai_keywords'],
            'roadmap': row['roadmap'],
            'skillsets': skill
        })

# Create new dataframe with expanded rows
final_df = pd.DataFrame(final_rows)

def get_dailytasks(skill):
    prompt = f"""Based on the following skillset:
    Desired Role: {skill}
    
    1. Provide a Python list as a response e.g. ["Day1: Read", "Day2: Write", ...]
    2. In each element of the list start with "Day"
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user",
                    "content": f"Give me a daily action plan to learn {skill}?"
                }
            ],
            model="llama3-70b-8192"
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error processing {skill}: {str(e)}")
        return "Error generating roadmap"
    
def process_dailytasks(df):
    tasks = []
    for keyword in df['skillsets']:
        task = get_dailytasks(keyword)
        tasks.append(task)
        time.sleep(1)  # Add 1 second delay between calls
    return tasks

print("Generating daily tasks...")
final_df['dailytasks'] = process_dailytasks(final_df)
final_df.to_csv("interim_temp.csv")
final_df['dailytasks'] = final_df['dailytasks'].apply(extract_list)

complete_rows = []
for _, row in final_df.iterrows():
    # Since dailytasks is already a list, we can iterate directly
    for task in row['dailytasks']:
        complete_rows.append({
            'user_id': row['user_id'],
            'username': row['username'],
            'genai_keywords': row['genai_keywords'],
            'roadmap': row['roadmap'],
            'skillsets': row['skillsets'],
            'dailytasks': task
        })

# Create new dataframe with expanded rows
complete_df = pd.DataFrame(complete_rows)

# Save the results
complete_df.to_csv('user_complete.csv', index=False)
print("\nResults saved to user_complete.csv")
print("\nSample of results:")
print(complete_df.head())

