# Copyright 2025 DatSciX
# Main Entry Point for Timekeeper Analysis Agent

"""
Main entry point for running the Timekeeper Analysis Agent.

Usage:
    python main.py                    # Interactive CLI mode
    python main.py --ui streamlit     # Launch Streamlit UI
    python main.py --file data.csv    # Analyze specific file
"""

import argparse
import sys
from pathlib import Path
import logging
import asyncio

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from agents import timekeeper_director
from config.config import config


def setup_logging():
    """Configure application-wide logging."""
    log_config = config.logging
    log_file = Path(log_config.file)
    log_file.parent.mkdir(exist_ok=True)

    logging.basicConfig(
        level=log_config.level.upper(),
        format=log_config.format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file)
        ]
    )
    logging.info("Logging configured successfully.")


async def interactive_mode():
    """Run agent in interactive CLI mode."""
    print("=" * 80)
    print("TIMEKEEPER ANALYSIS AGENT - Interactive Mode")
    print("=" * 80)
    print("Powered by Google ADK + Ollama\n")

    # Initialize runner
    session_service = InMemorySessionService()
    runner = Runner(
        agent=timekeeper_director,
        app_name="timekeeper_analysis",
        session_service=session_service
    )

    # Create session
    session = await session_service.create_session(user_id="cli_user")
    print(f"Session created: {session.id}\n")

    print("Type 'exit' or 'quit' to end session")
    print("Type 'help' for usage instructions\n")

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit"]:
                print("\nThank you for using Timekeeper Analysis Agent!")
                break

            if user_input.lower() == "help":
                print("\nUSAGE INSTRUCTIONS:")
                print("1. Upload a file: 'Please analyze the file at /path/to/data.csv'")
                print("2. Ask questions about the analysis")
                print("3. Request specific reports or insights")
                print("4. Type 'exit' or 'quit' to end\n")
                continue

            # Stream response
            print("\nAgent: ", end="", flush=True)
            async for event in runner.stream_query(
                user_id="cli_user",
                session_id=session.id,
                message=user_input
            ):
                if hasattr(event, 'text'):
                    print(event.text, end="", flush=True)

            print("\n")

        except KeyboardInterrupt:
            print("\n\nSession interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}\n")


async def analyze_file(file_path: str, analysis_type: str = "comprehensive"):
    """Analyze a specific file and print results."""
    print(f"\nAnalyzing file: {file_path}")
    print(f"Analysis type: {analysis_type}\n")

    # Initialize runner
    session_service = InMemorySessionService()
    runner = Runner(
        agent=timekeeper_director,
        app_name="timekeeper_analysis",
        session_service=session_service
    )

    # Create session
    session = await session_service.create_session(user_id="batch_user")

    # Construct prompt
    prompt = f"Please analyze the timekeeper data file at {file_path}. "
    if analysis_type == "comprehensive":
        prompt += "Provide a comprehensive analysis including productivity, billing anomalies, and resource optimization."
    elif analysis_type == "productivity":
        prompt += "Focus on productivity analysis only."
    elif analysis_type == "billing":
        prompt += "Focus on detecting billing anomalies and compliance issues only."
    elif analysis_type == "optimization":
        prompt += "Focus on resource optimization recommendations only."

    # Run analysis
    print("Running analysis...\n")
    print("=" * 80)

    async for event in runner.stream_query(
        user_id="batch_user",
        session_id=session.id,
        message=prompt
    ):
        if hasattr(event, 'text'):
            print(event.text, end="", flush=True)

    print("\n" + "=" * 80)
    print("\nAnalysis complete!")


def launch_streamlit():
    """Launch Streamlit UI."""
    import subprocess

    ui_path = Path(__file__).parent / "ui" / "streamlit_app.py"

    print("Launching Streamlit UI...")
    print(f"UI will be available at: http://localhost:8501")
    print("Press Ctrl+C to stop the server\n")

    subprocess.run(["streamlit", "run", str(ui_path)])

def launch_adk_web():
    """Launch ADK Web UI."""
    import subprocess

    ui_path = Path(__file__).parent / "ui" / "adk_web_app.py"
    web_config = config.ui.adk_web

    print("Launching ADK Web UI...")
    print(f"UI will be available at: http://localhost:{web_config.port}")
    print("Press Ctrl+C to stop the server\n")

    subprocess.run([sys.executable, str(ui_path)])


def main():
    """Main entry point with argument parsing."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Timekeeper Analysis Agent - AI-powered timekeeper data analysis"
    )

    parser.add_argument(
        "--ui",
        choices=["streamlit", "adk_web"],
        help="Launch web UI (streamlit or adk_web)"
    )

    parser.add_argument(
        "--file",
        type=str,
        help="Path to timekeeper data file to analyze"
    )

    parser.add_argument(
        "--analysis-type",
        choices=["comprehensive", "productivity", "billing", "optimization"],
        default="comprehensive",
        help="Type of analysis to perform (default: comprehensive)"
    )

    args = parser.parse_args()

    # Route to appropriate mode
    if args.ui == "streamlit":
        launch_streamlit()
    elif args.ui == "adk_web":
        launch_adk_web()
    elif args.file:
        if not Path(args.file).exists():
            print(f"Error: File not found: {args.file}")
            sys.exit(1)
        asyncio.run(analyze_file(args.file, args.analysis_type))
    else:
        asyncio.run(interactive_mode())


if __name__ == "__main__":
    main()