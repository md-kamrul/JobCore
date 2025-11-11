from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import PyPDF2
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import io
import json
import sys

# Load environment variables
env_path = Path(__file__).parent / ".env.local"
print(f"Looking for .env.local at: {env_path}")
print(f"File exists: {env_path.exists()}")

load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize OpenAI client
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    print("❌ Missing OPENAI_API_KEY in .env.local")
    print(f"Current directory: {os.getcwd()}")
    print(f"Script directory: {Path(__file__).parent}")
    sys.exit(1)
else:
    print("✅ API Key loaded successfully!")

client = OpenAI(api_key=API_KEY)

# ============== PROMPT TEMPLATES ==============

PROMPT_TEMPLATE_SUMMARY = """
Hey. Act like a skilled and very experienced ATS (Applicant Tracking System)
with a deep understanding of software engineering, data science, data analysis and big data engineering.
Evaluate the resume against the given job description. Consider the job market is competitive and provide
professional suggestions to improve the resume. Highlight strengths and weaknesses.

IMPORTANT: You must respond with ONLY a valid JSON object with exactly these keys:
- "JD Match": a percentage string (e.g., "85%")
- "MissingKeywords": an array of strings (e.g., ["Python", "AWS", "Docker"])
- "Profile Summary": a detailed string with strengths, weaknesses, and recommendations

Resume:
{text}

Job Description:
{jd}

Respond with ONLY the JSON object, no other text.
"""

PROMPT_TEMPLATE_PERCENT = """
You are an ATS scanner with deep knowledge of matching resumes to job descriptions.
Compare the resume to the job description.

IMPORTANT: You must respond with ONLY a valid JSON object with exactly these keys:
- "JD Match": a percentage string (e.g., "78%")
- "MissingKeywords": an array of important missing keywords (e.g., ["agile", "leadership", "roadmap"])
- "Profile Summary": a brief summary with match analysis and recommendations

Resume:
{text}

Job Description:
{jd}

Respond with ONLY the JSON object, no other text or markdown.
"""

# ============== HELPER FUNCTIONS ==============

def extract_pdf_text(pdf_file):
    """Extract text from PDF file"""
    try:
        # Read the file content
        pdf_content = pdf_file.read()
        pdf_file_obj = io.BytesIO(pdf_content)
        
        # Extract text using PyPDF2
        pdf_reader = PyPDF2.PdfReader(pdf_file_obj)
        text_parts = []
        
        for page_num, page in enumerate(pdf_reader.pages):
            try:
                text = page.extract_text()
                if text and text.strip():
                    text_parts.append(text)
            except Exception as page_error:
                print(f"Warning: Could not extract text from page {page_num + 1}: {str(page_error)}")
                continue
        
        full_text = "\n".join(text_parts)
        
        if not full_text.strip():
            raise Exception("No text could be extracted from the PDF. The file might be an image-based PDF or corrupted.")
        
        return full_text
    
    except Exception as e:
        raise Exception(f"Failed to extract PDF text: {str(e)}")

def call_openai(prompt_text):
    """Call OpenAI API and return the response"""
    try:
        print("📡 Calling OpenAI API...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert ATS (Applicant Tracking System) analyzer with deep HR and recruitment knowledge. You always respond with valid JSON format only."
                },
                {
                    "role": "user",
                    "content": prompt_text
                }
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        result = response.choices[0].message.content
        print("✅ OpenAI response received")
        return result
    
    except Exception as e:
        print(f"❌ OpenAI API error: {str(e)}")
        raise Exception(f"OpenAI API error: {str(e)}")

def parse_json_response(text):
    """Parse JSON from OpenAI response, handling markdown code blocks"""
    try:
        # Remove markdown code blocks if present
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        
        if text.endswith("```"):
            text = text[:-3]
        
        text = text.strip()
        
        # Try to parse as JSON
        return json.loads(text)
    
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON parsing failed: {str(e)}")
        print(f"Raw response: {text[:200]}...")
        
        # Return a structured error response
        return {
            "JD Match": "N/A",
            "MissingKeywords": [],
            "Profile Summary": text
        }

