import streamlit as st
import requests
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'answers' not in st.session_state:
    st.session_state.answers = {
        'user_id': None,
        'username': None,
        'love': None,
        'good': None,
        'paid': None,
        'worldneeds': None
    }
if 'show_results' not in st.session_state:
    st.session_state.show_results = False

# Set page config
st.set_page_config(
    page_title="Ikigai Career Finder",
    page_icon="🎯",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stTextInput > div > div > input {
        font-size: 1.1rem;
    }
    .stButton > button {
        width: 100%;
        font-size: 1.1rem;
        background-color: #4CAF50;
        color: white;
        padding: 0.5rem 1rem;
        border: none;
        border-radius: 5px;
    }
    .stButton > button:hover {
        background-color: #45a049;
    }
    .progress-container {
        margin-bottom: 2rem;
    }
    .step-indicator {
        display: flex;
        justify-content: space-between;
        margin-bottom: 1rem;
    }
    .step {
        text-align: center;
        flex: 1;
    }
    .step.active {
        color: #4CAF50;
        font-weight: bold;
    }
    .step.completed {
        color: #45a049;
    }
    </style>
    """, unsafe_allow_html=True)

# Title and description
st.title("🎯 Ikigai Career Finder")
st.markdown("""
    Discover your perfect career path by finding the intersection of what you love, what you're good at,
    what you can be paid for, and what the world needs.
""")

# Progress indicator
st.markdown("""
    <div class="progress-container">
        <div class="step-indicator">
            <div class="step {}">1. User Info</div>
            <div class="step {}">2. What You Love</div>
            <div class="step {}">3. What You're Good At</div>
            <div class="step {}">4. What You Can Be Paid For</div>
            <div class="step {}">5. What The World Needs</div>
        </div>
    </div>
""".format(
    "active" if st.session_state.step == 1 else "completed" if st.session_state.step > 1 else "",
    "active" if st.session_state.step == 2 else "completed" if st.session_state.step > 2 else "",
    "active" if st.session_state.step == 3 else "completed" if st.session_state.step > 3 else "",
    "active" if st.session_state.step == 4 else "completed" if st.session_state.step > 4 else "",
    "active" if st.session_state.step == 5 else "completed" if st.session_state.step > 5 else ""
), unsafe_allow_html=True)

def reset_session():
    st.session_state.step = 1
    st.session_state.answers = {
        'user_id': None,
        'username': None,
        'love': None,
        'good': None,
        'paid': None,
        'worldneeds': None
    }
    st.session_state.show_results = False

# Step 1: User Information
if st.session_state.step == 1 and not st.session_state.show_results:
    st.subheader("Step 1: Tell us about yourself")
    col1, col2 = st.columns(2)
    with col1:
        user_id = st.number_input("User ID", min_value=1, step=1)
    with col2:
        username = st.text_input("Username")
    
    if st.button("Next"):
        if user_id and username:
            st.session_state.answers['user_id'] = user_id
            st.session_state.answers['username'] = username
            st.session_state.step = 2
            st.rerun()
        else:
            st.error("Please fill in all fields!")

# Step 2: What You Love
elif st.session_state.step == 2 and not st.session_state.show_results:
    st.subheader("Step 2: What do you love? 💖")
    love = st.text_area("", placeholder="Describe what you're passionate about...")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back"):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if st.button("Next"):
            if love:
                st.session_state.answers['love'] = love
                st.session_state.step = 3
                st.rerun()
            else:
                st.error("Please fill in what you love!")

# Step 3: What You're Good At
elif st.session_state.step == 3 and not st.session_state.show_results:
    st.subheader("Step 3: What are you good at? ⭐")
    good = st.text_area("", placeholder="Describe your skills and talents...")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back"):
            st.session_state.step = 2
            st.rerun()
    with col2:
        if st.button("Next"):
            if good:
                st.session_state.answers['good'] = good
                st.session_state.step = 4
                st.rerun()
            else:
                st.error("Please fill in what you're good at!")

# Step 4: What You Can Be Paid For
elif st.session_state.step == 4 and not st.session_state.show_results:
    st.subheader("Step 4: What can you be paid for? 💰")
    paid = st.text_area("", placeholder="Describe what you can offer professionally...")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back"):
            st.session_state.step = 3
            st.rerun()
    with col2:
        if st.button("Next"):
            if paid:
                st.session_state.answers['paid'] = paid
                st.session_state.step = 5
                st.rerun()
            else:
                st.error("Please fill in what you can be paid for!")

# Step 5: What The World Needs
elif st.session_state.step == 5 and not st.session_state.show_results:
    st.subheader("Step 5: What does the world need? 🌍")
    worldneeds = st.text_area("", placeholder="Describe what problems you want to solve...")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back"):
            st.session_state.step = 4
            st.rerun()
    with col2:
        if st.button("Find My Ikigai"):
            if worldneeds:
                st.session_state.answers['worldneeds'] = worldneeds
                try:
                    # Prepare the data
                    data = {
                        "user_id": st.session_state.answers['user_id'],
                        "username": st.session_state.answers['username'],
                        "love": st.session_state.answers['love'],
                        "good": st.session_state.answers['good'],
                        "paid": st.session_state.answers['paid'],
                        "worldneeds": worldneeds,
                        "genai_summary": "",
                        "genai_keywords": ""
                    }

                    # Make API request
                    response = requests.post(
                        "http://localhost:8000/create_ikigai",
                        json=data
                    )

                    if response.status_code == 200:
                        st.session_state.result = response.json()
                        st.session_state.show_results = True
                        st.rerun()
                    else:
                        st.error("Error: Could not process your request. Please try again.")
                        
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
            else:
                st.error("Please fill in what the world needs!")

# Show Results
if st.session_state.show_results:
    st.success("✨ Your Ikigai Analysis is Ready!")
    
    # Create two columns for results
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📝 Career Summary")
        st.write(st.session_state.result["summary"])
    
    with col2:
        st.markdown("### 🏷️ Career Keywords")
        keywords = st.session_state.result["keywords"]
        if isinstance(keywords, str):
            try:
                keywords = eval(keywords)
            except:
                keywords = [keywords]
        
        # Display keywords as tags
        for keyword in keywords:
            st.markdown(f"<span style='background-color: #e0e0e0; padding: 5px 10px; border-radius: 15px; margin: 5px; display: inline-block;'>{keyword}</span>", unsafe_allow_html=True)
    
    # Add a download button for the results
    st.download_button(
        label="📥 Download Results",
        data=json.dumps(st.session_state.result, indent=2),
        file_name="ikigai_analysis.json",
        mime="application/json"
    )
    
    # Add a button to start over
    if st.button("Start Over"):
        reset_session()
        st.rerun()

# Add footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center'>
        <p>Built with ❤️ using Streamlit and FastAPI</p>
    </div>
""", unsafe_allow_html=True) 