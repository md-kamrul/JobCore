#!/usr/bin/env python3
"""
Quick Start Guide for Job Search Agent
Run this script to check if your environment is set up correctly
"""

import sys
import os

def check_environment():
    """Check if the environment is properly configured."""
    print("🔍 Job Search Agent - Environment Check\n")
    print("="*60)
    
    errors = []
    warnings = []
    
    # Check Python version
    print("\n1. Checking Python version...")
    py_version = sys.version_info
    if py_version.major == 3 and py_version.minor >= 8:
        print(f"   ✅ Python {py_version.major}.{py_version.minor}.{py_version.micro}")
    else:
        errors.append(f"   ❌ Python 3.8+ required, found {py_version.major}.{py_version.minor}")
    
    # Check for required packages
    print("\n2. Checking required packages...")
    required_packages = [
        'langgraph',
        'langchain',
        'langchain_openai',
        'langchain_community',
        'langchain_core',
        'dotenv',
        'requests'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            if package == 'dotenv':
                __import__('dotenv')
            else:
                __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - NOT INSTALLED")
            missing_packages.append(package)
    
    if missing_packages:
        errors.append("\n   Missing packages. Install with:")
        errors.append("   pip install -r requirements_job_agent.txt")
    
    # Check for .env file
    print("\n3. Checking environment variables...")
    if os.path.exists('.env'):
        print("   ✅ .env file found")
        
        # Try to load and check for OPENAI_API_KEY
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key and api_key != 'your_openai_api_key_here':
                print("   ✅ OPENAI_API_KEY is set")
            else:
                warnings.append("   ⚠️  OPENAI_API_KEY not properly configured in .env")
        except:
            warnings.append("   ⚠️  Could not verify OPENAI_API_KEY")
    else:
        warnings.append("   ⚠️  .env file not found")
        warnings.append("   Copy .env.example to .env and add your OpenAI API key")
    
    # Print summary
    print("\n" + "="*60)
    print("\n📊 SUMMARY\n")
    
    if not errors and not warnings:
        print("✅ All checks passed! You're ready to use the Job Search Agent.")
        print("\nRun the agent with:")
        print("   python job_search_agent.py")
        print("\nOr run tests with:")
        print("   python test_job_agent.py")
    else:
        if errors:
            print("❌ ERRORS:")
            for error in errors:
                print(error)
        
        if warnings:
            print("\n⚠️  WARNINGS:")
            for warning in warnings:
                print(warning)
        
        print("\n📖 See JOB_AGENT_README.md for setup instructions")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    check_environment()
