import pandas as pd
import streamlit as st
import ast

# Set page config
st.set_page_config(
    page_title="GenAI Keywords & Skillsets Viewer",
    page_icon="🔍",
    layout="wide"
)

# Add title and description
st.title("🔍 GenAI Keywords & Skillsets Viewer")
st.markdown("Select a keyword and skillset from the dropdown menus below.")

# Load the data
@st.cache_data
def load_data():
    return pd.read_csv('user_complete.csv')

def parse_tasks(tasks_str):
    """
    Safely parse the tasks string into a list.
    Handles string representation of lists and simple strings.
    """
    try:
        if pd.isna(tasks_str) or not isinstance(tasks_str, str):
            return []

        tasks_str = tasks_str.strip()

        # Attempt to parse as a list using ast.literal_eval
        if tasks_str.startswith('[') and tasks_str.endswith(']'):
            try:
                return ast.literal_eval(tasks_str)
            except:
                # If ast.literal_eval fails, treat as a single string if not empty
                if tasks_str:
                     # Remove potential surrounding quotes if it looks like a quoted list string
                     if tasks_str.startswith("'") and tasks_str.endswith("'"): tasks_str = tasks_str[1:-1]
                     if tasks_str.startswith('"') and tasks_str.endswith('"'): tasks_str = tasks_str[1:-1]
                     # Re-attempt literal_eval in case quotes were the issue
                     try:
                         return ast.literal_eval(tasks_str)
                     except:
                        return [tasks_str] if tasks_str else []
                else:
                    return []
        elif tasks_str:
             # If it doesn't look like a list string, treat as a single task
            return [tasks_str]
        else:
             return []

    except Exception as e:
        # In case of any unexpected error during parsing
        st.warning(f"Could not parse task entry: {tasks_str}. Error: {e}")
        return []

# Load data
user_complete = load_data()

# Ensure the necessary columns exist
required_columns = ['genai_keywords', 'skillsets', 'dailytasks', 'user_id'] # Added dailytasks
if not all(col in user_complete.columns for col in required_columns):
    missing = [col for col in required_columns if col not in user_complete.columns]
    st.error(f"Missing required columns in CSV: {', '.join(missing)}")
else:
    # Display the first dropdown for keyword selection
    st.markdown("### Select GenAI Keyword")
    available_keywords = sorted(user_complete['genai_keywords'].unique())
    selected_keyword = st.selectbox(
        "Choose a GenAI keyword",
        options=available_keywords,
        label_visibility="collapsed",
        index=None if not available_keywords else 0, # Allow no initial selection if list is empty
        placeholder="Select a keyword"
    )

    # Display the second dropdown for skillset selection, dependent on keyword selection
    if selected_keyword:
        st.markdown(f"### Select Skillset for '{selected_keyword}'")
        
        # Filter data by the selected keyword
        filtered_by_keyword = user_complete[user_complete['genai_keywords'] == selected_keyword]
        
        # Get unique skillsets for the selected keyword
        related_skillsets = sorted(filtered_by_keyword['skillsets'].unique())
        
        if related_skillsets:
            selected_skillset = st.selectbox(
                "Choose a skillset",
                options=related_skillsets,
                label_visibility="collapsed",
                 index=None if not related_skillsets else 0, # Allow no initial selection if list is empty
                 placeholder="Select a skillset"
            )
            
            if selected_skillset:
                st.subheader(f"Daily Tasks for '{selected_keyword}' - '{selected_skillset}'")
                
                # Filter data by the selected keyword AND skillset
                filtered_by_keyword_skillset = filtered_by_keyword[filtered_by_keyword['skillsets'] == selected_skillset]
                
                all_tasks = []
                if 'dailytasks' in filtered_by_keyword_skillset.columns:
                    # Iterate through the filtered data to collect all tasks for this combination
                    for _, row in filtered_by_keyword_skillset.iterrows():
                        tasks_list = parse_tasks(row.get('dailytasks')) # Use .get for safety
                        if tasks_list:
                            all_tasks.extend(tasks_list)
                
                if all_tasks:
                    # Remove duplicates while preserving order
                    unique_tasks = list(dict.fromkeys(all_tasks))
                    
                    st.write("Check off tasks as you complete them:")
                    for task in unique_tasks:
                         # Ensure task is a string before displaying
                        if isinstance(task, str):
                            st.checkbox(task)
                        else:
                             # Handle unexpected task formats if necessary
                             st.warning(f"Skipping unexpected task format: {task}")
                             st.json(task) # Or display it in a way that helps debugging

                else:
                    st.info(f"No daily tasks found for the keyword '{selected_keyword}' and skillset '{selected_skillset}'.")

        else:
            st.info(f"No skillsets found for the keyword '{selected_keyword}'.")
    else:
        st.info("Please select a keyword from the dropdown above.")

# Sidebar remains empty as per previous instructions
# Add helpful information (optional, sidebar is empty now)
# st.sidebar.markdown("---")
# st.sidebar.markdown("### Instructions")
# st.sidebar.markdown("1. Select a keyword from the dropdown.")
# st.sidebar.markdown("2. Select a skillset from the second dropdown that appears.")
# st.sidebar.markdown("3. View content related to the selected combination.")
