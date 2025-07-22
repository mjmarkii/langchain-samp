import os
import uuid
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chains import LLMChain
from langsmith import traceable, trace

from prompts.prompt_perf_rating import SYSTEM_PROMPT, USER_PROMPT

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

class TracedPerformanceRatingChain(LLMChain):
    """LLMChain wrapper that adds metadata to execution traces."""
    
    def __call__(self, inputs, return_only_outputs=False, callbacks=None, **kwargs):
        """Execute with metadata for LangSmith tracing."""
        print("Running chain 4/6: Performance Rating...")
        
        # Add metadata for this specific prompt execution
        metadata = {
            "chain_name": "performance_rating",
            "prompt_type": "rating_analysis",
            "model": "o4-mini",
            "temperature": 1,
            "expected_output": "performance_rating",
            "analysis_focus": "quantitative_performance_assessment"
        }
        
        with trace(name="performance_rating_execution", metadata=metadata):
            return super().__call__(inputs, return_only_outputs, callbacks, **kwargs)

def create_perf_rating_chain():
    """Create and return the performance rating LLMChain."""
    print("Creating performance rating chain...")
    
    # Initialize OpenAI reasoning model with specific configuration
    llm = ChatOpenAI(model="o4-mini", temperature=1)

    # Create the prompt template combining system and human messages
    chat_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT),
        HumanMessagePromptTemplate.from_template(USER_PROMPT)
    ])

    # Create and return the traced LangChain processing chain
    chain = TracedPerformanceRatingChain(llm=llm, prompt=chat_prompt, output_key="performance_rating")

    return chain

# Create the chain instance for export
performance_rating_chain = create_perf_rating_chain()