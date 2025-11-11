from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
from dotenv import load_dotenv

from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool

# Use the modern ddgs API (renamed from duckduckgo_search)
from ddgs import DDGS

import requests
import json

# Load environment variables
load_dotenv()

# Initialize LLM
llm = ChatOpenAI(temperature=0.7)

# ============= TOOLS =============

@tool
def search_jobs_indeed(query: str, location: str = "United States") -> dict:
    """
    Search for jobs on Indeed using a web scraping approach via DuckDuckGo search.
    Args:
        query: Job title or keywords (e.g., "software engineer", "data scientist")
        location: Location for job search (default: "United States")
    Returns:
        Dictionary with job search results
    """
    try:
        with DDGS() as ddgs:
            search_query = f"site:indeed.com {query} jobs {location}"
            results = list(ddgs.text(search_query, max_results=5))
            formatted_results = "\n".join([f"• {r['title']}: {r['href']}" for r in results])
            return {
                "platform": "Indeed",
                "query": query,
                "location": location,
                "results": formatted_results if formatted_results else "No results found"
            }
    except Exception as e:
        return {"error": f"Error searching Indeed: {str(e)}"}


@tool
def search_jobs_linkedin(query: str, location: str = "United States") -> dict:
    """
    Search for jobs on LinkedIn using a web scraping approach via DuckDuckGo search.
    Args:
        query: Job title or keywords (e.g., "python developer", "marketing manager")
        location: Location for job search (default: "United States")
    Returns:
        Dictionary with job search results
    """
    try:
        with DDGS() as ddgs:
            search_query = f"site:linkedin.com/jobs {query} {location}"
            results = list(ddgs.text(search_query, max_results=5))
            formatted_results = "\n".join([f"• {r['title']}: {r['href']}" for r in results])
            return {
                "platform": "LinkedIn",
                "query": query,
                "location": location,
                "results": formatted_results if formatted_results else "No results found"
            }
    except Exception as e:
        return {"error": f"Error searching LinkedIn: {str(e)}"}


@tool
def search_jobs_glassdoor(query: str, location: str = "United States") -> dict:
    """
    Search for jobs on Glassdoor using a web scraping approach via DuckDuckGo search.
    Args:
        query: Job title or keywords (e.g., "full stack developer", "project manager")
        location: Location for job search (default: "United States")
    Returns:
        Dictionary with job search results
    """
    try:
        with DDGS() as ddgs:
            search_query = f"site:glassdoor.com {query} jobs {location}"
            results = list(ddgs.text(search_query, max_results=5))
            formatted_results = "\n".join([f"• {r['title']}: {r['href']}" for r in results])
            return {
                "platform": "Glassdoor",
                "query": query,
                "location": location,
                "results": formatted_results if formatted_results else "No results found"
            }
    except Exception as e:
        return {"error": f"Error searching Glassdoor: {str(e)}"}


@tool
def get_job_market_insights(job_title: str) -> dict:
    """
    Get general job market insights and trends for a specific job title using web search.
    Args:
        job_title: The job title to research (e.g., "data analyst", "UX designer")
    Returns:
        Dictionary with market insights and trends
    """
    try:
        with DDGS() as ddgs:
            search_query = f"{job_title} job market trends salary 2025"
            results = list(ddgs.text(search_query, max_results=5))
            formatted_results = "\n".join([f"• {r['title']}: {r['body'][:150]}..." for r in results])
            return {
                "job_title": job_title,
                "market_insights": formatted_results if formatted_results else "No insights found"
            }
    except Exception as e:
        return {"error": f"Error getting job market insights: {str(e)}"}


@tool
def search_remote_jobs(query: str) -> dict:
    """
    Search specifically for remote job opportunities across multiple platforms.
    Args:
        query: Job title or keywords (e.g., "remote software engineer", "work from home")
    Returns:
        Dictionary with remote job search results
    """
    try:
        with DDGS() as ddgs:
            search_query = f"remote {query} jobs hiring 2025"
            results = list(ddgs.text(search_query, max_results=5))
            formatted_results = "\n".join([f"• {r['title']}: {r['href']}" for r in results])
            return {
                "job_type": "Remote",
                "query": query,
                "results": formatted_results if formatted_results else "No results found"
            }
    except Exception as e:
        return {"error": f"Error searching remote jobs: {str(e)}"}


# ============= AGENT SETUP =============

# Make tool list
tools = [
    search_jobs_indeed,
    search_jobs_linkedin,
    search_jobs_glassdoor,
    get_job_market_insights,
    search_remote_jobs
]

# Make the LLM tool-aware
llm_with_tools = llm.bind_tools(tools)


# State definition
class JobSearchState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# Graph nodes
def chat_node(state: JobSearchState):
    """LLM node that may answer or request a tool call."""
    messages = state['messages']
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


tool_node = ToolNode(tools)  # Executes tool calls


# Build the graph
graph = StateGraph(JobSearchState)
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat_node")
graph.add_conditional_edges("chat_node", tools_condition)
graph.add_edge("tools", "chat_node")

# Compile the agent
job_search_agent = graph.compile()


# ============= TERMINAL CHAT INTERFACE =============

def run_chat():
    """Run a basic terminal-based chat interface for the job search agent."""
    print("=" * 60)
    print("🔍 JOB SEARCH AI AGENT")
    print("=" * 60)
    print("\nWelcome! I can help you search for jobs across multiple platforms.")
    print("\nAvailable capabilities:")
    print("  • Search jobs on Indeed, LinkedIn, Glassdoor")
    print("  • Find remote job opportunities")
    print("  • Get job market insights and salary trends")
    print("\nExamples:")
    print("  - 'Find software engineer jobs in New York'")
    print("  - 'Search for remote data scientist positions'")
    print("  - 'What are the trends for product manager jobs?'")
    print("\nType 'exit' or 'quit' to end the conversation.")
    print("=" * 60)
    print()
    
    # Conversation history
    conversation_history = []
    
    while True:
        # Get user input
        user_input = input("You: ").strip()
        
        # Check for exit commands
        if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
            print("\n👋 Thank you for using Job Search AI Agent. Good luck with your job search!")
            break
        
        # Skip empty inputs
        if not user_input:
            continue
        
        # Add user message to history
        conversation_history.append(HumanMessage(content=user_input))
        
        try:
            # Invoke the agent
            print("\nAgent: ", end="", flush=True)
            result = job_search_agent.invoke({"messages": conversation_history})
            
            # Get the last message (agent's response)
            agent_response = result["messages"][-1]
            
            # Update conversation history with full result
            conversation_history = result["messages"]
            
            # Display the response
            if hasattr(agent_response, 'content'):
                print(agent_response.content)
            else:
                print(str(agent_response))
            
            print()  # Empty line for readability
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Please try again with a different query.\n")


# ============= MAIN EXECUTION =============

if __name__ == "__main__":
    run_chat()
