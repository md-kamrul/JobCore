import os
import logging
import asyncio
import json
from agents import (
    Agent,
    OpenAIChatCompletionsModel,
    Runner,
    set_tracing_disabled,
)
from agents.mcp import MCPServer
from openai import AsyncOpenAI
from linkedinScraper import scrape_linkedin_jobs_async, LinkedInJobScraper

logger = logging.getLogger(__name__)

async def run_job_search(mcp_server, user_query: str, linkedin_profile_url: str = None):
    """
    Run multi-agent job search based on user chat input.
    
    Args:
        mcp_server: Not used (kept for compatibility)
        user_query: User's chat message about job preferences
        linkedin_profile_url: Optional LinkedIn profile URL for personalization
    
    Returns:
        Formatted job search results
    """
    logger.info(f"Starting job search for query: {user_query}")
    
    api_key = os.environ["NEBIUS_API_KEY"]
    base_url = "https://api.tokenfactory.nebius.com/v1" 
    client = AsyncOpenAI(base_url=base_url, api_key=api_key)
    set_tracing_disabled(disabled=True)

    # Agent 1: Chat Understanding Agent
    chat_understanding_agent = Agent(
        name="Chat Understanding Agent",
        instructions="""You are a chat understanding agent that extracts job search criteria from user conversations.

        Your task is to analyze the user's message and extract:
        - Job title/role they're looking for
        - Required skills or technologies
        - Experience level (entry, mid, senior)
        - Location preferences (remote, specific city, etc.)
        - Company type preferences (startup, enterprise, etc.)
        - Any other relevant job search criteria

        Output format as JSON:
        {
            "job_title": "extracted job title",
            "keywords": ["keyword1", "keyword2"],
            "experience_level": "entry/mid/senior",
            "location": "location preference",
            "additional_criteria": "any other relevant info"
        }

        Rules:
        - Extract only information explicitly mentioned by the user
        - If information is not provided, use reasonable defaults
        - Be conversational and understand natural language
        - If the query is vague, make reasonable assumptions based on context
        """,
        model=OpenAIChatCompletionsModel(
            model="meta-llama/Llama-3.3-70B-Instruct",
            openai_client=client
        )
    )

    # Agent 2: LinkedIn Profile Context (optional)
    profile_context_agent = Agent(
        name="Profile Context Agent",
        instructions="""You are a profile context agent that provides additional context when a LinkedIn profile URL is provided.

        If a LinkedIn profile URL is provided:
        - Acknowledge that the profile was provided
        - Suggest that the user's experience level and skills will be considered
        - Provide general guidance on matching jobs to their likely profile
        
        Output format as JSON:
        {
            "profile_provided": true,
            "message": "LinkedIn profile URL received. Job recommendations will be tailored accordingly.",
            "guidance": "Consider experience level and skills when reviewing recommendations"
        }

        If no profile is provided, return:
        {
            "profile_provided": false,
            "message": "No profile provided. Recommendations will be based on search query only."
        }

        NOTE: Do not attempt to access external URLs. Just acknowledge the profile URL if provided.
        """,
        model=OpenAIChatCompletionsModel(
            model="meta-llama/Llama-3.3-70B-Instruct",
            openai_client=client
        )
    )

    # Agent 3: LinkedIn URL Generator
    linkedin_url_generator_agent = Agent(
        name="LinkedIn URL Generator",
        instructions="""You are a LinkedIn job search URL generator.

        Input: JSON from chat understanding agent and LinkedIn analyzer

        Create a LinkedIn jobs URL with proper query parameters:
        Base URL: "https://www.linkedin.com/jobs/search/"

        Parameters to include:
        - keywords: job title and key skills
        - location: location preference
        - f_E: experience level (1=Internship, 2=Entry, 3=Associate, 4=Mid-Senior, 5=Director, 6=Executive)
        - f_WT: work type (1=On-site, 2=Remote, 3=Hybrid)
        - position: 1 (pagination)
        - pageNum: 0 (first page)

        Example URL format:
        https://www.linkedin.com/jobs/search/?keywords=Software%20Engineer&location=Remote&f_E=2,3&f_WT=2

        Output format as JSON:
        {
            "linkedin_url": "generated URL",
            "search_summary": "brief description of search criteria"
        }

        Rules:
        - URL encode special characters
        - Combine job title and keywords for the keywords parameter
        - Map experience level appropriately
        - Include remote/hybrid filters if mentioned
        """,
        model=OpenAIChatCompletionsModel(
            model="meta-llama/Llama-3.3-70B-Instruct",
            openai_client=client
        )
    )

    # Agent 4: Search Parameters Extractor
    search_params_agent = Agent(
        name="Search Parameters Extractor",
        instructions="""You are a search parameters extractor that converts job criteria into LinkedIn search parameters.

        Input: Job search criteria from the chat understanding agent

        Extract and output:
        {
            "keywords": "job title and key skills combined",
            "location": "location or empty string for any",
            "experience_level": null or comma-separated values (1=Internship, 2=Entry, 3=Associate, 4=Mid-Senior, 5=Director, 6=Executive),
            "job_type": null or value (1=On-site, 2=Remote, 3=Hybrid)
        }

        Rules:
        - Combine job title and key skills into keywords field
        - Map experience level: entry->2, mid/associate->3, senior->4, director->5, executive->6
        - Map job type: remote->2, hybrid->3, onsite->1
        - If not specified, use null for experience_level and job_type
        - Keep location as provided or empty string for any location
        - Output ONLY valid JSON
        """,
        model=OpenAIChatCompletionsModel(
            model="meta-llama/Llama-3.3-70B-Instruct",
            openai_client=client
        )
    )

    # Agent 5: Job Formatter and Enhancer
    job_formatter_agent = Agent(
        name="Job Formatter",
        instructions="""You are a job formatter that displays recommended jobs in a clean format.

        Input: Job listings from the job generator

        Output ONLY the job listings section with this exact format:

        ## 🎯 Recommended Jobs

        [Insert all job listings here with full formatting - keep every job detail]

        Rules:
        - Output ONLY the "Recommended Jobs" section
        - Do NOT include search summary, tips, next steps, or any other sections
        - Keep all job details exactly as provided in the input
        - Maintain clean, professional formatting
        - Include all jobs from the input
        - Use the exact format from the job generator
        """,
        model=OpenAIChatCompletionsModel(
            model="meta-llama/Llama-3.3-70B-Instruct",
            openai_client=client
        )
    )

    try:
        # Step 1: Understand user's chat query
        logger.info("Understanding user query")
        chat_result = await Runner.run(
            starting_agent=chat_understanding_agent, 
            input=user_query
        )
        logger.info(f"Query understanding completed: {chat_result.final_output[:100]}...")

        # Step 2: Process LinkedIn profile context if provided
        profile_result = None
        if linkedin_profile_url:
            try:
                logger.info("Processing LinkedIn profile context")
                profile_result = await Runner.run(
                    starting_agent=profile_context_agent,
                    input=f"User provided LinkedIn profile URL: {linkedin_profile_url}. Acknowledge this for personalized recommendations."
                )
                logger.info("Profile context processed")
            except Exception as e:
                logger.warning(f"Profile context processing failed: {str(e)}, continuing without profile context")
                profile_result = None

        # Step 3: Generate LinkedIn search URL
        logger.info("Generating LinkedIn search URL")
        url_generator_input = f"""User Query Analysis: {chat_result.final_output}
        
        Profile Analysis: {profile_result.final_output if profile_result else 'No profile provided'}
        
        Generate a LinkedIn jobs search URL based on this information."""
        
        url_result = await Runner.run(
            starting_agent=linkedin_url_generator_agent,
            input=url_generator_input
        )
        logger.info(f"URL generation completed: {url_result.final_output[:100]}...")

        # Step 4: Extract search parameters for real scraping
        logger.info("Extracting search parameters")
        search_params_input = f"""User Search Criteria: {chat_result.final_output}
        
        Extract the search parameters for LinkedIn job scraping."""
        
        params_result = await Runner.run(
            starting_agent=search_params_agent,
            input=search_params_input
        )
        logger.info(f"Search parameters extracted: {params_result.final_output}")
        
        # Parse search parameters
        try:
            params_text = params_result.final_output.strip()
            # Extract JSON from markdown code blocks if present
            if "```json" in params_text:
                params_text = params_text.split("```json")[1].split("```")[0].strip()
            elif "```" in params_text:
                params_text = params_text.split("```")[1].split("```")[0].strip()
            
            search_params = json.loads(params_text)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing search parameters: {e}, using defaults")
            search_params = {
                "keywords": user_query,
                "location": "",
                "experience_level": None,
                "job_type": None
            }
        
        # Step 5: Scrape real LinkedIn jobs
        logger.info(f"Scraping LinkedIn with params: {search_params}")
        jobs = await scrape_linkedin_jobs_async(
            keywords=search_params.get("keywords", user_query),
            location=search_params.get("location", ""),
            experience_level=search_params.get("experience_level"),
            job_type=search_params.get("job_type"),
            max_jobs=15
        )
        logger.info(f"Scraped {len(jobs)} jobs from LinkedIn")
        
        # Format jobs for display
        scraper = LinkedInJobScraper()
        formatted_jobs = scraper.format_jobs_for_display(jobs)

        # Step 6: Polish and format results
        logger.info("Polishing final results")
        formatter_input = f"""Real LinkedIn Job Listings: {formatted_jobs}
        
        Present these REAL LinkedIn jobs under a "🎯 Recommended Jobs" section. Keep all job details intact."""
        
        final_result = await Runner.run(
            starting_agent=job_formatter_agent,
            input=formatter_input
        )
        logger.info("Result formatting completed")

        return final_result.final_output

    except KeyError as e:
        logger.error(f"Missing required environment variable: {str(e)}")
        return f"""# ❌ Configuration Error

Missing required environment variable: {str(e)}

Please make sure you have set up your `.env` file with:
- NEBIUS_API_KEY
- BRIGHT_DATA_API_KEY  
- BROWSER_AUTH

Check the README.md for setup instructions."""
        
    except Exception as e:
        logger.error(f"Error during job search: {str(e)}", exc_info=True)
        return f"""# ❌ Error During Job Search

An error occurred while processing your request:

**Error:** {str(e)}

**What you can try:**
1. Check that all API keys are correctly set in your .env file
2. Try a simpler search query
3. Check the terminal logs for more details
4. Try searching directly on [LinkedIn Jobs](https://www.linkedin.com/jobs/)

If the problem persists, please check the application logs."""
