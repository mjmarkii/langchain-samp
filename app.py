import os
import streamlit as st
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Load environment variables from .env
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Check if API key is available
if not openai_api_key:
    st.error("Please set your OPENAI_API_KEY in the .env file.")
    st.stop()

# Initialize LangChain Chat model
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# Create a basic prompt template
prompt = PromptTemplate(
    input_variables=["question"],
    template="You are a helpful assistant. Answer the following question:\n{question}"
)

# Set up the LangChain chain
chain = LLMChain(llm=llm, prompt=prompt)

# Streamlit UI
st.set_page_config(page_title="LangChain Chatbot", layout="centered")
st.title("💬 LangChain Chatbot")
st.write("Ask anything below 👇")

user_input = st.text_input("Enter your question", key="user_input")

if user_input:
    with st.spinner("Thinking..."):
        response = chain.run(user_input)
        st.markdown("### 🤖 Response")
        st.write(response)
