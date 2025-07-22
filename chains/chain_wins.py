import os
import uuid
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chains import LLMChain

from prompts.prompt_wins import SYSTEM_PROMPT, USER_PROMPT

# Load environment variables from .env
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
langsmith_project = os.getenv("LANGSMITH_PROJECT", "performance-review-generator")

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

def create_wins_chain():
    """Create and return the impact highlights LLMChain."""
    print("Creating impact highlights chain...")

    # Initialize OpenAI language model with specific configuration
    llm = ChatOpenAI(model="gpt-4.1", temperature=0)

    # Create the prompt template combining system and human messages
    chat_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT),
        HumanMessagePromptTemplate.from_template(USER_PROMPT)
    ])

    # Create and return the LangChain processing chain
    chain = LLMChain(llm=llm, prompt=chat_prompt, output_key="impact_highlights", verbose=True)

    return chain

# Create the chain instance for export
impact_highlights_chain = create_wins_chain()