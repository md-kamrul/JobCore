"""
Google Jobs Scraper using SerpAPI
"""
import os
import logging
from serpapi import Client
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class GoogleJobScraper:
    """Scraper for Google Jobs postings (demo version)"""
    def __init__(self):
        self.api_key = os.getenv("SERPAPI_API_KEY")
        if not self.api_key:
            raise ValueError("SERPAPI_API_KEY not set in .env file.")
        self.engine = "google_jobs"

    def build_search_params(self, keywords, location=None):
        query = f'{keywords}' + (f' {location}' if location else '')
        params = {
            "engine": self.engine,
            "q": query,
            "hl": "en",
            "api_key": self.api_key
        }
        return params

    def scrape_jobs(self, keywords, location=None, max_jobs=5):
        params = self.build_search_params(keywords, location)
        logger.info(f"Searching Google Jobs via SerpAPI for: {keywords} in {location or 'Any location'}")
        client = Client(api_key=self.api_key)
        results = client.search(params)
        jobs_results = results.get("jobs_results", [])
        jobs = []
        for job in jobs_results[:max_jobs]:
            jobs.append({
                'title': job.get('title', 'Unknown Title'),
                'company': job.get('company_name', 'Unknown Company'),
                'location': job.get('location', 'Not specified'),
                'description': job.get('description', ''),
                'url': job.get('apply_options', [{}])[0].get('link', job.get('link', '')),
            })
        return jobs

def scrape_google_jobs_async(keywords, location=None, max_jobs=5):
    import asyncio
    scraper = GoogleJobScraper()
    loop = asyncio.get_event_loop()
    jobs = loop.run_in_executor(
        None,
        scraper.scrape_jobs,
        keywords,
        location,
        max_jobs
    )
    return jobs
