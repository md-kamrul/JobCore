# Job Agent API Integration

This connects the Job Finder Agent backend with the React frontend chatbox.

## Architecture

- **Backend**: Flask API server that runs the multi-agent job search system
- **Frontend**: React chatbox interface in the Frontend folder
- **Communication**: REST API endpoints for job search

## Setup & Run

### 1. Install Backend Dependencies

```bash
cd /Users/kamrul/Developer/JobCore/Project/Backend/jobAgent/jobFinderAgent
pip install -r requirements.txt
```

### 2. Start the Backend API Server

```bash
python api.py
```

The API server will start on `http://localhost:5001`

### 3. Start the Frontend

```bash
cd /Users/kamrul/Developer/JobCore/Project/Frontend
npm install  # if not already done
npm run dev
```

The frontend will be available at `http://localhost:5173` (or the port Vite assigns)

### 4. Use the Application

1. Open the frontend in your browser
2. Navigate to the "Job Agent" page
3. Type your job search query in the chatbox
4. Wait 30-60 seconds for the AI to process and return results
5. View job recommendations directly in the chat

## API Endpoints

### POST `/api/chat`
Main chat endpoint that handles conversational job searches.

**Request:**
```json
{
  "message": "Find me remote Python developer jobs"
}
```

**Response:**
```json
{
  "success": true,
  "type": "job_results",
  "message": "## 🎯 Recommended Jobs\n\n..."
}
```

### POST `/api/search-jobs`
Direct job search endpoint.

**Request:**
```json
{
  "query": "senior data scientist in New York"
}
```

**Response:**
```json
{
  "success": true,
  "result": "## 🎯 Recommended Jobs\n\n...",
  "query": "senior data scientist in New York"
}
```

### GET `/api/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "message": "Job Agent API is running"
}
```

## Features

- ✅ Real-time job search through chat interface
- ✅ Natural language processing of job queries
- ✅ 8-10 relevant job recommendations per search
- ✅ LinkedIn job links and details
- ✅ Clean markdown-formatted results in chat
- ✅ Error handling and user feedback
- ✅ Loading states during search

## Troubleshooting

**Backend not starting:**
- Check that NEBIUS_API_KEY is set in `.env`
- Install missing dependencies: `pip install -r requirements.txt`

**Frontend can't connect:**
- Make sure backend is running on port 5001
- Check CORS is enabled (already configured)
- Check browser console for errors

**Slow responses:**
- Normal: AI agents need 30-60 seconds to process
- Check your internet connection
- Check terminal logs for errors

## Development

To modify the agent behavior, edit:
- `jobAgent.py` - Multi-agent system logic
- `api.py` - API endpoints and request handling
- `JobAgent.jsx` - Frontend chat interface
