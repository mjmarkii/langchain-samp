import os
import uuid
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.chains import SequentialChain
from langsmith import traceable, trace

# Import the individual chains
from chains.chain_wins import impact_highlights_chain
from chains.chain_work import execution_ownership_chain
from chains.chain_challenges import gaps_growth_areas_chain
from chains.chain_perf_rating import performance_rating_chain
from chains.chain_action_plan import action_plan_chain
from chains.chain_executive_summary import executive_summary_chain

# Import variables and data sources
from variables import *
from datasource import *

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

@traceable(name="sequential_chain_creation", tags=["setup", "chain-creation"], run_type="chain")
def create_master_sequential_chain():
    """Create and return the master SequentialChain that combines all chains."""
    
    # Generate unique execution ID for this chain creation
    execution_id = str(uuid.uuid4())
    print(f"Creating master sequential chain - Execution ID: {execution_id}")
    
    # Add execution ID to trace metadata
    metadata = {
        "execution_id": execution_id,
        "operation": "sequential_chain_creation",
        "total_chains": 6,  # Back to all chains
        "chain_names": ["impact_highlights", "execution_ownership", "gaps_growth_areas", "performance_rating", "action_plan", "executive_summary"]
    }
    
    with trace(name="chain_setup_execution", metadata=metadata):
        # Create the sequential chain that combines all chains
        master_chain = SequentialChain(
            chains=[
                impact_highlights_chain,
                execution_ownership_chain, 
                gaps_growth_areas_chain,
                performance_rating_chain,
                action_plan_chain,
                executive_summary_chain
            ],
            input_variables=[
                "manager", 
                "team_member",
                "role", 
                "date_range", 
                "daily_text", 
                "claap_text", 
                "fathom_text", 
                "jira_text"
            ],
            output_variables=[
                "impact_highlights",
                "execution_ownership", 
                "gaps_growth_areas", 
                "performance_rating", 
                "action_plan", 
                "executive_summary"
            ],
            verbose=True
        )
        
        print(f"Sequential chain created successfully - Execution ID: {execution_id}")
        return master_chain

@traceable(name="performance_review_execution", tags=["execution", "performance-review"], run_type="chain")
def execute_performance_review(chain_inputs, chain, session_id):
    """Execute the performance review chain with tracing."""
    return chain(chain_inputs)

@traceable(name="master_orchestrator", tags=["orchestrator", "end-to-end"], run_type="chain") 
def run_master_chain():
    """Run the master chain with the input variables and handle output."""
    
    # Create the master chain
    master_chain = create_master_sequential_chain()
    
    print("Running each chain in sequence...")
    
    # Generate a unique session ID for tracing
    session_id = str(uuid.uuid4())
    
    # Prepare input variables
    chain_inputs = {
        "manager": MANAGER,
        "team_member": TEAM_MEMBER,
        "role": ROLE_TEAM_MEMBER,
        "date_range": DATE_RANGE,
        "daily_text": DAILY_TEXT,
        "claap_text": CLAAP_TEXT,
        "fathom_text": FATHOM_TEXT,
        "jira_text": JIRA_TEXT
    }
    
    # Run the chain with LangSmith tracing
    result = execute_performance_review(chain_inputs, master_chain, session_id)
    
    print("All chains completed!")
    
    return result

if __name__ == "__main__":
    # Run the master chain
    try:
        result = run_master_chain()

        # Write results to output.py
        print("Writing results to output.py...")

        # Prepare all content first
        output_sections = [
            ("Impact Highlights", result['impact_highlights']),
            ("Execution and Ownership", result['execution_ownership']),
            ("Gaps and Growth Areas", result['gaps_growth_areas']),
            ("Performance Rating", result['performance_rating']),
            ("Action Plan", result['action_plan']),
            ("Executive Summary", result['executive_summary'])
        ]
        
        # Write all content in a single operation
        with open("output.py", "w", encoding="utf-8") as f:
            for section_name, content in output_sections:
                print(f"Adding {section_name} result...")
                f.write(f"{content}\n\n")
        
        print("Results successfully written to output.py!")
        print("Master chain execution completed successfully!")
    except Exception as e:
        print(f"Error running master chain: {str(e)}")
        raise 