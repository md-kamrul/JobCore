"""
Simplified Job Search Agent - Terminal Chat Interface
This is a standalone version that can run with minimal dependencies
"""

def print_banner():
    """Print welcome banner."""
    print("\n" + "="*70)
    print("🔍 JOB SEARCH AI AGENT")
    print("="*70)
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
    print("="*70 + "\n")


def simulate_job_search(query: str) -> str:
    """
    Simulate job search response for demonstration.
    Replace this with actual agent logic once dependencies are installed.
    """
    query_lower = query.lower()
    
    # Determine what the user is asking for
    platforms = []
    if 'indeed' in query_lower:
        platforms.append('Indeed')
    if 'linkedin' in query_lower:
        platforms.append('LinkedIn')
    if 'glassdoor' in query_lower:
        platforms.append('Glassdoor')
    
    if not platforms:
        platforms = ['Indeed', 'LinkedIn', 'Glassdoor']
    
    # Check if it's a remote job search
    is_remote = 'remote' in query_lower or 'work from home' in query_lower
    
    # Check if asking for insights
    is_insights = 'trend' in query_lower or 'insight' in query_lower or 'salary' in query_lower or 'market' in query_lower
    
    # Build response
    response = []
    
    if is_insights:
        response.append("📊 Job Market Insights:")
        response.append("I would search for market trends and salary information for your query.")
        response.append("(This requires the full agent with LangChain/LangGraph installed)")
    else:
        response.append(f"🔍 Searching for jobs on: {', '.join(platforms)}")
        if is_remote:
            response.append("   Focus: Remote positions")
        response.append("")
        response.append("I would search these platforms and return relevant job listings.")
        response.append("(This requires the full agent with LangChain/LangGraph installed)")
    
    response.append("")
    response.append("💡 To enable full functionality, please:")
    response.append("   1. Install dependencies: pip install -r requirements_job_agent.txt")
    response.append("   2. Create .env file with your OPENAI_API_KEY")
    response.append("   3. Run: python job_search_agent.py")
    
    return "\n".join(response)


def run_simple_chat():
    """Run a simple terminal chat interface."""
    print_banner()
    
    print("🚀 Running in DEMO mode (install dependencies for full features)\n")
    
    while True:
        # Get user input
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋 Thank you for using Job Search AI Agent!")
            break
        
        # Check for exit commands
        if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
            print("\n👋 Thank you for using Job Search AI Agent. Good luck with your job search!")
            break
        
        # Skip empty inputs
        if not user_input:
            continue
        
        # Generate response
        print("\nAgent:", flush=True)
        response = simulate_job_search(user_input)
        print(response)
        print()


def main():
    """Main entry point."""
    try:
        # Try to import the full agent
        from job_search_agent import job_search_agent, run_chat
        from langchain_core.messages import HumanMessage
        
        print("✅ Full agent loaded! Starting with all features enabled...\n")
        run_chat()
        
    except ImportError as e:
        # Fall back to demo mode
        print(f"⚠️  Some dependencies not installed: {e}")
        print("Running in DEMO mode...\n")
        run_simple_chat()


if __name__ == "__main__":
    main()
