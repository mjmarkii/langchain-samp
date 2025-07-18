import os
import uuid
import streamlit as st
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chains import LLMChain
from langchain_community.callbacks import get_openai_callback
from langsmith import traceable, trace

# Load environment variables from .env
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
langsmith_project = os.getenv("LANGSMITH_PROJECT", "gaps-growth-areas-generator")

# Set up LangSmith
if langsmith_api_key:
    os.environ["LANGSMITH_TRACING_V2"] = "true"
    os.environ["LANGSMITH_API_KEY"] = langsmith_api_key
    os.environ["LANGSMITH_PROJECT"] = langsmith_project
else:
    st.warning("LANGSMITH_API_KEY not found. Tracing will be disabled.")

# Validate API key availability before proceeding
if not openai_api_key:
    st.error("Please set your OPENAI_API_KEY in the .env file.")
    st.stop()

# SYSTEM PROMPT
system_message = """
Your goal is to **analyze source files and produce a concise, neutral report that surfaces recurring negative performance patterns.**

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

### Sections on Report Guidelines
#### Gaps and Growth Areas
- Use the **Severity Level Rubric** and the **Negative Pattern Detection Guidance** rubrics as internal guidance for analysis
- Only surface recurring patterns internally rated Severity 3 to 5. Do not reference these numbers in the final output.  
- Do **NOT** display severity numbers or rubric names (e.g., “Severity 3”) in the final report. Use descriptive labels (“Moderate”, “High”, or “Critical”) **only in plain English**, and only when appropriate.  
- For every issue in the **Gaps & Growth** section:
  - Clearly explain **why the pattern qualifies as recurring** (e.g., “seen 3 times across retros”)
  - Provide **proof of at least 3 separate instances**
  - Use direct quotes, task IDs, timestamps, or meeting references
  - Do not include isolated or resolved issues
  
---

### 📚 Negative Detection Rubrics

#### 📑 Severity-Level Rubric 

🟦 **Severity 1 – Low / Cosmetic**
**Impact**: Minimal to none; stylistic, personal, or situational.

**Characteristics**:
- Does not affect performance, clarity, or outcomes.
- Typically not worth action unless recurring unnecessarily.

**Examples**:
- Informal or overly casual writing tone
- Inconsistent formatting
- Slight deviation from team preferences

🟨 **Severity 2 – Mild / Contextual**
**Impact**: Low or isolated; often stems from temporary conditions like onboarding or unclear expectations.

**Characteristics**:
- No material effect on team coordination or delivery.
- Generally self-resolving with time or context clarification.

**Examples**:
- One-off delay in task updates
- Brief hesitation in async discussions
- Minor learning curve delays

> **Note**: May be tracked informally in coaching notes. Not included in formal growth area reports unless they escalate.

🟧 **Severity 3 – Moderate / Coaching-Worthy**
**Impact**: Repeated friction or ambiguity affecting clarity, communication rhythm, or trust.

**Characteristics**:
- Noticed by team or manager, creating low-level concern.
- Excellent coaching opportunity; does not yet warrant escalation.
- If unresolved, may evolve into a Severity 4 pattern.

**Examples**:
- Regularly vague stand-up updates (“Still working on it”)
- Doesn't respond to PR comments for days
- Doesn't review teammate PRs even when asked
- Seems disengaged or distracted in team discussions
- Regular delays with no time estimate or heads-up
- Doesn't mention they're blocked until asked

🟧 **Special Coaching-Worthy Patterns** (still Severity 3):
**Examples**:
- Chronic low energy or late starts but still completes work (possible sleep or health-related – coach with empathy)
- Avoids pairing or collaboration (“I'll just figure it out later”)
- Repeatedly chooses solo work, avoids team calls
- Doesn't show initiative outside of assigned tasks

🟥 **Severity 4 – High / Delivery-Impacting**
**Impact**: Noticeable degradation of delivery quality, velocity, or coordination.

**Characteristics**:
- Requires intervention from peers or managers.
- May result in planning rework or trust breakdowns.
- Represents a repeated, unresolved Severity 3 issue.

**Examples**:
- Drops assigned tasks without updating anyone
- Refuses pairing or help despite clear blockers
- Tasks consistently spill over sprints due to poor time management
- Doesn't show up to key syncs or retros without explanation
- Team members rework or reassign their items to compensate
- Leaves team guessing on status until the last minute

🔴 **Severity 5 – Critical / Systemic Risk**
**Impact**: Severe and recurring damage to team output, reliability, or cohesion.

**Characteristics**:
- Signals misalignment in role fit or expectations.
- Requires immediate and sustained managerial intervention.

**Examples**:
- Doesn't show up to work without notice or goes dark in active projects
- Withholds blockers even after being asked directly
- Ignores review feedback or delivery standards
- Teammates raise repeated concerns about dependability or behavior
- Misses sprint deadlines multiple times with no warning
- Blames others or avoids accountability when work slips

---

#### 📘 Negative Pattern Detection Guidance

⏳ **Execution Gaps**:
- Frequently missing task updates or incomplete reports
- Repeated delays without clear blockers or external dependencies
- Regularly incomplete sprint work despite available time

🧩 **Unclear or Weak Ownership**:
- Avoidance or vague description of assigned tasks
- Patterns of shifting responsibility without resolution
- Failing to follow up on feedback, tasks, or issues raised

📉 **Engagement and Presence**:
- Repeated silence in meetings or reports (e.g., multi-day gaps)
- Signs of disengagement: abrupt one-line updates, lack of context, no retrospection
- Consistently reactive (never proactive) communication

💬 **Collaboration Friction**:
- Poor visibility to teammates (e.g., no async status, unclear handoffs)
- Lack of responsiveness to peer or manager input
- Missing collaboration in known cross-functional tasks

🔄 **Repetition of Avoidable Mistakes**:
- Repeated misimplementation of known standards or feedback
- Frequently needing multiple rounds of correction on similar tasks
- Recurring misunderstandings in handoff or integration work

🚩 **Signals of Burnout or Frustration**:
- Noticeable drop in quality, energy, or tone over time
- Language that signals frustration, confusion, or feeling overwhelmed
- Abrupt or defensive responses in written communication

🚫 **Breaks in Process or Rituals**:
- Consistently skipping or minimizing participation in standups or check-ins
- Avoiding documentation, testing, or code reviews without reason
- Disregard for team agreements (e.g., feature flags, ticket hygiene)

⚖️ **Pattern Evaluation**:
- Use pattern + frequency + tone + context to determine severity
- One-time or context-specific misses must be ignored
- If no high-severity patterns exist, clearly state that as a positive indicator of performance

📵 **Unreliable Availability**:
- Frequently goes offline or unavailable during expected work hours without prior notice
- Misses scheduled syncs, standups, or deadlines with no explanation
- Team is left guessing about presence, timeline, or ownership due to lack of communication
- Causes coordination issues due to unclear or erratic availability patterns

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

### ⚠️ Gaps & Growth Areas

Highlight any **recurring**, **unresolved**, or **high-severity** challenges that were directly attributable to **{team_member}** during **{date_range}**.

This section is designed to support **constructive growth**, not evaluation or blame. Use it to help **{manager}** understand the team member's current struggles so they can offer the right support, realignment, or enablement.

If no significant concerns were identified, explicitly state:

> _"No performance concerns were identified during this period. {team_member}'s work aligns well with expectations. Recommend maintaining current consistency, visibility, and proactive engagement to sustain impact."_

DO NOT include, mention, or refer to severity ratings in the report. 

For any meaningful issue found, present your findings as a **markdown-formatted list**. Use the structure below for each item:

- **[Issue Observed]**: Clearly name the pattern or problem behavior (e.g., missed follow-through on tickets, unclear async updates, resistance to feedback).
  - **Level**: The severity level description of the issue (e.g., Moderate / Coaching-Worthy, High / Delivery-Impacting, or Critical / Systemic Risk).
  - **Recurrence**: How many times (e.g., “seen 3 times across retros”)
  - **Evidences**: Up to 3 direct quotes, paraphrased examples, or observable actions that illustrate the behavior.
  - **Cause**: Identify the likely root factor (e.g., skill gap, misalignment of priorities, communication breakdown, mindset).
  - **Impact**: Explain how this affected team performance, delivery velocity, quality, morale, or stakeholder trust.
  - **Manager Action**: Suggest how the manager can help — whether through coaching, clarity, additional structure, or delegation.

Keep tone neutral and developmental. Prioritize clarity and accountability.

---

"""

