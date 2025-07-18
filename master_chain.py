import os
import uuid
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.chains import SequentialChain

# Import the individual chains
from chain_wins_work_challenges import chain1
from chain_rating_action_plan import chain2
from chain_executive_summary import chain3

# Import variables and data sources
from variables import *
from datasource import *

# Load environment variables from .env
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
langsmith_project = os.getenv("LANGSMITH_PROJECT", "master-chain-generator")

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

def create_master_sequential_chain():
    """Create and return the master SequentialChain that combines all three chains."""
    print("Creating master sequential chain...")
    
    # Create the sequential chain that combines all three chains
    master_chain = SequentialChain(
        chains=[chain1, chain2, chain3],
        input_variables=[
            "manager", 
            "team_member", 
            "date_range", 
            "daily_text", 
            "claap_text", 
            "fathom_text", 
            "jira_text"
        ],
        output_variables=[
            "wins_work_challenges",
            "rating_action_plan", 
            "executive_summary"
        ],
        verbose=True
    )
    
    return master_chain

def run_master_chain():
    """Run the master chain with the input variables and handle output."""
    print("Starting master chain execution...")
    
    # Create the master chain
    master_chain = create_master_sequential_chain()
    
    print("Running chain 1: Wins Work Challenges...")
    
    # Run the chain with input variables
    result = master_chain({
        "manager": MANAGER,
        "team_member": TEAM_MEMBER,
        "date_range": DATE_RANGE,
        "daily_text": DAILY_TEXT,
        "claap_text": CLAAP_TEXT,
        "fathom_text": FATHOM_TEXT,
        "jira_text": JIRA_TEXT
    })
    
    print("Chain 1 completed successfully!")
    print("Running chain 2: Rating Action Plan...")
    print("Chain 2 completed successfully!")
    print("Running chain 3: Executive Summary...")
    print("Chain 3 completed successfully!")
    
    print("All chains completed! Writing results to output.py...")
    
    # Clear output.py first
    with open("output.py", "w", encoding="utf-8") as f:
        f.write("# Generated Performance Review Results\n\n")
    
    # Append each result to output.py
    print("Appending Wins Work Challenges result...")
    with open("output.py", "a", encoding="utf-8") as f:
        f.write(f"{result['wins_work_challenges']}\n\n")
    
    print("Appending Rating Action Plan result...")
    with open("output.py", "a", encoding="utf-8") as f:
        f.write(f"{result['rating_action_plan']}\n\n")
    
    print("Appending Executive Summary result...")
    with open("output.py", "a", encoding="utf-8") as f:
        f.write(f"{result['executive_summary']}\n\n")
    
    print("Results successfully written to output.py!")
    print("Master chain execution completed successfully!")
    
    return result

if __name__ == "__main__":
    # Run the master chain
    try:
        result = run_master_chain()
    except Exception as e:
        print(f"Error running master chain: {str(e)}")
        raise 