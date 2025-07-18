import os
import uuid
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chains import LLMChain
from langsmith import traceable, trace

from variables import *
from prompts import final_report as fr

# Read the contents of output.py
try:
    with open("output.py", "r", encoding="utf-8") as f:
        analyzed_report_output = f.read()
except FileNotFoundError:
    analyzed_report_output = ""
    print("Warning: output.py not found. Using empty content.")

# Load environment variables from .env
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
langsmith_project = os.getenv("LANGSMITH_PROJECT", "wins-work-challenges-generator")

# Set up LangSmith
if langsmith_api_key:
    os.environ["LANGSMITH_TRACING_V2"] = "true"
    os.environ["LANGSMITH_API_KEY"] = langsmith_api_key
    os.environ["LANGSMITH_PROJECT"] = langsmith_project
else:
    print("Warning: LANGSMITH_API_KEY not found. Tracing will be disabled.")

# Validate API key availability before proceeding
if not openai_api_key:
    raise ValueError("Please set your OPENAI_API_KEY in the .env file.")

@traceable(name="performance_review_final_report", tags=["performance", "review", "report"], run_type="llm")
def generate_performance_review(chain_inputs, chain, session_id):
    """Generate performance review with LangSmith tracing."""
    # Create metadata with only the key fields (excluding long text inputs)
    metadata = {
        "session_id": session_id,
        "manager": chain_inputs["manager"],
        "team_member": chain_inputs["team_member"],
        "role": chain_inputs["role"],
        "date_range": chain_inputs["date_range"]
    }
    
    with trace(name="chain_final_report", metadata=metadata):
        return chain.run(chain_inputs)

def create_final_report_chain():
    """Create and return the final report LLMChain."""
    # Initialize OpenAI language model with specific configuration
    llm = ChatOpenAI(model="gpt-4.1", temperature=0)

    # Create the prompt template combining system and human messages
    # Get the prompts from the final_report module
    system_message = fr.SYSTEM_PROMPT
    human_message_template = fr.USER_PROMPT

    chat_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_message),
        HumanMessagePromptTemplate.from_template(human_message_template)
    ])

    # Create and return the LangChain processing chain
    return LLMChain(llm=llm, prompt=chat_prompt, output_key="final_output")

def main():
    """Simple Streamlit app for generating final performance review reports."""
    st.title("Performance Review Final Report Generator")
    
    # Initialize session state
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    # Generate button
    if st.button("Generate Final Report"):
        if not analyzed_report_output:
            st.error("No performance signals data found. Make sure output.py exists.")
            return
        
        with st.spinner("Generating report..."):
            try:
                # Create the chain
                chain = create_final_report_chain()
                
                # Prepare inputs
                date_today = datetime.now().strftime("%B %d, %Y")
                chain_inputs = {
                    "manager": MANAGER,
                    "team_member": TEAM_MEMBER,
                    "role": ROLE_TEAM_MEMBER,
                    "date_range": DATE_RANGE,
                    "date_today": date_today,
                    "analyzed_report": analyzed_report_output
                }
                
                # Generate the report
                result = generate_performance_review(chain_inputs, chain, st.session_state.session_id)
                
                # Display the result directly
                st.markdown(result)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Call the main function
if __name__ == "__main__":
    main()
