# Performance Review Generator with LangSmith Integration

A Streamlit-based performance review generator that uses LangChain and OpenAI's GPT-4.1 model to analyze various data sources and create comprehensive performance reports, with LangSmith integration for tracking and monitoring.

## Features

- 📋 Automated performance review generation from multiple data sources
- 📊 LangSmith integration for conversation tracking with session IDs
- 🧵 Session management for grouping review generations
- 🔍 Real-time monitoring and debugging in LangSmith
- 📝 Analysis of daily updates, meeting transcripts, and JIRA tickets
- 💰 Token usage and cost tracking
- 📋 Easy session ID copying for trace correlation

## Setup

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file in the root directory with:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   LANGSMITH_API_KEY=your_langsmith_api_key_here
   LANGSMITH_PROJECT=performance-review-generator
   ```

4. **Get LangSmith API Key:**
   - Sign up at [https://smith.langchain.com/](https://smith.langchain.com/)
   - Go to your profile settings
   - Copy your API key

5. **Ask for the datasource file from devs**
   - You need this to run the app

5. **Run the app:**
   ```bash
   python master_chain.py
   ```

## LangSmith Features

With LangSmith integration, you can:

- **Track Review Generations**: Every performance review generation is logged with session ID and input metadata
- **Monitor Performance**: View response times, token usage, and success rates
- **Debug Issues**: Inspect detailed traces of each review generation process
- **Group by Session**: All reviews in a session are grouped by unique session ID
- **Analyze Input Patterns**: See what types of data lead to better reviews

## Usage

1. Open the app in your browser
2. View your current session ID in the sidebar
3. Fill in the review context (manager, team member, role, date range)
4. Paste input data in all four required sections:
   - Daily Status Updates
   - Claap Transcripts
   - Fathom Transcripts
   - JIRA Tickets
5. Click "🚀 Generate Review" to create the performance report
6. Use "📋 Copy Session ID" to get your session ID for LangSmith tracking
7. Monitor all traces in your LangSmith dashboard

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `LANGSMITH_API_KEY`: Your LangSmith API key (optional, but recommended for tracking)
- `LANGSMITH_PROJECT`: Project name in LangSmith (defaults to "performance-review-generator")
- `LANGSMITH_TRACING_V2`: Enable LangSmith tracing (automatically set to "true" when LANGSMITH_API_KEY is provided)

## Troubleshooting

- If you see a warning about missing LangSmith API key, add it to your `.env` file
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check the LangSmith dashboard at [https://smith.langchain.com/](https://smith.langchain.com/) for traces
- Each session has a unique session ID visible in the sidebar for trace correlation
- All input fields are required - the app will warn if any are missing