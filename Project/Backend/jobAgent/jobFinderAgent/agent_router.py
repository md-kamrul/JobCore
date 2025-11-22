"""
Agent Router using LangGraph, LangChain, and OpenAI SDK
Routes user queries to the appropriate agent (job search or other task agents)
"""
from langchain.llms import OpenAI
from langgraph.graph import StateGraph, ToolNode, RouterNode
from langchain.tools import Tool

# Define Job Search Tool
class JobSearchTool(Tool):
    name = "job_search"
    description = "Handles job search queries."
    def _run(self, query: str):
        # Integrate with your job search logic here
        return f"[Job Search Results for: {query}]"

# Define Resume Checker Tool
class ResumeCheckerTool(Tool):
    name = "resume_checker"
    description = "Handles resume/cv checking queries."
    def _run(self, query: str):
        return "💡 If you want to check or improve your resume, try our website's Resume Checker option!"

# Router logic (can be replaced with LLM-based intent detection)
def route_query(query: str):
    q = query.lower()
    if any(word in q for word in ["job", "search", "find work", "position", "vacancy"]):
        return "job_search"
    elif any(word in q for word in ["resume", "cv", "checker"]):
        return "resume_checker"
    else:
        return "default"

# Build LangGraph router
job_search_tool = JobSearchTool()
resume_checker_tool = ResumeCheckerTool()

tools = {
    "job_search": job_search_tool,
    "resume_checker": resume_checker_tool,
}

class AgentRouter:
    def __init__(self, tools):
        self.tools = tools
    def handle(self, query):
        agent_name = route_query(query)
        if agent_name in self.tools:
            return self.tools[agent_name].run(query)
        return "Sorry, I can't assist with that."

# Example usage
if __name__ == "__main__":
    router = AgentRouter(tools)
    print(router.handle("Can you check my resume?"))
    print(router.handle("Find me a software job in Berlin."))
    print(router.handle("Tell me a joke."))
