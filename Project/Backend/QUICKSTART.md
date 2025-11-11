# 🚀 Quick Start Guide - Job Search AI Agent

## What I've Built For You

I've created an AI-powered job search agent based on the architecture from `11_tools.ipynb`. Here's what you have:

### 📁 Files Created:

1. **`job_search_agent.py`** - Main AI agent with full LangGraph/LangChain integration
2. **`simple_job_agent.py`** - Demo version you can run immediately
3. **`test_job_agent.py`** - Test script with example queries
4. **`requirements_job_agent.txt`** - All required dependencies
5. **`.env.example`** - Environment variables template
6. **`setup_check.py`** - Environment verification script
7. **`JOB_AGENT_README.md`** - Detailed documentation

## 🎯 Features

### Job Search Capabilities:
- ✅ Search jobs on **Indeed**
- ✅ Search jobs on **LinkedIn** 
- ✅ Search jobs on **Glassdoor**
- ✅ Find **remote** opportunities
- ✅ Get **market insights** and salary trends

### Tech Stack (Same as 11_tools.ipynb):
- **LangGraph** - State management and workflow
- **LangChain** - LLM and tool orchestration
- **OpenAI GPT** - Language understanding
- **DuckDuckGo Search** - Web scraping for jobs

## ⚡ Run It NOW (Demo Mode)

You can try the interface immediately without installing anything:

```bash
cd /Users/kamrul/Developer/JobCore/Project/Backend
python3 simple_job_agent.py
```

This runs in DEMO mode and shows you how the chat interface works.

## 🔧 Full Setup (For Complete Functionality)

### Step 1: Install Dependencies

```bash
cd /Users/kamrul/Developer/JobCore/Project/Backend
pip3 install -r requirements_job_agent.txt
```

This will install:
- langgraph
- langchain
- langchain-openai
- langchain-community
- langchain-core
- python-dotenv
- requests
- duckduckgo-search

### Step 2: Set Up OpenAI API Key

1. Get your API key from: https://platform.openai.com/api-keys

2. Create `.env` file:
```bash
cp .env.example .env
```

3. Edit `.env` and add your key:
```bash
OPENAI_API_KEY=sk-your-actual-key-here
```

### Step 3: Verify Setup

```bash
python3 setup_check.py
```

This will check if everything is configured correctly.

### Step 4: Run the Full Agent

```bash
python3 job_search_agent.py
```

Or run tests:
```bash
python3 test_job_agent.py
```

## 💬 Example Conversations

Once running, try these queries:

```
You: Find software engineer jobs in San Francisco
Agent: [Searches Indeed, LinkedIn, Glassdoor and returns results]

You: Search for remote Python developer positions
Agent: [Searches specifically for remote jobs]

You: What are the salary trends for data scientists?
Agent: [Provides market insights and trends]

You: Look for UX designer jobs in Seattle on LinkedIn
Agent: [Searches LinkedIn specifically]

You: Find remote full stack jobs and give me market insights
Agent: [Uses multiple tools to search and analyze]
```

## 🏗️ Architecture (Like 11_tools.ipynb)

```
User Query
    ↓
Chat Node (LLM decides which tools to use)
    ↓
Tool Node (Executes selected tools)
    ↓
Chat Node (Synthesizes response)
    ↓
User sees results
```

### Tools Available:
1. `search_jobs_indeed` - Indeed.com search
2. `search_jobs_linkedin` - LinkedIn.com search
3. `search_jobs_glassdoor` - Glassdoor.com search
4. `search_remote_jobs` - Remote job search
5. `get_job_market_insights` - Trends & salary data

## 📊 Comparison with 11_tools.ipynb

| Feature | 11_tools.ipynb | job_search_agent.py |
|---------|----------------|---------------------|
| Framework | LangGraph ✅ | LangGraph ✅ |
| State Management | TypedDict + add_messages ✅ | TypedDict + add_messages ✅ |
| Tool Integration | @tool decorator ✅ | @tool decorator ✅ |
| LLM | ChatOpenAI ✅ | ChatOpenAI ✅ |
| Graph Structure | StateGraph ✅ | StateGraph ✅ |
| Conditional Edges | tools_condition ✅ | tools_condition ✅ |
| Example Tools | Calculator, Stock, Search | Job Search Tools |
| Interface | Notebook | Terminal Chat |

## 🎓 How It Works (Just Like 11_tools.ipynb)

### 1. Define Tools
```python
@tool
def search_jobs_indeed(query: str, location: str = "United States") -> dict:
    """Search for jobs on Indeed"""
    # Implementation
```

### 2. Create State
```python
class JobSearchState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
```

### 3. Build Graph
```python
graph = StateGraph(JobSearchState)
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)
graph.add_conditional_edges("chat_node", tools_condition)
```

### 4. Compile & Run
```python
job_search_agent = graph.compile()
result = job_search_agent.invoke({"messages": [HumanMessage(content=query)]})
```

## 🐛 Troubleshooting

### "No module named 'langgraph'"
→ Run: `pip3 install -r requirements_job_agent.txt`

### "OPENAI_API_KEY not found"
→ Create `.env` file with your API key

### "python: command not found"
→ Use `python3` instead

## 📚 Next Steps

1. **Try Demo**: Run `simple_job_agent.py` 
2. **Install Full**: Run `pip3 install -r requirements_job_agent.txt`
3. **Add API Key**: Create `.env` with your OpenAI key
4. **Test It**: Run `job_search_agent.py`
5. **Customize**: Add more job platforms or features

## 🎯 Want to Extend It?

You can add more tools like:
- Resume parsing
- Application tracking
- Salary comparison
- Company reviews
- Interview preparation

Just follow the same pattern from `11_tools.ipynb`:
1. Define tool with `@tool` decorator
2. Add to tools list
3. Agent automatically uses it!

## 💡 Tips

- The agent maintains conversation context
- You can ask follow-up questions
- Be specific with job titles and locations
- Type 'exit' to quit

---

**Ready to start?** Run: `python3 simple_job_agent.py`

For questions, see: `JOB_AGENT_README.md`
