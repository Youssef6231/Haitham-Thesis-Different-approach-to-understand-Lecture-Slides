import os
import json
import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

VECTORSTORE_PATH = "/home/fafnir/Alpha/_Python/Python Current/Haitham Thesis/vectorstore.faiss"
HISTORY_DIR = "/home/fafnir/Alpha/_Python/Python Current/Haitham Thesis/History"
HISTORY_FILE = os.path.join(HISTORY_DIR, "askLectures.json")

# Ensure the history directory and file exist
if not os.path.exists(HISTORY_DIR):
    os.makedirs(HISTORY_DIR)
if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "w") as f:
        json.dump([], f)  # Initialize with an empty list

def load_history():
    """
    Load chat history from the JSON file. If the file is empty, return an empty list.
    """
    try:
        with open(HISTORY_FILE, "r") as f:
            content = f.read().strip()
            if not content:  # Handle empty file
                return []
            return json.loads(content)
    except json.JSONDecodeError:
        return []

def save_to_history(question, answer):
    """
    Save a question-answer pair to the JSON file.
    """
    history = load_history()
    history.append({"question": question, "answer": answer})
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def get_conversation_chain():
    """
    Create a conversational retrieval chain using LangChain.
    Ensure the FAISS vectorstore is loaded safely.
    """
    if not os.path.exists(VECTORSTORE_PATH):
        st.error("Embeddings not found. Please ensure uploadEmb.py processed the PDFs.")
        return None

    try:
        vectorstore = FAISS.load_local(
            VECTORSTORE_PATH,
            OpenAIEmbeddings(),
            allow_dangerous_deserialization=True
        )
    except Exception as e:
        st.error(f"Failed to load embeddings: {e}")
        return None

    llm = ChatOpenAI(temperature=0)
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )

def explain_answer(answer):
    """
    Generate a detailed explanation of the answer using OpenAI's GPT model.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("OpenAI API key not set. Please add it to your environment variables.")
        return "OpenAI API key is missing."

    # Initialize the OpenAI GPT model
    llm = ChatOpenAI(api_key=api_key, temperature=0.7)

    prompt = f"Explain this concept in detail with examples: {answer}"
    try:
        explanation = llm.predict(prompt)
        return explanation
    except Exception as e:
        return f"Error generating explanation: {e}"

def display_history():
    """
    Display the chat history below the asking bar, with the most recent interactions on top.
    """
    st.markdown("### Chat History")
    history = load_history()
    if history:
        # Display most recent interactions first
        for interaction in reversed(history):
            st.markdown(f"**You:** {interaction['question']}")
            st.markdown(f"**Lecture:** {interaction['answer']}")
            st.markdown("---")
    else:
        st.write("No chat history yet.")

def app():
    """
    Streamlit app to chat with lectures and save the history.
    """
    st.title("Ask The Lectures")

    # Initialize conversation chain
    conversation_chain = get_conversation_chain()
    if conversation_chain is None:
        return

    # Input for user question
    user_question = st.text_input("Ask your question about the lectures:")

    if user_question:
        try:
            # Generate answer using embeddings
            answer = conversation_chain.run(user_question)

            # Display the interaction
            st.markdown(f"**You:** {user_question}")
            st.markdown(f"**Lecture:** {answer}")
            st.markdown("---")

            # Save the interaction to history
            save_to_history(user_question, answer)

            # Add the "Explain Answer" button only if the answer exists
            if answer:
                if st.button(f"Explain Answer: {user_question}", key=f"explain_{user_question}"):
                    explanation = explain_answer(answer)
                    st.markdown(f"**Explanation:** {explanation}")
        except Exception as e:
            st.error(f"Error generating answer: {e}")

    # Display chat history under the input box
    display_history()
