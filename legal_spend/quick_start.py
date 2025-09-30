import sys

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import google.adk
        import pandas
        import ollama
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e.name}")
        print("\nPlease install all dependencies with:")
        print("  pip install -r requirements.txt")
        return False

def main():
    print("🚀 Legal Spend AI Agent Quick Start")
    print("=" * 50)
    
    if not check_dependencies():
        sys.exit(1)
    
    print("\n✅ Dependencies are installed.")
    print("\n📋 To run the agent, use the ADK command-line tool:")
    print("\n   adk run legal_spend")
    
    print("\nOnce the agent starts, you can instruct it to analyze a file. For example:")
    print("\n   'Analyze the legal data in C:\\path\\to\\your\\file.csv'\n")

if __name__ == "__main__":
    main()

