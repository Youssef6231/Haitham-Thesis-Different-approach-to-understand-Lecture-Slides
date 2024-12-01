import streamlit as st
from streamlit_option_menu import option_menu
import account
import predetQuestionsA
import predetQuestionsB
import askLectures
from uploadEmb import process_pdfs

# Ensure embeddings are processed automatically when main.py is run
def initialize_embeddings():
    try:
        process_pdfs()
    except Exception as e:
        st.error(f"Failed to process embeddings: {e}")

class MultiApp:

    def __init__(self):
        self.apps = []

    def add_app(self, title, func, icon):
        self.apps.append({
            "title": title,
            "function": func,
            "icon": icon
        })

    def run(self):
        with st.sidebar:
            selected_app = option_menu(
                menu_title='Ask any question',
                options=[app["title"] for app in self.apps],
                icons=[app["icon"] for app in self.apps],
                menu_icon='chat-text-fill',
                default_index=0,
                styles={
                    "container": {"padding": "5!important", "background-color": 'black'},
                    "icon": {"color": "white", "font-size": "23px"},
                    "nav-link": {"color": "white", "font-size": "20px", "text-align": "left", "margin": "0px", "--hover-color": "blue"},
                    "nav-link-selected": {"background-color": "#02ab21"},
                }
            )

        for app in self.apps:
            if app["title"] == selected_app:
                app["function"]()

if __name__ == "__main__":
    st.info("Initializing the application... Please wait.")
    initialize_embeddings()  # Run uploadEmb.py automatically
    app = MultiApp()
    app.add_app("Lecture Key Questions", predetQuestionsA.app, "mortarboard")
    app.add_app("Different Answers", predetQuestionsB.app, "arrow-clockwise")
    app.add_app("Ask The Lectures", askLectures.app, "chat-dots")
    app.run()
