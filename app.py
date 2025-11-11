import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import PyPDF2
from openai import OpenAI

# Load Environment Variables from .env.local explicitly
env_path = Path(__file__).parent / ".env.local"
print(f"Looking for .env.local at: {env_path}")
print(f"File exists: {env_path.exists()}")

load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    print("Missing OPENAI_API_KEY in .env.local. Exiting.")
    print(f"Current directory: {os.getcwd()}")
    print(f"Script directory: {Path(__file__).parent}")
    sys.exit(1)

print("✓ API Key loaded successfully!")

# Initialize OpenAI client
client = OpenAI(api_key=API_KEY)

# ---------------- PDF Extraction ----------------
def extract_pdf_text(pdf_path):
    reader = PyPDF2.PdfReader(pdf_path)
    text_parts = []
    for p in reader.pages:
        t = p.extract_text()
        if t:
            text_parts.append(t)
    return "\n".join(text_parts)

# ---------------- Prompt Templates ----------------
PROMPT_TEMPLATE_SUMMARY = """
Hey. Act like a skilled and very experienced ATS (Applicant Tracking System)
with a deep understanding of software engineering, data science, data analysis and big data engineering.
Evaluate the resume against the given job description. Consider the job market is competitive and provide
professional suggestions to improve the resume. Highlight strengths and weaknesses.
Output should be a single JSON-like string with keys: "JD Match", "MissingKeywords", "Profile Summary".

resume:
{text}

description:
{jd}
"""

PROMPT_TEMPLATE_PERCENT = """
You are an ATS scanner with deep knowledge of matching resumes to job descriptions.
Compare the resume to the job description and return:
1) A percentage match (as "JD Match": "xx%")
2) A list of missing/high-value keywords ("MissingKeywords": [...])
3) Final short thoughts ("Profile Summary": "...")

Resume:
{text}

Job description:
{jd}
"""

# ---------------- Input Handlers ----------------
def ask_job_description():
    """Get job description from user"""
    print("\n" + "="*50)
    print("Enter the job description (press Enter twice to finish):")
    print("="*50)
    lines = []
    empty_count = 0
    while True:
        try:
            line = input()
            if line == "":
                empty_count += 1
                if empty_count >= 2:
                    break
            else:
                empty_count = 0
            lines.append(line)
        except EOFError:
            break
    
    # Remove trailing empty lines
    while lines and lines[-1] == "":
        lines.pop()
    
    return "\n".join(lines).strip()

def ask_pdf_path():
    """Get PDF path from user"""
    while True:
        print("\nEnter path to your resume PDF file")
        print("(or type 'q' to quit): ", end="")
        p = input().strip()
        
        if p.lower() in ("q", "quit", "exit"):
            return None
        
        p = os.path.abspath(p)
        
        if os.path.exists(p) and p.lower().endswith(".pdf"):
            return p
        else:
            print(f"❌ Error: File not found or not a PDF")
            print(f"   Checked path: {p}")

# ---------------- OpenAI Call ----------------
def call_openai(prompt_text):
    """Call OpenAI API to get resume analysis"""
    try:
        print("\n⏳ Processing... (this may take a few seconds)")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert ATS (Applicant Tracking System) analyzer with deep HR knowledge."
                },
                {
                    "role": "user",
                    "content": prompt_text
                }
            ],
            temperature=0.7,
            max_tokens=1024
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ API error: {str(e)}"

# ---------------- Main Logic ----------------
def main():
    print("\n")
    print("=" * 60)
    print("     🎯 ATS RESUME EXPERT (OpenAI GPT VERSION)")
    print("=" * 60)
    
    # Get job description
    job_description = ask_job_description()
    if not job_description:
        print("\n❌ Job description is required. Exiting.")
        return

    # Get PDF path
    pdf_path = ask_pdf_path()
    if not pdf_path:
        print("\n❌ No PDF provided. Exiting.")
        return

    # Extract resume text
    print(f"\n📄 Reading resume from: {pdf_path}")
    try:
        resume_text = extract_pdf_text(pdf_path)
    except Exception as e:
        print(f"❌ Failed to read PDF: {str(e)}")
        return
    
    if not resume_text.strip():
        print("❌ No text extracted from PDF. Please check the file.")
        return

    print("✅ Resume loaded successfully!")

    # Main menu loop
    while True:
        print("\n" + "=" * 60)
        print("MENU - Choose an option:")
        print("=" * 60)
        print("1️⃣  Tell Me About the Resume")
        print("2️⃣  Percentage Match + Missing Keywords")
        print("3️⃣  Exit")
        print("=" * 60)
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == "1":
            prompt = PROMPT_TEMPLATE_SUMMARY.format(text=resume_text, jd=job_description)
            output = call_openai(prompt)
            print("\n" + "=" * 60)
            print("📋 RESUME ANALYSIS")
            print("=" * 60)
            print(output)
            print("=" * 60)
        
        elif choice == "2":
            prompt = PROMPT_TEMPLATE_PERCENT.format(text=resume_text, jd=job_description)
            output = call_openai(prompt)
            print("\n" + "=" * 60)
            print("📊 MATCH ANALYSIS")
            print("=" * 60)
            print(output)
            print("=" * 60)
        
        elif choice == "3":
            print("\n👋 Thank you for using ATS Resume Expert!")
            print("=" * 60)
            break
        
        else:
            print("\n❌ Invalid option. Please select 1, 2, or 3.")

# ---------------- Run Program ----------------
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Program interrupted by user. Exiting.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {str(e)}")
        sys.exit(1)
