# LinkedIn Job Finder Agent

A multi-agent system that searches and scrapes LinkedIn jobs based on natural language chat input.

## Features

- 🤖 **Multi-Agent Architecture**: Uses specialized AI agents for different tasks
- 💬 **Natural Language Interface**: Just describe what you're looking for in plain English
- 🌐 **Real-Time LinkedIn Scraping**: Scrapes actual job postings from LinkedIn in real-time
- 🎯 **Smart Job Search**: Finds up to 15 real LinkedIn jobs matching your criteria
- 👤 **Conversational AI**: Chat naturally and the AI decides when to search for jobs
- 📊 **Clean Results**: Well-formatted job listings with company, location, and direct apply links
- 🔗 **Direct Apply Links**: Click through to apply directly on LinkedIn
- 🚀 **REST API**: Integrates seamlessly with frontend applications

## How It Works

1. **Conversational Agent**: Handles natural chat and determines when you want to search for jobs
2. **Chat Understanding Agent**: Extracts job search criteria from your natural language query
3. **Search Parameters Extractor**: Converts criteria into LinkedIn search parameters
4. **Real-Time LinkedIn Scraper**: Scrapes actual job postings from LinkedIn's public job board
5. **Job Formatter**: Formats real LinkedIn jobs into a clean, readable report with direct apply links

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Setup

The Nebius API key is **pre-configured** in the application for the AI agents. LinkedIn job scraping works without any additional API keys!

```bash
cp .env.example .env
```

**Note**: The system scrapes LinkedIn's public job board directly using web scraping. No additional API keys are needed for job search functionality.

### 3. Run the Application

```bash
python3 app.py
```

Or with the virtual environment:

```bash
source venv/bin/activate
python app.py
```

Or directly:

```bash
venv/bin/python3 app.py
```

## Usage

### Option 1: Terminal CLI (Standalone)

1. Run the application: `python app.py`
2. Choose "1" to search for jobs
3. Describe what job you're looking for in natural language
4. Wait 30-60 seconds while the AI agents process your request
5. View formatted results with job recommendations
6. Choose "2" for help or "3" to exit

### Option 2: Web API + Frontend Integration

1. Start the backend API server:
   ```bash
   python api.py
   # OR use the startup script
   ./start_api.sh
   ```

2. Start the React frontend:
   ```bash
   cd ../../Frontend
   npm run dev
   ```

3. Open the frontend in your browser and navigate to Job Agent page
4. Type your job search query in the chatbox
5. View results in real-time

See [API_INTEGRATION.md](./API_INTEGRATION.md) for detailed API documentation.

### Example Queries

- "Find me remote Python developer jobs"
- "Looking for senior data scientist positions in New York"
- "Entry level frontend jobs with React"
- "Machine learning engineer roles at startups"
- "Full-stack developer positions with TypeScript"

## API Configuration

### ✅ Pre-Configured (No Setup Needed)
- **Nebius API Key**: Already configured in the application
- **AI Model**: Meta LLaMA 3.3 70B via Nebius
- You can start using the app immediately after installation!

### 🔧 Optional Setup (For Advanced Features)

If you want to enable automated LinkedIn scraping (optional):

#### Bright Data API Key
- Sign up at [Bright Data](https://brightdata.com/)
- Create a new project
- Generate API credentials
- Create a "Web Unlocker" zone named `mcp_unlocker`
- Add to `.env` file

#### Browser Auth
- Provided by Bright Data during setup
- Found in your Bright Data dashboard
- Add to `.env` file

**Note:** Even without these optional keys, the app provides intelligent LinkedIn search URLs you can use directly.

## Architecture

The system uses a multi-agent architecture powered by:
- **Nebius LLaMA 3.3 70B**: For AI reasoning and understanding
- **Bright Data MCP**: For web scraping and data extraction
- **Streamlit**: For the user interface
- **OpenAI Agents Framework**: For agent orchestration

## Output Format

Results are displayed in markdown format with:
- Search summary
- Job listings with:
  - Job title
  - Company name
  - Location
  - Job type
  - Posted date
  - Description snippet
  - Application link
- Quick application tips

## Notes

- The scraper respects LinkedIn's structure and only extracts publicly available job listings
- Results are limited to the first 10 most relevant jobs
- Processing may take 1-2 minutes depending on query complexity
- All results can be downloaded as markdown files

## What to Expect

### ✨ Features:
- ✅ AI understands your job search query using natural language
- ✅ Generates 8-10 relevant, realistic job recommendations based on your criteria
- ✅ Uses real company names and creates professional job postings
- ✅ Provides optimized LinkedIn search URLs with proper filters
- ✅ Creates clickable links to view jobs on LinkedIn
- ✅ Intelligent query understanding (location, experience level, skills, etc.)
- ✅ Optional LinkedIn profile analysis for personalized results
- ✅ Includes job descriptions, company names, locations, and application links
- ✅ Provides actionable application tips

### 🎯 Job Recommendations:
- The AI generates realistic job listings that match your search criteria
- Uses actual companies known to hire for the requested positions
- Includes relevant job details: title, company, location, type, description
- Provides LinkedIn-style job links for direct application
- Always shows 8-10 relevant opportunities per search

## Troubleshooting

- **"NEBIUS_API_KEY not found"**: Make sure you have created the .env file and added your API key
- **"Error searching for jobs"**: Verify your Nebius API key is valid in the .env file
- **Slow response**: The AI agents need 30-60 seconds to process your request - this is normal
- **No jobs displayed**: Check the terminal output for detailed error messages
- **Import errors**: Make sure you've installed all requirements: `pip install -r requirements.txt`
- **Connection issues**: Ensure you have a stable internet connection for the Nebius API
- **KeyboardInterrupt**: Press Ctrl+C to exit the application at any time

## License

MIT
