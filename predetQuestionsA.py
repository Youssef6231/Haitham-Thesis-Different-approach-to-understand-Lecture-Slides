import streamlit as st
import os
import json

def display_questions_and_answers(data):
    """
    Display questions in bold and title-like format and predefined answers as normal text.
    """
    for item in data:
        # Ensure both 'question' and 'answer' keys exist
        question = item.get('question', 'No question found.')
        answer = item.get('answer', 'Answer not found.')

        # Display the question in bold and larger font
        st.markdown(f"## **{question}**")  # Header format for larger bold text

        # Display the answer in normal text
        st.write(answer)
        st.markdown("---")

def app():
    """
    Streamlit app for predefined Q&A from JSON files.
    """
    st.title("Lecture Key Questions")

    # Define the directory where JSON files are stored
    saved_answers_dir = "/home/fafnir/Alpha/_Python/Python Current/Haitham Thesis/Saved Answers"
    if not os.path.exists(saved_answers_dir):
        st.error("The directory 'Saved Answers' does not exist.")
        return

    # Get JSON files and remove ".json" from the displayed names
    json_files = [file.replace(".json", "") for file in os.listdir(saved_answers_dir) if file.endswith(".json")]
    if not json_files:
        st.warning("No JSON files found in the 'Saved Answers' directory.")
        return

    # Dropdown to select a JSON file
    selected_file = st.selectbox("Select a JSON file for questions", json_files)

    if selected_file:
        # Read the selected JSON file
        file_path = os.path.join(saved_answers_dir, f"{selected_file}.json")
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            display_questions_and_answers(data)  # Display the questions and answers
        except Exception as e:
            st.error(f"Failed to read {selected_file}.json: {e}")
