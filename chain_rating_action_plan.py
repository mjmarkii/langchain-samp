import os
import uuid
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chains import LLMChain

from variables import *
from prompts import rating_action_plan as rap
from datasource import *

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

def create_rating_action_plan_chain():
    """Create and return the rating action plan LLMChain."""
    print("Creating rating action plan chain...")

    # Initialize OpenAI language model with specific configuration
    llm = ChatOpenAI(model="gpt-4.1", temperature=0)

    # Create the prompt template combining system and human messages
    # Get the prompts from the rating_action_plan module
    system_message = rap.SYSTEM_PROMPT
    human_message_template = rap.USER_PROMPT

    chat_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_message),
        HumanMessagePromptTemplate.from_template(human_message_template)
    ])

    # Create and return the LangChain processing chain
    chain = LLMChain(llm=llm, prompt=chat_prompt, output_key="rating_action_plan")

    return chain

# Create the chain instance for export
chain2 = create_rating_action_plan_chain()
