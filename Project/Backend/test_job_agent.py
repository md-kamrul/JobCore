"""
Job Search Agent - Test Examples
This script demonstrates how to use the job search agent programmatically
Similar to the test cases in 11_tools.ipynb
"""

from job_search_agent import job_search_agent
from langchain_core.messages import HumanMessage


def test_agent(query: str):
    """Helper function to test the agent with a query."""
    print(f"\n{'='*70}")
    print(f"QUERY: {query}")
    print('='*70)
    
    result = job_search_agent.invoke({"messages": [HumanMessage(content=query)]})
    response = result["messages"][-1].content
    
    print(f"\nRESPONSE:\n{response}")
    print(f"\n{'='*70}\n")
    return response


if __name__ == "__main__":
    print("\n🔍 JOB SEARCH AGENT - TEST EXAMPLES\n")
    
    # Test 1: Simple job search
    print("\n--- Test 1: Simple Indeed Job Search ---")
    test_agent("Find software engineer jobs in California")
    
    # Test 2: Remote job search
    print("\n--- Test 2: Remote Job Search ---")
    test_agent("Search for remote Python developer positions")
    
    # Test 3: LinkedIn specific search
    print("\n--- Test 3: LinkedIn Search ---")
    test_agent("Look for data scientist jobs on LinkedIn in New York")
    
    # Test 4: Job market insights
    print("\n--- Test 4: Market Insights ---")
    test_agent("What are the current trends for AI engineer jobs?")
    
    # Test 5: Multi-platform search
    print("\n--- Test 5: Multi-Platform Search ---")
    test_agent("Search for UX designer jobs on Indeed and Glassdoor in Seattle")
    
    # Test 6: Complex query with multiple tools
    print("\n--- Test 6: Complex Query ---")
    test_agent("Find remote full stack developer jobs and tell me about the job market trends")
    
    print("\n✅ All tests completed!")
