import os
import uuid
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chains import LLMChain
from langsmith import traceable

from prompts.prompt_executive_summary import SYSTEM_PROMPT, USER_PROMPT

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

class TracedExecutiveSummaryChain(LLMChain):
    """LLMChain wrapper that adds metadata to execution traces."""
    
    @traceable(tags=["prompt-analysis", "summary", "executive-summary"], run_type="llm")
    def __call__(self, inputs, return_only_outputs=False, callbacks=None, **kwargs):
        """Execute with metadata for LangSmith tracing."""
        from langsmith import trace
        
        # Add metadata for this specific prompt execution
        metadata = {
            "chain_name": "executive_summary",
            "prompt_type": "summary_analysis",
            "model": "gpt-4.1",
            "temperature": 0,
            "expected_output": "executive_summary",
            "analysis_focus": "high_level_synthesis"
        }
        
        with trace(name="executive_summary_execution", metadata=metadata):
            return super().__call__(inputs, return_only_outputs, callbacks, **kwargs)

def create_executive_summary_chain():
    """Create and return the executive summary LLMChain."""
    print("Creating executive summary chain...")
    
    # Initialize OpenAI language model with specific configuration
    llm = ChatOpenAI(model="gpt-4.1", temperature=0)

    # Create the prompt template combining system and human messages
    chat_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT),
        HumanMessagePromptTemplate.from_template(USER_PROMPT)
    ])

    # Create and return the traced LangChain processing chain
    chain = TracedExecutiveSummaryChain(llm=llm, prompt=chat_prompt, output_key="executive_summary")

    return chain

# Create the chain instance for export
executive_summary_chain = create_executive_summary_chain()