# ============== API ROUTES ==============

@app.route('/check_resume', methods=['POST'])
def check_resume():
    """Main endpoint to check resume"""
    try:
        print("\n" + "="*60)
        print("📥 Received resume check request")
        print("="*60)
        
        # Validate file upload
        if 'file' not in request.files:
            print("❌ No file in request")
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            print("❌ Empty filename")
            return jsonify({"error": "No file selected"}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            print("❌ Invalid file type")
            return jsonify({"error": "Only PDF files are supported"}), 400
        
        # Get form data
        position = request.form.get('position', '').strip()
        description = request.form.get('description', '').strip()
        analysis_type = request.form.get('analysis_type', 'summary').strip()
        
        print(f"📋 Position: {position}")
        print(f"📄 Description length: {len(description)} chars")
        print(f"🔍 Analysis type: {analysis_type}")
        
        # Validate required fields
        if not position:
            print("❌ Position is required")
            return jsonify({"error": "Target position is required"}), 400
        
        # Extract text from PDF
        print("📖 Extracting text from PDF...")
        try:
            resume_text = extract_pdf_text(file)
            print(f"✅ Extracted {len(resume_text)} characters from PDF")
        except Exception as extract_error:
            print(f"❌ PDF extraction failed: {str(extract_error)}")
            return jsonify({"error": str(extract_error)}), 400
        
        # Build job description
        if description:
            job_description = f"Position: {position}\n\nJob Description:\n{description}"
        else:
            job_description = f"Position: {position}\n\nNo specific job description provided. Please analyze the resume for this position in general."
        
        # Choose prompt template based on analysis type
        if analysis_type == 'percentage':
            print("🎯 Using percentage match analysis")
            prompt = PROMPT_TEMPLATE_PERCENT.format(text=resume_text, jd=job_description)
        else:
            print("📊 Using full summary analysis")
            prompt = PROMPT_TEMPLATE_SUMMARY.format(text=resume_text, jd=job_description)
        
        # Call OpenAI API
        try:
            analysis_result = call_openai(prompt)
        except Exception as openai_error:
            print(f"❌ OpenAI call failed: {str(openai_error)}")
            return jsonify({"error": f"AI analysis failed: {str(openai_error)}"}), 500
        
        # Parse the JSON response
        parsed_result = parse_json_response(analysis_result)
        
        print("✅ Analysis complete!")
        print("="*60 + "\n")
        
        # Return response
        return jsonify({
            "success": True,
            "analysis": json.dumps(parsed_result),
            "recommendation": json.dumps(parsed_result),
            "parsed": parsed_result
        }), 200
    
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        print("="*60 + "\n")
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "running",
        "message": "ATS Resume Checker Backend is healthy!",
        "openai_configured": API_KEY is not None
    }), 200

@app.route('/', methods=['GET'])
def home():
    """Home endpoint with API documentation"""
    return jsonify({
        "message": "ATS Resume Checker API",
        "version": "1.0.0",
        "endpoints": {
            "POST /check_resume": {
                "description": "Analyze a resume against a job description",
                "parameters": {
                    "file": "PDF file (required)",
                    "position": "Target position (required)",
                    "description": "Job description (optional)",
                    "analysis_type": "'summary' or 'percentage' (optional, default: 'summary')"
                }
            },
            "GET /health": {
                "description": "Check if the backend is running"
            }
        }
    }), 200

# ============== ERROR HANDLERS ==============

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500

# ============== MAIN ==============

if __name__ == '__main__':
    print("\n" + "="*70)
    print("     🎯 ATS RESUME CHECKER BACKEND - OpenAI GPT Version")
    print("="*70)
    print(f"✅ OpenAI API Key: {'Configured' if API_KEY else 'Missing'}")
    print(f"🌐 Backend URL: http://localhost:5000")
    print(f"🏥 Health Check: http://localhost:5000/health")
    print(f"📚 API Docs: http://localhost:5000/")
    print("="*70)
    print("🚀 Starting Flask server...")
    print("="*70 + "\n")
    
    try:
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n\n⚠️  Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {str(e)}")
