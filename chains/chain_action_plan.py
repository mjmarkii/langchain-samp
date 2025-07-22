import os
import uuid
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chains import LLMChain
from langsmith import traceable, trace

from prompts.prompt_action_plan import SYSTEM_PROMPT, USER_PROMPT

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

class TracedActionPlanChain(LLMChain):
    """LLMChain wrapper that adds metadata to execution traces."""
    
    def __call__(self, inputs, return_only_outputs=False, callbacks=None, **kwargs):
        """Execute with metadata for LangSmith tracing."""
        print("Running chain 5/6: Action Plan...")
        
        # Add metadata for this specific prompt execution
        metadata = {
            "chain_name": "action_plan",
            "prompt_type": "planning_analysis",
            "model": "o4-mini",
            "temperature": 1,
            "expected_output": "action_plan",
            "analysis_focus": "actionable_recommendations"
        }
        
        with trace(name="action_plan_execution", metadata=metadata):
            return super().__call__(inputs, return_only_outputs, callbacks, **kwargs)

def create_action_plan_chain():
    """Create and return the manager action plan LLMChain."""
    print("Creating manager action plan chain...")
    
    # Initialize OpenAI reasoning model with specific configuration
    llm = ChatOpenAI(model="o4-mini", temperature=1)

    # Create the prompt template combining system and human messages
    chat_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT),
        HumanMessagePromptTemplate.from_template(USER_PROMPT)
    ])

    # Create and return the traced LangChain processing chain
    chain = TracedActionPlanChain(llm=llm, prompt=chat_prompt, output_key="action_plan")

    return chain

# Create the chain instance for export
action_plan_chain = create_action_plan_chain()