import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Set page config
st.set_page_config(page_title="User Authentication", page_icon="🔐")

# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def check_credentials(username, password):
    try:
        # Read the CSV file
        df = pd.read_csv('users.csv')
        # Check if username and password match
        user = df[(df['username'] == username) & (df['password'] == password)]
        return not user.empty
    except FileNotFoundError:
        return False

def signup_user(username, email, password):
    try:
        # Make request to FastAPI signup endpoint
        response = requests.post(
            "http://localhost:8000/signup",
            json={
                "username": username,
                "email": email,
                "password": password
            }
        )
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the server. Make sure the FastAPI server is running.")
        return False

# Main app
st.title("🔐 User Authentication")

# Create tabs for Login and Signup
tab1, tab2 = st.tabs(["Login", "Signup"])

with tab1:
    st.header("Login")
    with st.form("login_form"):
        login_username = st.text_input("Username")
        login_password = st.text_input("Password", type="password")
        login_submitted = st.form_submit_button("Login")
        
        if login_submitted:
            if check_credentials(login_username, login_password):
                st.session_state.authenticated = True
                st.success("Login successful!")
            else:
                st.error("Invalid username or password")

with tab2:
    st.header("Signup")
    with st.form("signup_form"):
        signup_username = st.text_input("Choose a username")
        signup_email = st.text_input("Enter your email")
        signup_password = st.text_input("Choose a password", type="password")
        confirm_password = st.text_input("Confirm password", type="password")
        signup_submitted = st.form_submit_button("Signup")
        
        if signup_submitted:
            if signup_password != confirm_password:
                st.error("Passwords do not match!")
            elif not signup_username or not signup_email or not signup_password:
                st.error("Please fill in all fields!")
            else:
                if signup_user(signup_username, signup_email, signup_password):
                    st.success("Signup successful! You can now login.")
                else:
                    st.error("Signup failed. Please try again.")

# Display authentication status
if st.session_state.authenticated:
    st.sidebar.success("Logged in successfully!")
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.experimental_rerun() 