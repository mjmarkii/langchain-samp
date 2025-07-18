import os
import uuid
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chains import LLMChain

from prompts import wins_work_challenges as wwc

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

def create_wins_work_challenges_chain():
    """Create and return the wins work challenges LLMChain."""
    print("Creating wins work challenges chain...")

    # Initialize OpenAI language model with specific configuration
    llm = ChatOpenAI(model="gpt-4.1", temperature=0)

    # Create the prompt template combining system and human messages
    # Get the prompts from the wins_work_challenges module
    system_message = wwc.SYSTEM_PROMPT
    human_message_template = wwc.USER_PROMPT

    chat_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_message),
        HumanMessagePromptTemplate.from_template(human_message_template)
    ])

    # Create and return the LangChain processing chain
    chain = LLMChain(llm=llm, prompt=chat_prompt, output_key="wins_work_challenges")

    return chain

# Create the chain instance for export
chain1 = create_wins_work_challenges_chain()