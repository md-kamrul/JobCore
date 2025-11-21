from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import logging
from dotenv import load_dotenv
from jobAgent import run_job_search

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "message": "Job Agent API is running"})

@app.route('/api/search-jobs', methods=['POST'])
def search_jobs():
    """Search for jobs based on user query."""
    try:
        data = request.json
        user_query = data.get('query', '').strip()
        
        if not user_query:
            return jsonify({
                "error": "Query is required"
            }), 400
        
        logger.info(f"Received job search query: {user_query}")
        
        # Run the async job search
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(run_job_search(None, user_query, None))
            logger.info("Job search completed successfully")
            
            return jsonify({
                "success": True,
                "result": result,
                "query": user_query
            })
        finally:
            loop.close()
    
    except Exception as e:
        logger.error(f"Error processing job search: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "An error occurred while searching for jobs. Please try again."
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint that handles conversational queries."""
    try:
        data = request.json
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({
                "error": "Message is required"
            }), 400
        
        # Check if the message is a job search query
        job_keywords = ['job', 'jobs', 'position', 'role', 'work', 'career', 'hire', 'hiring', 'find', 'search', 'looking for']
        is_job_query = any(keyword in message.lower() for keyword in job_keywords)
        
        if is_job_query:
            logger.info(f"Processing as job search: {message}")
            
            # Run the job search
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(run_job_search(None, message, None))
                
                return jsonify({
                    "success": True,
                    "type": "job_results",
                    "message": result
                })
            finally:
                loop.close()
        else:
            # Return a helpful response for non-job queries
            return jsonify({
                "success": True,
                "type": "response",
                "message": "I'm here to help you find jobs! Please describe what kind of job you're looking for. For example: 'Find me remote Python developer jobs' or 'Looking for senior data scientist positions in New York'."
            })
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "An error occurred. Please try again."
        }), 500

if __name__ == '__main__':
    import os
    
    # Check API key
    if not os.getenv("NEBIUS_API_KEY"):
        logger.error("NEBIUS_API_KEY not found in .env file")
        print("❌ ERROR: NEBIUS_API_KEY not found in .env file")
        exit(1)
    
    logger.info("✅ API Key loaded successfully")
    logger.info("🚀 Starting Job Agent API Server...")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
