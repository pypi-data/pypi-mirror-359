import argparse
import subprocess
import sys
import os
from groq import Groq
from dotenv import load_dotenv
from . import __version__

SUPPORTED_MODELS = {
    "llama3-70b": "llama-3.3-70b-versatile",  # Most capable model
    "llama3-8b": "llama-3.1-8b-instant",      # Faster model
    "gemma-9b": "gemma2-9b-it",               # Alternative model
}

DEFAULT_MODEL = "llama3-70b"

def check_git_repository():
    try:
        # Check if git is installed
        subprocess.run(["git", "--version"], check=True, capture_output=True)
        
        # Check if current directory is a git repository
        subprocess.run(["git", "rev-parse", "--git-dir"], check=True, capture_output=True)
        
        # Check if there are staged changes
        result = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)
        if result.returncode == 0:
            print("❌ No staged changes found. Stage your changes with 'git add' first.", file=sys.stderr)
            sys.exit(1)
            
    except subprocess.CalledProcessError:
        print("❌ Not a git repository or git is not installed.", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Git is not installed or not in PATH.", file=sys.stderr)
        sys.exit(1)

def setup_api_key():
    print("🔑 GROQ API Key Setup")
    api_key = input("Enter your GROQ API key: ").strip()
    
    with open(".env", "w") as f:
        f.write(f"GROQ_API_KEY={api_key}")
    
    print("✅ API key saved successfully.")
    return api_key

def check_api_key():
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        return setup_api_key()
    return api_key

def generate_commit_message(user_input: str, api_key: str, model: str = DEFAULT_MODEL) -> str:
    client = Groq(api_key=api_key)
    
    system_message = (
        "Generate a semantic git commit message in Conventional Commits format "
        "(type(scope): summary). Use one of: feat, fix, chore, docs, refactor, test, "
        "style, perf, or ci for type.\n"
        "Keep the summary under 72 characters, written in imperative mood.\n"
    )
    
    completion = client.chat.completions.create(
        model=SUPPORTED_MODELS[model],
        messages=[
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": user_input
            }
        ],
        temperature=1,
        max_completion_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )

    return completion.choices[0].message.content.strip()

def run_git_commit(message: str):
    try:
        subprocess.run(["git", "commit", "-m", message], check=True)
        print("✅ Commit successful.")
    except subprocess.CalledProcessError:
        print("❌ Git commit failed.", file=sys.stderr)
        sys.exit(1)

def print_commit_options():
    print("\nOptions:")
    print("Enter - Proceed with commit")
    print("r - Rephrase the commit")
    print("k - Reset API key")
    print("q - Quit")

def handle_commit_interaction(initial_input: str, api_key: str, model: str):
    current_message = generate_commit_message(initial_input, api_key, model)
    user_input = initial_input
    current_api_key = api_key
    
    while True:
        print("\n🔧 Current commit message:\n")
        print(current_message)
        print_commit_options()
        
        choice = input("\nEnter your choice (press Enter to commit): ").strip().lower()
        
        if choice == '':  # Empty string means Enter was pressed
            run_git_commit(current_message)
            break
        elif choice == 'q':
            print("❌ Commit aborted.")
            break
        elif choice == 'r':
            print("\nEnter new description for the commit:")
            user_input = input("> ").strip()
            current_message = generate_commit_message(user_input, current_api_key, model)
        elif choice == 'k':
            current_api_key = setup_api_key()
            current_message = generate_commit_message(user_input, current_api_key, model)
        else:
            print("❌ Invalid option. Please try again.")

def main():
    parser = argparse.ArgumentParser(
        description=(
            "AI-powered semantic git commit tool using Groq's LLaMA models.\n\n"
            "This tool helps generate semantic commit messages in Conventional Commits format.\n"
            "To use this tool, you need a GROQ API key. You can get one by:\n"
            "1. Sign up at https://console.groq.com\n"
            "2. Navigate to API Keys section\n"
            "3. Create a new API key\n\n"
            "The tool will prompt you to enter your API key on first use.\n\n"
            "Available models (see https://console.groq.com/docs/models for details):\n"
            "- llama3-70b: LLaMA 3.3 70B Versatile (default, most capable)\n"
            "- llama3-8b: LLaMA 3.1 8B Instant (faster)\n"
            "- gemma-9b: Gemma 2 9B (alternative)"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("input", nargs="*", help="Describe what this commit does")
    parser.add_argument("--api-key", "-k", help="Set new GROQ API key")
    parser.add_argument(
        "--model", "-m",
        choices=list(SUPPORTED_MODELS.keys()),
        default=DEFAULT_MODEL,
        help="Select the AI model to use (default: %(default)s)"
    )
    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    args = parser.parse_args()

    # Handle API key setup if requested
    if args.api_key:
        with open(".env", "w") as f:
            f.write(f"GROQ_API_KEY={args.api_key}")
        print("✅ API key updated successfully.")
        if not args.input:
            sys.exit(0)

    if not args.input:
        parser.print_help()
        sys.exit(1)

    # Check git repository status
    check_git_repository()

    api_key = check_api_key()
    user_input = " ".join(args.input)
    print(f"🧠 Generating semantic commit message using {args.model}...")
    
    handle_commit_interaction(user_input, api_key, args.model)

if __name__ == "__main__":
    main() 