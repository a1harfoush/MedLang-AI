#!/usr/bin/env python3
"""
MedLang Setup Script
This script helps set up the MedLang medical chatbot environment.
"""

import os
import sys
import subprocess
import json

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required.")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def install_requirements():
    """Install required packages."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed successfully")
    except subprocess.CalledProcessError:
        print("Error: Failed to install requirements")
        sys.exit(1)

def setup_environment():
    """Set up environment variables."""
    env_file = ".env"
    if not os.path.exists(env_file):
        print("Creating .env file template...")
        with open(env_file, "w") as f:
            f.write("""# MedLang Environment Variables
# Add your API keys here

# Groq API Key (required)
GROQ_API_KEY=your_groq_api_key_here

# Google Cloud Project ID (required for translation)
GOOGLE_CLOUD_PROJECT_ID=your_project_id_here

# Langchain Tracing (optional)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langchain_api_key_here
""")
        print("✓ .env file created. Please add your API keys.")
    else:
        print("✓ .env file already exists")

def main():
    """Main setup function."""
    print("🩺 MedLang Setup Script")
    print("=" * 30)
    
    check_python_version()
    install_requirements()
    setup_environment()
    
    print("\n✅ Setup completed!")
    print("\nNext steps:")
    print("1. Add your API keys to the .env file")
    print("2. Run the application with: chainlit run app.py")
    print("3. Or use Docker: docker build -t medlang . && docker run -p 5100:5100 medlang")

if __name__ == "__main__":
    main()