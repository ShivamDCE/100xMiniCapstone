import streamlit as st
import requests
import json
from typing import Dict, List
import pandas as pd
from datetime import datetime, timedelta

# Configure the page
st.set_page_config(
    page_title="Ikigai Upskilling Track",
    page_icon="🎯",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        margin-top: 1rem;
    }
    .role-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .skill-list {
        margin: 0.5rem 0;
    }
    .task-item {
        padding: 0.5rem;
        margin: 0.5rem 0;
        border-radius: 0.3rem;
        background-color: #f8f9fa;
    }
    .completed-task {
        text-decoration: line-through;
        color: #6c757d;
    }
    </style>
    """, unsafe_allow_html=True)

# Title and description
st.title("🎯 Ikigai Upskilling Track")
st.markdown("""
    Get a personalized upskilling track based on your Ikigai profile. 
    Select your desired role from the options below to see the recommended path.
""")

# Initialize session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'available_roles' not in st.session_state:
    st.session_state.available_roles = []
if 'selected_role' not in st.session_state:
    st.session_state.selected_role = None
if 'upskilling_track' not in st.session_state:
    st.session_state.upskilling_track = None
if 'daily_tasks' not in st.session_state:
    st.session_state.daily_tasks = []
if 'completed_tasks' not in st.session_state:
    st.session_state.completed_tasks = set()

# User ID input
user_id = st.text_input("Enter your User ID", value=st.session_state.user_id or "")

if user_id:
    st.session_state.user_id = user_id
    
    # Fetch available roles
    try:
        response = requests.get(f"http://localhost:8001/get_user_roles/{user_id}")
        if response.status_code == 200:
            data = response.json()
            st.session_state.available_roles = data.get("available_roles", [])
            
            if st.session_state.available_roles:
                st.success(f"Found {len(st.session_state.available_roles)} potential roles for you!")
                
                # Role selection
                selected_role = st.selectbox(
                    "Select your desired role",
                    options=st.session_state.available_roles,
                    index=0 if st.session_state.available_roles else None
                )
                
                if selected_role:
                    st.session_state.selected_role = selected_role
                    
                    # Get upskilling track
                    if st.button("Generate Upskilling Track"):
                        with st.spinner("Generating your personalized upskilling track..."):
                            try:
                                response = requests.post(
                                    "http://localhost:8001/get_upskilling_track",
                                    json={"user_id": user_id, "role": selected_role}
                                )
                                
                                if response.status_code == 200:
                                    data = response.json()
                                    st.session_state.upskilling_track = data.get("upskilling_track")
                                    # Reset tasks when new track is generated
                                    st.session_state.daily_tasks = []
                                    st.session_state.completed_tasks = set()
                                else:
                                    st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                            except requests.exceptions.ConnectionError:
                                st.error("Could not connect to the upskilling service. Please make sure it's running on port 8001.")
            else:
                st.warning("No roles found for this user ID. Please check your user ID and try again.")
        else:
            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the upskilling service. Please make sure it's running on port 8001.")

# Display upskilling track
if st.session_state.upskilling_track:
    st.markdown("---")
    st.markdown(f"## 📚 Upskilling Track for {st.session_state.selected_role}")
    
    # Technical Skills
    st.markdown("### 🔧 Technical Skills")
    tech_skills = st.session_state.upskilling_track.get("technical_skills", [])
    for skill in tech_skills:
        st.markdown(f"- {skill}")
    
    # Soft Skills
    st.markdown("### 🤝 Soft Skills")
    soft_skills = st.session_state.upskilling_track.get("soft_skills", [])
    for skill in soft_skills:
        st.markdown(f"- {skill}")
    
    # Learning Resources
    st.markdown("### 📖 Learning Resources")
    resources = st.session_state.upskilling_track.get("learning_resources", [])
    for resource in resources:
        st.markdown(f"- {resource}")
    
    # Timeline
    st.markdown("### ⏳ Timeline")
    st.markdown(st.session_state.upskilling_track.get("timeline", "Not specified"))
    
    # Milestones and Daily Tasks
    st.markdown("### 🎯 Key Milestones")
    milestones = st.session_state.upskilling_track.get("milestones", [])
    
    # Convert milestones to daily tasks if not already done
    if not st.session_state.daily_tasks and milestones:
        if st.button("Generate Daily Tasks"):
            daily_tasks = []
            for milestone in milestones:
                # Generate 3-5 daily tasks for each milestone
                num_tasks = 3  # You can adjust this number
                for i in range(num_tasks):
                    task = {
                        'milestone': milestone,
                        'task': f"Task {i+1} for {milestone}",
                        'date': (datetime.now() + timedelta(days=len(daily_tasks))).strftime('%Y-%m-%d'),
                        'completed': False
                    }
                    daily_tasks.append(task)
            st.session_state.daily_tasks = daily_tasks
    
    # Display daily tasks
    if st.session_state.daily_tasks:
        st.markdown("### 📅 Daily Tasks")
        
        # Task completion tracking
        for task in st.session_state.daily_tasks:
            task_id = f"{task['date']}_{task['task']}"
            col1, col2 = st.columns([0.1, 0.9])
            with col1:
                if st.checkbox("", key=task_id, value=task_id in st.session_state.completed_tasks):
                    st.session_state.completed_tasks.add(task_id)
                else:
                    st.session_state.completed_tasks.discard(task_id)
            with col2:
                task_class = "completed-task" if task_id in st.session_state.completed_tasks else ""
                st.markdown(f"""
                    <div class="task-item {task_class}">
                        <strong>{task['date']}</strong><br>
                        {task['task']}<br>
                        <small>Milestone: {task['milestone']}</small>
                    </div>
                """, unsafe_allow_html=True)
        
        # Progress tracking
        total_tasks = len(st.session_state.daily_tasks)
        completed_tasks = len(st.session_state.completed_tasks)
        progress = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
        
        st.markdown(f"""
            ### Progress Tracking
            <div style="background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem;">
                <p>Completed: {completed_tasks} / {total_tasks} tasks</p>
                <div style="background-color: #e9ecef; height: 20px; border-radius: 10px;">
                    <div style="background-color: #28a745; width: {progress}%; height: 100%; border-radius: 10px;"></div>
                </div>
                <p>{progress:.1f}% Complete</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Download options
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Download Upskilling Track"):
            # Convert to DataFrame for better formatting
            df = pd.DataFrame({
                "Category": ["Technical Skills", "Soft Skills", "Learning Resources", "Timeline", "Milestones"],
                "Details": [
                    "\n".join(tech_skills),
                    "\n".join(soft_skills),
                    "\n".join(resources),
                    st.session_state.upskilling_track.get("timeline", ""),
                    "\n".join(f"{i}. {m}" for i, m in enumerate(milestones, 1))
                ]
            })
            
            # Convert to CSV
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download as CSV",
                data=csv,
                file_name=f"upskilling_track_{st.session_state.selected_role.lower().replace(' ', '_')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.session_state.daily_tasks:
            if st.button("Download Daily Tasks"):
                tasks_df = pd.DataFrame(st.session_state.daily_tasks)
                tasks_csv = tasks_df.to_csv(index=False)
                st.download_button(
                    label="Download Tasks as CSV",
                    data=tasks_csv,
                    file_name=f"daily_tasks_{st.session_state.selected_role.lower().replace(' ', '_')}.csv",
                    mime="text/csv"
                )

# Footer
st.markdown("---")
st.markdown("Made with ❤️ by Ikigai Career Advisor") 