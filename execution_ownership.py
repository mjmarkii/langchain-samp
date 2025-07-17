import os
import streamlit as st
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chains import LLMChain
from langchain_community.callbacks import get_openai_callback

# Load environment variables from .env
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Validate API key availability before proceeding
if not openai_api_key:
    st.error("Please set your OPENAI_API_KEY in the .env file.")
    st.stop()

# SYSTEM PROMPT
system_message = """
Your goal is to **analyze source files and produce a concise, neutral report.**

---

### Behavior Guidelines
- Strip all HTML and normalize whitespace  
- Retain speaker labels, timestamps, and conversational flow  
- Preserve quoted remarks for authenticity and nuance  
- Favor plain business language; avoid jargon unless quoting  
- Prioritize clarity, conciseness, and manager usefulness  
- Avoid vague praise, exaggeration, or over-interpretation  
- If source data lacks enough signals for a section, state:  
  _"Not enough evidence found for this section within {date_range}."_
- When referencing specific evidence, include ticket ID or timestamp in parentheses 
- DO NOT add any additional sections or output that isn't stated in the Output Structure

---

### Fallback

If unsure or data is incomplete, respond:  
> "I don't have enough information to answer this accurately."
"""

# USER PROMPT (combined content and instructions)
human_message_template = """
## 🎯 Context

You are a highly skilled engineering performance analyst. Your task is to examine raw data from the provided files—these may include daily reports, meeting transcripts, JIRA tickets, and HTML content—spanning the period of **{date_range}**.

Your objective is to generate a comprehensive **Performance Review Briefing** for **{manager}**, offering clear, context-rich insights into **{team_member}**'s contributions, behavioral patterns, and any friction points observed during this period that may need **{manager}**'s attention.

This report is designed to support a high-impact 1-on-1 conversation between the manager and the team member. It should help the manager:
- Recognize and highlight key contributions and achievements  
- Identify trends or patterns in engagement, productivity, and collaboration  
- Detect and flag potential challenges or areas needing attention
- Deliver specific, actionable feedback  
- Guide thoughtful coaching conversations that support growth and development

---

## 📂 Source Files

### Daily Status Updates:
{daily_text}

---

### Claap Transcripts:
{claap_text}

---

### Fathom Transcripts:
{fathom_text}

---

### JIRA Tickets:
{jira_text}

---

## 📄 OUTPUT: Report Structure

---

### 🛠️ Execution & Ownership

Summarize how **{team_member}** executed on their core responsibilities during **{date_range}**, with a focus on consistency, initiative, and follow-through.

Break down your assessment into the following categories:
- **[Primary Scope]**: What areas, systems, or types of work did {team_member} consistently own? Include recurring responsibilities or specialized roles they were trusted with.
- **[Delivery Patterns]**: Describe how reliably they delivered work. Were tasks completed on time and to spec? Did they consistently follow through without needing reminders or rework?
- **[Reliability & Accountability Signals]**: Provide examples of behaviors that show ownership—such as proactively unblocking themselves or others, raising flags early, clarifying requirements, or taking initiative beyond assigned work.
- **[Adaptability & Learning (Optional)]**: If applicable, highlight how {team_member} responded to new challenges, changing priorities, or learning opportunities.

Use clear examples and avoid vague adjectives. If signals were mixed or inconsistent, call that out with balance.

"""

# STREAMLIT APPLICATION INTERFACE
def main():
    st.set_page_config(page_title="Performance Review Generator - Execution and Ownership", layout="wide")
    st.title("📋 Performance Review Briefing Generator")

    # SIDEBAR: REVIEW CONTEXT CONFIGURATION
    # Sidebar contains the essential context variables needed for generating
    # personalized performance reviews
    with st.sidebar:
        st.header("🧠 Review Context")
        manager = st.text_input("Manager", value="Cleo Credo")
        team_member = st.text_input("Team Member", value="Harold Inacay")
        role = st.text_input("Role", value="Full-Stack Developer")
        date_range = st.text_input("Date Range", value="April 1, 2025 - June 30, 2025")
        run = st.button("🚀 Generate Review")

    # MAIN CONTENT: DATA INPUT SECTIONS
    # These text areas allow users to paste different types of source data
    # that will be analyzed to generate the performance review
    st.subheader("📝 Paste Inputs (All Required)")
    daily_text = st.text_area("📆 Daily Status Updates", height=200)
    claap_text = st.text_area("🎙️ Claap Transcripts", height=200)
    fathom_text = st.text_area("📼 Fathom Transcripts", height=200)
    jira_text = st.text_area("🛠 JIRA Tickets", height=200)

    # PROCESSING AND RESULTS GENERATION
    if run:
        # Validate that all required inputs are provided
        if not all([daily_text, claap_text, fathom_text, jira_text]):
            st.warning("⚠️ Please fill in all input sections.")
            return

        st.info("Generating performance report...")

        # Initialize OpenAI language model with specific configuration
        llm = ChatOpenAI(model="gpt-4.1", temperature=0)

        # Create the prompt template combining system and human messages
        chat_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_message),
            HumanMessagePromptTemplate.from_template(human_message_template)
        ])

        # Create the LangChain processing chain
        chain = LLMChain(llm=llm, prompt=chat_prompt, output_key="final_output")

        # Execute the chain with token usage tracking for cost monitoring
        with get_openai_callback() as cb:
            result = chain.run({
                "manager": manager,
                "team_member": team_member,
                "role": role,
                "date_range": date_range,
                "daily_text": daily_text,
                "claap_text": claap_text,
                "fathom_text": fathom_text,
                "jira_text": jira_text
            })

            # Extract token usage metrics for cost tracking
            total_tokens = cb.total_tokens
            prompt_tokens = cb.prompt_tokens
            completion_tokens = cb.completion_tokens
            cost = cb.total_cost

        # Display the generated performance review and usage statistics
        st.success("✅ Report Ready!")
        st.markdown(result)

        # Expandable section showing detailed token usage and cost information
        with st.expander("📊 Token Usage"):
            st.write(f"**Prompt tokens:** {prompt_tokens}")
            st.write(f"**Completion tokens:** {completion_tokens}")
            st.write(f"**Total tokens:** {total_tokens}")
            st.write(f"**Estimated cost (USD):** ${cost:.5f}")

# main fn call
if __name__ == "__main__":
    main()
