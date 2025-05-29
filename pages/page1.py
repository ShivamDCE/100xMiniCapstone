import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Set page config
st.set_page_config(
    page_title="Task List",
    page_icon="📋",
    layout="wide"
)

# Initialize session state for user authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# Function to load users
def load_users():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(current_dir)
        users_path = os.path.join(root_dir, 'users.csv')
        
        if os.path.exists(users_path):
            return pd.read_csv(users_path)
        else:
            st.error(f"users.csv not found at {users_path}")
            return pd.DataFrame(columns=['username', 'email', 'password', 'signup_date'])
    except Exception as e:
        st.error(f"Error loading users: {str(e)}")
        return pd.DataFrame(columns=['username', 'email', 'password', 'signup_date'])

# Function to load task progress
def load_task_progress():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(current_dir)
        progress_path = os.path.join(root_dir, 'task_progress.csv')
        
        if os.path.exists(progress_path):
            return pd.read_csv(progress_path)
        else:
            # Create new progress file with default tasks
            default_tasks = [
                {"username": "", "task_name": "Complete Project Documentation", "completed": False, "submission": ""},
                {"username": "", "task_name": "Review Code Changes", "completed": False, "submission": ""},
                {"username": "", "task_name": "Update Dependencies", "completed": False, "submission": ""},
                {"username": "", "task_name": "Run Final Tests", "completed": False, "submission": ""}
            ]
            df = pd.DataFrame(default_tasks)
            df.to_csv(progress_path, index=False)
            return df
    except Exception as e:
        st.error(f"Error loading task progress: {str(e)}")
        return pd.DataFrame(columns=['username', 'task_name', 'completed', 'submission'])

# Function to save task progress
def save_task_progress(progress_df):
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(current_dir)
        progress_path = os.path.join(root_dir, 'task_progress.csv')
        progress_df.to_csv(progress_path, index=False)
    except Exception as e:
        st.error(f"Error saving task progress: {str(e)}")

# Function to get user tasks
def get_user_tasks(username):
    progress_df = load_task_progress()
    user_tasks = progress_df[progress_df['username'] == username]
    if user_tasks.empty:
        # If user has no tasks, create default tasks
        default_tasks = [
            {"username": username, "task_name": "Complete Project Documentation", "completed": False, "submission": ""},
            {"username": username, "task_name": "Review Code Changes", "completed": False, "submission": ""},
            {"username": username, "task_name": "Update Dependencies", "completed": False, "submission": ""},
            {"username": username, "task_name": "Run Final Tests", "completed": False, "submission": ""}
        ]
        new_tasks = pd.DataFrame(default_tasks)
        progress_df = pd.concat([progress_df, new_tasks], ignore_index=True)
        save_task_progress(progress_df)
        return new_tasks
    return user_tasks

# Function to update task progress
def update_task_progress(username, task_name, completed, submission):
    progress_df = load_task_progress()
    mask = (progress_df['username'] == username) & (progress_df['task_name'] == task_name)
    progress_df.loc[mask, ['completed', 'submission']] = [completed, submission]
    save_task_progress(progress_df)

# Function to authenticate user
def authenticate_user(username, password):
    try:
        users_df = load_users()
        if users_df.empty:
            return None
        
        user = users_df[(users_df['username'] == username) & (users_df['password'] == password)]
        if not user.empty:
            return user.iloc[0].to_dict()
        return None
    except Exception as e:
        st.error(f"Authentication error: {str(e)}")
        return None

# Login form
if not st.session_state.authenticated:
    st.header("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if username and password:
            user = authenticate_user(username, password)
            if user is not None:
                st.session_state.authenticated = True
                st.session_state.current_user = user
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")
        else:
            st.error("Please enter both username and password")
else:
    # Show logout button
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.current_user = None
        st.rerun()

    try:
        # Get user's tasks
        user_tasks = get_user_tasks(st.session_state.current_user['username'])
        
        # Create a container for the progress bar at the top
        progress_container = st.container()

        # Calculate progress
        total_tasks = len(user_tasks)
        completed_tasks = sum(1 for task in user_tasks.itertuples() if task.completed)
        progress = (completed_tasks / total_tasks) * 100

        # Update the progress bar in the container
        with progress_container:
            st.progress(progress / 100)
            st.write(f"Progress: {completed_tasks}/{total_tasks} tasks completed ({progress:.0f}%)")
            st.write(f"Logged in as: {st.session_state.current_user['username']}")

        # Display tasks
        st.header("📋 Task List")

        # Find the first incomplete task
        current_task = None
        for task in user_tasks.itertuples():
            if not task.completed:
                current_task = task
                break

        if current_task is not None:
            # Display current task
            st.write(f"**Current Task: {current_task.task_name}**")
            
            # Add text input and submit button
            submission = st.text_input("Enter your completion details:", key=f"input_{current_task.task_name}")
            col3, col4 = st.columns([0.1, 0.9])
            with col3:
                if st.button("Submit", key=f"submit_{current_task.task_name}"):
                    if submission.strip():
                        update_task_progress(
                            st.session_state.current_user['username'],
                            current_task.task_name,
                            True,
                            submission
                        )
                        st.success("Task completed!")
                        st.rerun()
                    else:
                        st.error("Please provide completion details before submitting.")

        # Show completed tasks
        st.write("---")
        st.subheader("Your Completed Tasks")
        for task in user_tasks.itertuples():
            if task.completed:
                st.write(f"**Task: {task.task_name}**")
                st.info(f"**Completion Details:** {task.submission}")
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.error("Please try logging out and logging in again.")
