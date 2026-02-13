"""
Test script for LinkedIn scraper
"""
import asyncio
from linkedinScraper import scrape_linkedin_jobs_async, LinkedInJobScraper

async def test_scraper():
    print("Testing LinkedIn Job Scraper...")
    print("=" * 60)
    
    # Test 1: Remote Python Developer jobs
    print("\nTest 1: Remote Python Developer jobs")
    print("-" * 60)
    jobs = await scrape_linkedin_jobs_async(
        keywords="Python Developer",
        location="Remote",
        job_type=2,  # Remote
        max_jobs=5
    )
    
    if jobs:
        print(f"✅ Found {len(jobs)} jobs!")
        for i, job in enumerate(jobs[:3], 1):
            print(f"\n{i}. {job['title']}")
            print(f"   Company: {job['company']}")
            print(f"   Location: {job['location']}")
            print(f"   Posted: {job['posted_date']}")
    else:
        print("❌ No jobs found or scraping failed")
    
    # Test 2: Format for display
    print("\n" + "=" * 60)
    print("\nTest 2: Formatted output")
    print("-" * 60)
    scraper = LinkedInJobScraper()
    formatted = scraper.format_jobs_for_display(jobs)
    print(formatted)

if __name__ == "__main__":
    asyncio.run(test_scraper())
