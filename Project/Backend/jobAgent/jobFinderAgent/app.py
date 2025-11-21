import asyncio
import os
import logging
from dotenv import load_dotenv
from jobAgent import run_job_search

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_banner():
    """Print application banner."""
    print("\n" + "="*70)
    print("🔍 LinkedIn Job Finder Agent")
    print("Powered by AI Multi-Agent System")
    print("="*70 + "\n")

def print_menu():
    """Print main menu."""
    print("\n" + "-"*70)
    print("What would you like to do?")
    print("1. Search for jobs")
    print("2. View help & examples")
    print("3. Exit")
    print("-"*70)

def print_help():
    """Print help information."""
    print("\n" + "="*70)
    print("📚 HOW TO USE")
    print("="*70)
    print("""
1. Choose 'Search for jobs' from the menu
2. Describe what job you're looking for in natural language
3. Get 8-10 relevant job recommendations instantly

📝 EXAMPLE QUERIES:
- "Find me remote Python developer jobs"
- "Looking for senior data scientist positions in New York"
- "Entry level frontend jobs with React"
- "Machine learning engineer roles at startups"
- "Full-stack developer positions with TypeScript"
- "Backend developer with Node.js and MongoDB"

✨ FEATURES:
- AI understands natural language queries
- Generates relevant job recommendations from LinkedIn
- Shows company names, locations, and job details
- Displays results directly in terminal
- Fast and simple - no configuration needed
""")
    print("="*70 + "\n")

async def search_jobs_interactive():
    """Interactive job search."""
    print("\n" + "="*70)
    print("💬 JOB SEARCH")
    print("="*70 + "\n")
    
    # Get job search query
    print("Describe the job you're looking for:")
    print("(e.g., 'remote software engineer with Python and React')\n")
    user_query = input("Your query: ").strip()
    
    if not user_query:
        print("\n❌ Error: Please enter a job search query.\n")
        return
    
    print("\n" + "="*70)
    print("🔄 Searching LinkedIn for jobs... This may take 30-60 seconds.")
    print("="*70)
    print("""
1. Understanding your requirements...
2. Generating optimized search criteria...
3. Creating relevant job recommendations...
4. Formatting results...
""")
    
    try:
        result = await run_job_search(None, user_query, None)
        
        # Display results
        print("\n" + "="*70)
        print("✅ SEARCH COMPLETE")
        print("="*70 + "\n")
        print(result)
        print("\n" + "="*70 + "\n")
    
    except Exception as e:
        logger.error(f"Error searching for jobs: {str(e)}", exc_info=True)
        print(f"\n❌ Error: {str(e)}\n")
        print("""**Troubleshooting:**
- Verify your Nebius API key is set in .env file
- Check your internet connection
- Try a simpler search query
- Check the logs above for more details
""")

def main():
    """Main application loop."""
    print_banner()
    
    # Check API key
    if not os.getenv("NEBIUS_API_KEY"):
        print("❌ ERROR: NEBIUS_API_KEY not found in .env file")
        print("Please add your API key to the .env file and try again.\n")
        return
    
    print("✅ AI System Ready")
    print("📡 Connected to Nebius AI\n")
    
    while True:
        print_menu()
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == '1':
            asyncio.run(search_jobs_interactive())
        elif choice == '2':
            print_help()
        elif choice == '3':
            print("\n👋 Thank you for using LinkedIn Job Finder Agent!\n")
            break
        else:
            print("\n❌ Invalid choice. Please enter 1, 2, or 3.\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Exiting... Goodbye!\n")
