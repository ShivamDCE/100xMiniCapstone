#Objective: Give the user the ability to select which skill they want to work on and create a week long daily planner
import pandas as pd

user_complete = pd.read_csv('user_complete.csv',index_col=False)
user="user_0"
skill_list = ['Communication']
role = "Consultant"
def skill_checklist(df,user, role,skill_list):
    tempdf = df[(df["user_id"]==user) & (df["genai_keywords"]==role) & (df["skillsets"].isin(skill_list))]
    return tempdf

print(skill_checklist(user_complete, user, role, skill_list))
    
