import os
import json
import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from serpapi import GoogleSearch

VECTORSTORE_PATH = "/home/fafnir/Alpha/_Python/Python Current/Haitham Thesis/vectorstore.faiss"
SAVED_JSON_DIR = "/home/fafnir/Alpha/_Python/Python Current/Haitham Thesis/Saved Answers"

# Ensure the Saved Answers directory exists
if not os.path.exists(SAVED_JSON_DIR):
    os.makedirs(SAVED_JSON_DIR)

def load_questions(file_path):
    """
    Load questions from a JSON file.
    """
    with open(file_path, "r") as f:
        return json.load(f)

def get_conversation_chain():
    """
    Create a conversational retrieval chain using LangChain.
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

def search_images(question, num_images=3):
    """
    Search for high-quality images using SerpAPI (Google Image Search).
    """
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        st.error("SERPAPI API key not set. Please add it to your environment variables.")
        return []

    search = GoogleSearch({
        "q": question,
        "tbm": "isch",  # Image search
        "num": num_images,
        "api_key": api_key,
        "tbs": "isz:l"  # Filter for large images
    })
    results = search.get_dict()

    # Extract high-quality image URLs
    images = [result["original"] for result in results.get("images_results", [])[:num_images] if "original" in result]
    return images

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

def display_questions_and_answers(data, conversation_chain):
    """
    Display questions and answers, along with the "Answer by Image" and "Explain Answer" buttons.
    """
    for item in data:
        question = item["question"]
        st.markdown(f"### {question}")  # Display question in a larger format

        answer = ""
        if conversation_chain:
            try:
                answer = conversation_chain.run(question)
                st.markdown(answer)
            except Exception as e:
                st.error(f"Error generating answer: {e}")
        
        # Add a button to search for images
        if st.button(f"Answer by Image: {question}", key=f"image_search_{question}"):
            images = search_images(question)
            if images:
                for img_url in images:
                    st.image(img_url, use_container_width=True)  # Fixed the warning
            else:
                st.warning("No images found.")

        # Add a button to explain the answer
        if st.button(f"Explain Answer: {question}", key=f"explain_{question}"):
            if answer:
                explanation = explain_answer(answer)
                st.markdown(f"**Explanation:** {explanation}")
            else:
                st.warning("Answer not found to explain.")

        st.markdown("---")

def app():
    """
    Streamlit app for different answers.
    """
    st.title("Different Answers")

    # Dropdown to select a JSON file
    json_files = [f for f in os.listdir(SAVED_JSON_DIR) if f.endswith(".json")]
    selected_file = st.selectbox("Select a Lecture", [f.replace(".json", "") for f in json_files])

    # Load selected file
    if selected_file:
        file_path = os.path.join(SAVED_JSON_DIR, f"{selected_file}.json")
        data = load_questions(file_path)
        
        # Initialize conversation chain
        conversation_chain = get_conversation_chain()
        if conversation_chain:
            display_questions_and_answers(data, conversation_chain)
