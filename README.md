# Performance Review Generator with LangSmith Integration

A Streamlit-based performance review generator that uses LangChain and OpenAI's GPT-4.1 model to analyze various data sources and create comprehensive performance reports, with comprehensive LangSmith tracing for monitoring and debugging.

## Features

- 📋 Automated performance review generation from multiple data sources
- 🔍 **Comprehensive LangSmith Tracing**: End-to-end visibility of the review generation pipeline
- 📊 **Chain-Specific Monitoring**: Individual tracing for all 6 review components with rich metadata
- 🎯 **Progress Tracking**: Real-time console logging showing "Running chain 1/6: Impact Highlights..." 
- 🧵 Session management for grouping review generations
- 📝 Analysis of daily updates, meeting transcripts, and JIRA tickets
- 💰 Token usage and cost tracking per chain
- 🔧 Debug-friendly trace trees for troubleshooting

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
   LANGSMITH_TRACING_V2=true
   ```

4. **Get LangSmith API Key:**
   - Sign up at [https://smith.langchain.com/](https://smith.langchain.com/)
   - Go to your profile settings
   - Copy your API key

5. **Ask for the datasource file from devs**
   - You need this to run the app

6. **Run the master chain:**
   ```bash
   python master_chain.py
   ```

7. To generate the final report, run:
   ```bash
   streamlit run generate_final_report.py
   ```

## LangSmith Tracing Features

### 🔍 End-to-End Pipeline Monitoring
- **Master Orchestrator**: Tracks the complete review generation process
- **Chain Creation**: Monitors sequential chain setup and configuration
- **Individual Chains**: Detailed traces for each of the 6 review components

### 📊 Rich Metadata for Analysis
Each chain execution includes detailed metadata for filtering and performance analysis:
- `chain_name`: Specific identifier (impact_highlights, execution_ownership, gaps_growth_areas, etc.)
- `prompt_type`: Analysis type (wins_analysis, work_analysis, challenges_analysis, etc.)
- `model`: LLM model used (gpt-4.1, o4-mini)
- `temperature`: Model temperature setting
- `analysis_focus`: Specific focus area for each chain

### 🎯 Console Progress Tracking
Real-time logging shows exactly which chain is executing:
```
Running chain 1/6: Impact Highlights...
Running chain 2/6: Execution and Ownership...
Running chain 3/6: Gaps and Growth Areas...
Running chain 4/6: Performance Rating...
Running chain 5/6: Action Plan...
Running chain 6/6: Executive Summary...
```

### 📈 Performance Analysis
- **Chain-Specific Metrics**: Monitor performance of individual prompt types
- **Model Comparison**: Compare gpt-4.1 vs o4-mini across different chains
- **Filtering Capabilities**: Group traces by chain type, model, or analysis focus
- **Token Usage Tracking**: Per-chain cost and performance analysis

## Trace Structure

```
master_orchestrator
├── sequential_chain_creation
│   └── chain_setup_execution
└── performance_review_execution
    └── SequentialChain
        ├── TracedImpactHighlightsChain → impact_highlights_execution
        ├── TracedExecutionOwnershipChain → execution_ownership_execution
        ├── TracedGapsGrowthAreasChain → gaps_growth_areas_execution
        ├── TracedPerformanceRatingChain → performance_rating_execution
        ├── TracedActionPlanChain → action_plan_execution
        └── TracedExecutiveSummaryChain → executive_summary_execution
```

## Usage

### For Master Chain (Recommended)
1. Run `python master_chain.py`
2. Watch console for real-time progress tracking
3. Monitor traces in [LangSmith Dashboard](https://smith.langchain.com/)
4. Filter by `chain_name` for specific prompt analysis
5. Group by `model` for performance comparison

### For Streamlit App
1. Open the app in your browser with `streamlit run generate_final_report.py`
2. View your current session ID in the sidebar
3. Fill in the review context (manager, team member, role, date range)
4. Paste input data in all four required sections:
   - Daily Status Updates
   - Claap Transcripts
   - Fathom Transcripts
   - JIRA Tickets
5. Click "🚀 Generate Review" to create the performance report
6. Use "📋 Copy Session ID" to get your session ID for LangSmith tracking

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `LANGSMITH_API_KEY`: Your LangSmith API key (optional, but recommended for tracing)
- `LANGSMITH_PROJECT`: Project name in LangSmith (defaults to "performance-review-generator")
- `LANGSMITH_TRACING_V2`: Enable LangSmith tracing (set to "true" for full tracing)

## Troubleshooting

- If you see a warning about missing LangSmith API key, add it to your `.env` file
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check the LangSmith dashboard at [https://smith.langchain.com/](https://smith.langchain.com/) for traces
- Each execution has a unique session ID for trace correlation
- Console logging will show progress even if LangSmith is not configured