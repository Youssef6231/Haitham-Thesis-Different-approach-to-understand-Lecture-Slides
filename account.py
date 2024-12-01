import streamlit as st

def app():
    st.title("Welcome to :violet[the Kingdom] :sunglasses:")

    # Initialize session state variables for user login
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # Define login function
    def login(username, password):
        # Replace this with your own user validation logic if needed
        if username == "admin" and password == "password":
            st.session_state.username = username
            st.session_state.logged_in = True
            st.success("Login successful!")
        else:
            st.warning("Invalid username or password.")

    # Define logout function
    def logout():
        st.session_state.username = ""
        st.session_state.logged_in = False
        st.info("You have been logged out.")

    # Display login/logout interface
    if not st.session_state.logged_in:
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            login(username, password)
    else:
        st.subheader(f"Welcome, {st.session_state.username}!")
        if st.button("Logout"):
            logout()
