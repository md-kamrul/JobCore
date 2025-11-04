from dotenv import load_dotenv
load_dotenv()
import base64
import os
import io
from PIL import Image 
import pdf2image
import google.generativeai as genai
import sys

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input_text, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content([input_text, pdf_content[0], prompt])
    return response.text

def input_pdf_setup(pdf_path):
    """Convert PDF to image and prepare for Gemini API"""
    try:
        # Convert the PDF to image
        images = pdf2image.convert_from_path(pdf_path)
        first_page = images[0]

        # Convert to bytes
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()  # encode to base64
            }
        ]
        return pdf_parts
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return None

def validate_pdf_path(pdf_path):
    """Validate if the PDF path exists and is accessible"""
    if not pdf_path.strip():
        return False
    if not os.path.exists(pdf_path):
        return False
    if not pdf_path.lower().endswith('.pdf'):
        return False
    return True

def get_pdf_path():
    """Get and validate PDF path from user"""
    while True:
        pdf_path = input("\nEnter the full path to your resume (PDF): ").strip()
        
        # Allow user to exit
        if pdf_path.lower() in ['q', 'quit', 'exit']:
            return None
            
        # Convert relative path to absolute path
        pdf_path = os.path.abspath(pdf_path)
        
        if validate_pdf_path(pdf_path):
            return pdf_path
        else:
            print("\nError: Invalid PDF file path. Please ensure:")
            print("1. The file exists")
            print("2. The path is correct")
            print("3. The file is a PDF")
            print("4. Type 'q' to quit")

def get_job_description():
    """Get job description from user with better handling"""
    print("\nEnter the job description (press Enter twice when finished):")
    lines = []
    while True:
        line = input()
        if line == "":
            if lines and lines[-1] == "":  # Two consecutive empty lines
                break
        lines.append(line)
    return "\n".join(lines[:-1])  # Remove the last empty line

def main():
    print("\n=== ATS Resume Expert ===\n")
    
    # Get job description
    job_description = get_job_description()
    if not job_description.strip():
        print("Job description cannot be empty. Exiting...")
        return

    # Get PDF path
    pdf_path = get_pdf_path()
    if not pdf_path:
        print("\nExiting program...")
        return

    # Process PDF
    pdf_content = input_pdf_setup(pdf_path)
    if not pdf_content:
        print("Failed to process PDF. Exiting...")
        return

    while True:
        print("\nChoose an option:")
        print("1. Tell Me About the Resume")
        print("2. Percentage Match")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()

        input_prompt1 = """
        You are an experienced Technical Human Resource Manager,your task is to review the provided resume against the job description. 
        Please share your professional evaluation on whether the candidate's profile aligns with the role. 
        Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
        """

        input_prompt3 = """
        You are an skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality, 
        your task is to evaluate the resume against the provided job description. give me the percentage of match if the resume matches
        the job description. First the output should come as percentage and then keywords missing and last final thoughts.
        """

        try:
            if choice == "1":
                response = get_gemini_response(input_prompt1, pdf_content, job_description)
                print("\nResponse:")
                print("-" * 50)
                print(response)
                print("-" * 50)
            
            elif choice == "2":
                response = get_gemini_response(input_prompt3, pdf_content, job_description)
                print("\nResponse:")
                print("-" * 50)
                print(response)
                print("-" * 50)
            
            elif choice == "3":
                print("\nThank you for using ATS Resume Expert!")
                break
            
            else:
                print("\nInvalid choice. Please try again.")

        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram terminated by user.")
        sys.exit(0)
