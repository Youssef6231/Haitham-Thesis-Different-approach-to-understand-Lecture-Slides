import os
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
import streamlit as st

# Load environment variables from .env file
load_dotenv()

VECTORSTORE_PATH = "/home/fafnir/Alpha/_Python/Python Current/Haitham Thesis/vectorstore.faiss"

def get_pdf_text(pdf_dir):
    text = ""
    for file in os.listdir(pdf_dir):
        if file.endswith(".pdf"):
            pdf_reader = PdfReader(os.path.join(pdf_dir, file))
            for page in pdf_reader.pages:
                text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    return text_splitter.split_text(text)

def process_pdfs():
    """
    Process all PDFs in the `Fixed Pdfs` folder and save the embeddings to a file.
    """
    pdf_dir = "/home/fafnir/Alpha/_Python/Python Current/Haitham Thesis/Fixed Pdfs"

    # Ensure OpenAI API key is loaded
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")

    # Extract text from PDFs
    st.info("Processing PDFs...")
    text = get_pdf_text(pdf_dir)
    if not text:
        st.warning("No text found in the provided PDFs.")
        return

    # Split text into chunks
    text_chunks = get_text_chunks(text)

    # Create embeddings
    st.info("Generating embeddings...")
    embeddings = OpenAIEmbeddings(openai_api_key=api_key)
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)

    # Save vector store to file
    vectorstore.save_local(VECTORSTORE_PATH)
    st.success("Embeddings uploaded successfully!")

if __name__ == "__main__":
    process_pdfs()
