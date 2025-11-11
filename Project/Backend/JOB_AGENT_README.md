# 🔍 Job Search AI Agent

An intelligent AI agent built with LangGraph and LangChain that helps you search for jobs across multiple platforms using natural language.

## Features

- **Multi-Platform Job Search**: Search jobs on Indeed, LinkedIn, and Glassdoor
- **Remote Job Search**: Find remote and work-from-home opportunities
- **Market Insights**: Get job market trends and salary information
- **Conversational Interface**: Natural language interaction in terminal
- **Tool Integration**: Uses LangGraph for orchestrating multiple search tools

## Tech Stack

- **LangGraph**: For building the agent workflow and state management
- **LangChain**: For LLM integration and tool orchestration
- **OpenAI GPT**: Language model for understanding queries
- **DuckDuckGo Search**: For web scraping job listings
- **Python**: Core programming language

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements_job_agent.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the Backend directory:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

You can get an OpenAI API key from: https://platform.openai.com/api-keys

## Usage

### Running the Agent

```bash
cd Project/Backend
python job_search_agent.py
```

### Example Queries

1. **Basic Job Search**:
   - "Find software engineer jobs in San Francisco"
   - "Search for data scientist positions in New York"

2. **Remote Jobs**:
   - "Find remote Python developer jobs"
   - "Search for work from home marketing positions"

3. **Multi-Platform Search**:
   - "Look for UX designer jobs on LinkedIn and Indeed"
   - "Search Glassdoor for product manager roles"

4. **Market Insights**:
   - "What are the trends for AI engineer jobs?"
   - "Tell me about the job market for full stack developers"

5. **Complex Queries**:
   - "Search for remote frontend developer jobs and give me market insights"
   - "Find data analyst positions in Boston and check salary trends"

## Available Tools

The agent has access to the following tools:

1. **search_jobs_indeed**: Search jobs on Indeed.com
2. **search_jobs_linkedin**: Search jobs on LinkedIn.com
3. **search_jobs_glassdoor**: Search jobs on Glassdoor.com
4. **search_remote_jobs**: Find remote job opportunities
5. **get_job_market_insights**: Get market trends and salary information

## How It Works

1. **User Input**: You type a natural language query about job searching
2. **LLM Processing**: The OpenAI model understands your intent
3. **Tool Selection**: The agent decides which tools to use
4. **Tool Execution**: Selected tools search for jobs on various platforms
5. **Response Generation**: The LLM synthesizes results into a helpful response

## Architecture

The agent uses LangGraph's StateGraph with:
- **ChatState**: Manages conversation history
- **Chat Node**: Processes messages and decides on tool usage
- **Tool Node**: Executes the selected job search tools
- **Conditional Edges**: Routes between chat and tools based on context

## Tips

- Be specific with job titles and locations for better results
- You can ask for multiple things in one query
- The agent maintains conversation context
- Type 'exit' or 'quit' to end the session

## Limitations

- Uses DuckDuckGo for web scraping (not official APIs)
- Results depend on search engine availability
- Rate limiting may apply for frequent searches
- Requires active internet connection

## Future Enhancements

- Integration with official job board APIs
- Resume matching capabilities
- Application tracking
- Salary comparison tools
- Company reviews and ratings
- Email notifications for new jobs

## Troubleshooting

### Error: "Import ... could not be resolved"
Install the required packages: `pip install -r requirements_job_agent.txt`

### Error: "OpenAI API key not found"
Make sure you have a `.env` file with `OPENAI_API_KEY=your_key`

### Error: "Rate limit exceeded"
Wait a few moments before making more requests

## License

Part of the JobCore project.
