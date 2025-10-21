"""
Setup script for LinkedIn Article Generation System
"""

import os
import subprocess
import sys


def install_requirements():
    """Install required packages"""
    print("Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        return False


def check_api_key():
    """Check if OpenAI API key is set"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY environment variable not set!")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return False
    else:
        print("OpenAI API key found!")
        return True


def create_env_file():
    """Create .env file template"""
    env_content = """# LinkedIn Article Generation System Environment Variables
OPENAI_API_KEY=your-openai-api-key-here

# Optional: Custom model settings
# OPENAI_MODEL=gpt-4-turbo-preview
# OPENAI_TEMPERATURE=0.7
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("Created .env file template")
    print("Please edit .env file with your actual API key")


def run_test():
    """Run a basic test to verify installation"""
    print("Running basic test...")
    try:
        from workflow import LinkedInArticleWorkflow
        print("Import successful!")
        return True
    except ImportError as e:
        print(f"Import failed: {e}")
        return False


def main():
    """Main setup function"""
    print("LinkedIn Article Generation System Setup")
    print("=" * 50)
    
    # Install requirements
    if not install_requirements():
        print("Setup failed at requirements installation")
        return
    
    # Check API key
    if not check_api_key():
        create_env_file()
        print("\nPlease set your OpenAI API key and run setup again")
        return
    
    # Run test
    if not run_test():
        print("Setup failed at import test")
        return
    
    print("\nSetup completed successfully!")
    print("\nNext steps:")
    print("1. Set your OPENAI_API_KEY environment variable")
    print("2. Run: python examples/basic_usage.py")
    print("3. Run: python examples/export_example.py")


if __name__ == "__main__":
    main()
