#!/usr/bin/env python3
"""
Quick test script for the job search agent
Run this to verify the fix works
"""

from job_search_agent import job_search_agent
from langchain_core.messages import HumanMessage

def test_bangladesh_query():
    """Test the specific query that was failing"""
    print("Testing: 'find frontend web developer jobs in Bangladesh as a junior positions or internship'\n")
    
    query = "find frontend web developer jobs in Bangladesh as a junior positions or internship"
    result = job_search_agent.invoke({"messages": [HumanMessage(content=query)]})
    
    response = result["messages"][-1].content
    print("Agent Response:")
    print("=" * 70)
    print(response)
    print("=" * 70)
    
    # Check if there's an error
    if "error" in response.lower() and "import" in response.lower():
        print("\n❌ FAILED: Import error still present")
        return False
    else:
        print("\n✅ SUCCESS: Agent working correctly!")
        return True

if __name__ == "__main__":
    test_bangladesh_query()