# LANGSMITH TRACING FUNCTION
@traceable(name="performance_review_generation", tags=["performance", "review"], run_type="llm")
def generate_performance_review(chain_inputs, chain, session_id):
    """Generate performance review with LangSmith tracing."""
    # Create metadata with only the key fields (excluding long text inputs)
    metadata = {
        "session_id": session_id,
        "manager": chain_inputs["manager"],
        "team_member": chain_inputs["team_member"],
        "role": chain_inputs["role"],
        "date_range": chain_inputs["date_range"]
    }
    
    with trace(name="chain_execution", metadata=metadata):
        return chain.run(chain_inputs)

# STREAMLIT APPLICATION INTERFACE
def main():
    st.set_page_config(page_title="Performance Review Generator - Impact Highlights", layout="wide")
    st.title("📋 Performance Review Briefing Generator")
    
    # Generate session ID for this Streamlit session
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

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
        
        # Session ID display
        st.divider()
        st.subheader("🔍 Session Tracking")
        st.text_input(
            "Session ID", 
            value=st.session_state.session_id, 
            disabled=True,
            help="Copy this ID to track your session in LangSmith"
        )
        if st.button("📋 Copy Session ID"):
            st.write("Session ID copied to clipboard!")
            st.code(st.session_state.session_id)

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
            result = generate_performance_review({
                "manager": manager,
                "team_member": team_member,
                "role": role,
                "date_range": date_range,
                "daily_text": daily_text,
                "claap_text": claap_text,
                "fathom_text": fathom_text,
                "jira_text": jira_text
            }, chain, st.session_state.session_id)

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
