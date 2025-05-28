import streamlit as st

# Set page title
st.title("Task1: Fill the Ikigai")

# Create text input fields
input1 = st.text_input("What you love:", "")
input2 = st.text_input("What you are good at:", "")
input3 = st.text_input("What the world needs:", "")
input4 = st.text_input("What you can be paid for:", "")

# Display the input text
if input1 or input2 or input3 or input4:
    st.write("Your Ikigai inputs:")
    if input1:
        st.write("What you love:", input1)
    if input2:
        st.write("What you are good at:", input2)
    if input3:
        st.write("What the world needs:", input3)
    if input4:
        st.write("What you can be paid for:", input4)
