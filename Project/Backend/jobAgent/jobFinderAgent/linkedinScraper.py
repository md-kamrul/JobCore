"""
Real-time LinkedIn Job Scraper
Uses public LinkedIn job search API and web scraping
"""

import requests
from bs4 import BeautifulSoup
import logging
import time
import json
from urllib.parse import urlencode, quote_plus
import random

logger = logging.getLogger(__name__)

class LinkedInJobScraper:
    """Scraper for LinkedIn job postings"""
    
    def __init__(self):
        self.base_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
    
    def build_search_url(self, keywords, location="", experience_level=None, job_type=None, start=0):
        """
        Build LinkedIn job search URL with parameters
        
        Args:
            keywords: Job title and skills
            location: Location or "Remote"
            experience_level: 1-6 (1=Internship, 2=Entry, 3=Associate, 4=Mid-Senior, 5=Director, 6=Executive)
            job_type: 1=On-site, 2=Remote, 3=Hybrid
            start: Pagination start
        """
        params = {
            'keywords': keywords,
            'location': location,
            'start': start
        }
        
        if experience_level:
            params['f_E'] = experience_level
        
        if job_type:
            params['f_WT'] = job_type
        
        # Remove empty parameters
        params = {k: v for k, v in params.items() if v}
        
        url = f"{self.base_url}?{urlencode(params)}"
        logger.info(f"Built search URL: {url}")
        return url
    
    def scrape_jobs(self, keywords, location="", experience_level=None, job_type=None, max_jobs=15):
        """
        Scrape LinkedIn jobs matching the criteria
        
        Returns:
            List of job dictionaries with title, company, location, description, url, posted_date
        """
        try:
            url = self.build_search_url(keywords, location, experience_level, job_type)
            
            logger.info(f"Scraping LinkedIn jobs for: {keywords} in {location or 'Any location'}")
            
            # Add random delay to avoid rate limiting
            time.sleep(random.uniform(1, 2))
            
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            jobs = []
            job_cards = soup.find_all('li')
            
            logger.info(f"Found {len(job_cards)} potential job cards")
            
            for card in job_cards[:max_jobs]:
                try:
                    job_data = self._parse_job_card(card)
                    if job_data:
                        jobs.append(job_data)
                        logger.debug(f"Parsed job: {job_data['title']} at {job_data['company']}")
                except Exception as e:
                    logger.debug(f"Error parsing job card: {str(e)}")
                    continue
            
            logger.info(f"Successfully scraped {len(jobs)} jobs")
            return jobs
            
        except requests.RequestException as e:
            logger.error(f"Network error while scraping LinkedIn: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error while scraping: {str(e)}", exc_info=True)
            return []
    
    def _parse_job_card(self, card):
        """Parse individual job card from HTML"""
        try:
            # Find job title
            title_elem = card.find('h3', class_='base-search-card__title')
            if not title_elem:
                return None
            title = title_elem.text.strip()
            
            # Find company name
            company_elem = card.find('h4', class_='base-search-card__subtitle')
            company = company_elem.text.strip() if company_elem else "Unknown Company"
            
            # Find location
            location_elem = card.find('span', class_='job-search-card__location')
            location = location_elem.text.strip() if location_elem else "Not specified"
            
            # Find job URL
            link_elem = card.find('a', class_='base-card__full-link')
            job_url = link_elem['href'] if link_elem and 'href' in link_elem.attrs else ""
            
            # Find posted date
            time_elem = card.find('time')
            posted_date = time_elem['datetime'] if time_elem and 'datetime' in time_elem.attrs else ""
            if not posted_date and time_elem:
                posted_date = time_elem.text.strip()
            
            # Find job description snippet
            description_elem = card.find('p', class_='base-search-card__snippet')
            description = description_elem.text.strip() if description_elem else ""
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'description': description,
                'url': job_url,
                'posted_date': posted_date or "Recently posted"
            }
            
        except Exception as e:
            logger.debug(f"Error parsing job card: {str(e)}")
            return None
    
    def format_jobs_for_display(self, jobs):
        """
        Format scraped jobs into markdown for display
        
        Args:
            jobs: List of job dictionaries
            
        Returns:
            Formatted markdown string
        """
        if not jobs:
            return "## 🎯 No Jobs Found\n\nNo jobs matching your criteria were found on LinkedIn at this time. Try:\n- Broadening your search terms\n- Adjusting location preferences\n- Checking back later"
        
        output = f"## 🎯 Found {len(jobs)} Real LinkedIn Jobs\n\n"
        
        for i, job in enumerate(jobs, 1):
            output += f"### {i}. {job['title']}\n"
            output += f"- **Company:** {job['company']}\n"
            output += f"- **Location:** {job['location']}\n"
            output += f"- **Posted:** {job['posted_date']}\n"
            
            if job['description']:
                # Truncate description if too long
                desc = job['description'][:200] + "..." if len(job['description']) > 200 else job['description']
                output += f"- **Description:** {desc}\n"
            
            if job['url']:
                output += f"- **Apply:** {job['url']}\n"
            
            output += "\n---\n\n"
        
        return output


async def scrape_linkedin_jobs_async(keywords, location="", experience_level=None, job_type=None, max_jobs=15):
    """
    Async wrapper for LinkedIn job scraping
    
    Args:
        keywords: Job search keywords
        location: Job location
        experience_level: Experience level filter
        job_type: Job type filter (remote, hybrid, onsite)
        max_jobs: Maximum number of jobs to return
        
    Returns:
        List of job dictionaries
    """
    import asyncio
    
    scraper = LinkedInJobScraper()
    
    # Run synchronous scraping in executor to not block event loop
    loop = asyncio.get_event_loop()
    jobs = await loop.run_in_executor(
        None, 
        scraper.scrape_jobs,
        keywords,
        location,
        experience_level,
        job_type,
        max_jobs
    )
    
    return jobs
