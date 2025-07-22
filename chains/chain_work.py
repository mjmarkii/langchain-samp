import os
import uuid
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chains import LLMChain
from langsmith import traceable

from prompts.prompt_work import SYSTEM_PROMPT, USER_PROMPT

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

class TracedExecutionOwnershipChain(LLMChain):
    """LLMChain wrapper that adds metadata to execution traces."""
    
    def __call__(self, inputs, return_only_outputs=False, callbacks=None, **kwargs):
        """Execute with metadata for LangSmith tracing."""
        print("Running chain 2/6: Execution and Ownership...")
        
        from langsmith import trace
        
        # Add metadata for this specific prompt execution
        metadata = {
            "chain_name": "execution_ownership",
            "prompt_type": "work_analysis",
            "model": "gpt-4.1", 
            "temperature": 0,
            "expected_output": "execution_ownership",
            "analysis_focus": "work_quality_and_ownership"
        }
        
        with trace(name="execution_ownership_execution", metadata=metadata):
            return super().__call__(inputs, return_only_outputs, callbacks, **kwargs)

def create_work_chain():
    """Create and return the execution and ownership LLMChain."""
    print("Creating execution and ownership chain...")
    
    # Initialize OpenAI language model with specific configuration
    llm = ChatOpenAI(model="gpt-4.1", temperature=0)

    # Create the prompt template combining system and human messages
    chat_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT),
        HumanMessagePromptTemplate.from_template(USER_PROMPT)
    ])

    # Create and return the traced LangChain processing chain
    chain = TracedExecutionOwnershipChain(llm=llm, prompt=chat_prompt, output_key="execution_ownership")

    return chain

# Create the chain instance for export
execution_ownership_chain = create_work_chain()