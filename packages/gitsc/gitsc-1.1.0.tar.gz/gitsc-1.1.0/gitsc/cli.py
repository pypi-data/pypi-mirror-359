import argparse
import subprocess
import sys
import os
import json
from groq import Groq
import appdirs
import keyring
from dotenv import load_dotenv
from prompt_toolkit import PromptSession
from prompt_toolkit.shortcuts import clear
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application import Application
from prompt_toolkit.layout import Layout
from prompt_toolkit.widgets import MenuContainer, MenuItem
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import radiolist_dialog
from rich.console import Console
from threading import Thread
import time

console = Console()
session = PromptSession()

SUPPORTED_MODELS = {
    "llama3-70b": "llama-3.3-70b-versatile",  # Most capable model
    "llama3-8b": "llama-3.1-8b-instant",      # Faster model
    "gemma-9b": "gemma2-9b-it",               # Alternative model
}

DEFAULT_MODEL = "llama3-70b"
APP_NAME = "gitsc"
APP_AUTHOR = "gitsc"

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
    
    # Store API key securely using keyring
    keyring.set_password(APP_NAME, "groq_api_key", api_key)
    
    print("✅ API key saved successfully.")
    return api_key

def check_api_key():
    # Try to get API key from keyring
    api_key = keyring.get_password(APP_NAME, "groq_api_key")
    
    if not api_key:
        return setup_api_key()
    return api_key

def generate_commit_messages(user_input: str, api_key: str, model: str = DEFAULT_MODEL, additional_context: str = "") -> list[dict]:
    client = Groq(api_key=api_key)
    
    system_message = (
        "Generate 3 semantic git commit messages in JSON format in schema {commits: [array of commit strings]}"
    )

    user_prompt = user_input
    if additional_context:
        user_prompt += f"\n\nAdditional context:\n{additional_context}"
    
    completion = client.chat.completions.create(
        model=SUPPORTED_MODELS[model],
        messages=[
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        temperature=1,
        max_completion_tokens=1024,
        top_p=1,
        response_format={"type": "json_object"},
        stop=None,
    )

    try:
        result = json.loads(completion.choices[0].message.content.strip())
        return result["commits"]
    except (json.JSONDecodeError, KeyError) as e:
        print("❌ Error parsing AI response. Retrying...", file=sys.stderr)
        return generate_commit_messages(user_input, api_key, model, additional_context)

def run_git_commit(message: str):
    try:
        subprocess.run(["git", "commit", "-m", message], check=True)
        print("✅ Commit successful.")
    except subprocess.CalledProcessError:
        print("❌ Git commit failed.", file=sys.stderr)
        sys.exit(1)

def print_commit_options(commits: list[str]):
    print("\nOptions:")
    for i, commit in enumerate(commits, 1):
        print(f"{i} - {commit}")
    print("c - Add more context to get better suggestions")
    print("r - Rephrase the commit")
    print("k - Reset API key")
    print("q - Quit")

def soft_reset_last_commit():
    try:
        subprocess.run(["git", "reset", "--soft", "HEAD~1"], check=True)
        print("🔙 Last commit undone (soft reset).")
    except subprocess.CalledProcessError:
        print("❌ Failed to undo last commit.", file=sys.stderr)


def format_commit_message(msg: str) -> str:
    """
    Clean and format commit message string.
    Removes surrounding quotes or whitespace.
    """
    return msg.strip().strip('"').strip("'")

def show_loading(message="🧠 Generating semantic commit messages..."):
    with console.status(message, spinner="dots"):
        time.sleep(0.5)  # Just to show spinner briefly


def handle_commit_interaction(initial_input: str, api_key: str, model: str):
    user_input = initial_input
    additional_context = ""
    current_api_key = api_key

    # Show loading spinner
    with console.status("🧠 Generating semantic commit messages...", spinner="dots"):
        current_commits = generate_commit_messages(user_input, current_api_key, model, additional_context)

    selected_index = 0
    show_menu = False

    def render():
        console.clear()
        console.print("\n🔧 [bold]Commit message suggestions:[/bold]\n")
        for i, commit in enumerate(current_commits):
            prefix = "👉" if i == selected_index else "   "
            style = "bold green" if i == selected_index else ""
            console.print(f"{prefix} {commit}", style=style)

        if show_menu:
            console.print("\n[dim]Other Options: (press space to collapse)[/dim]")
            console.print(" [c] Add more context")
            console.print(" [r] Rephrase the commit")
            console.print(" [b] Undo last commit (soft reset)")
            console.print(" [k] Reset API key")
            console.print(" [q] Quit")
        else:
            console.print("\n[dim](Press space to show other options)[/dim]")

    render()

    kb = KeyBindings()

    @kb.add("up")
    def _(event):
        nonlocal selected_index
        selected_index = (selected_index - 1) % len(current_commits)
        render()

    @kb.add("down")
    def _(event):
        nonlocal selected_index
        selected_index = (selected_index + 1) % len(current_commits)
        render()

    @kb.add("enter")
    def _(event):
        commit_msg = format_commit_message(current_commits[selected_index])
        run_git_commit(commit_msg)
        event.app.exit()

    @kb.add(" ")
    def _(event):
        nonlocal show_menu
        show_menu = not show_menu
        render()
        
    @kb.add("b")
    def _(event):
        soft_reset_last_commit()
        event.app.exit()

    @kb.add("c")
    def _(event):
        nonlocal additional_context, current_commits
        context = session.prompt("📝 Enter additional context: ")
        if context:
            additional_context += "\n" + context
            with console.status("🔄 Regenerating with more context...", spinner="bouncingBall"):
                current_commits = generate_commit_messages(user_input, current_api_key, model, additional_context)
            render()

    @kb.add("r")
    def _(event):
        nonlocal user_input, additional_context, current_commits
        user_input = session.prompt("🔁 New description for commit: ")
        additional_context = ""
        with console.status("🔄 Regenerating...", spinner="bouncingBall"):
            current_commits = generate_commit_messages(user_input, current_api_key, model)
        render()

    @kb.add("k")
    def _(event):
        nonlocal current_api_key, current_commits
        current_api_key = setup_api_key()
        with console.status("🔄 Regenerating...", spinner="bouncingBall"):
            current_commits = generate_commit_messages(user_input, current_api_key, model, additional_context)
        render()

    @kb.add("q")
    def _(event):
        print("❌ Commit aborted.")
        event.app.exit()

    # Start a minimal prompt loop to keep keybindings active
    from prompt_toolkit.application import Application
    from prompt_toolkit.layout import Layout
    from prompt_toolkit.layout.containers import Window
    from prompt_toolkit.layout.controls import FormattedTextControl

    layout = Layout(Window(content=FormattedTextControl("")))
    app = Application(layout=layout, key_bindings=kb, full_screen=False)
    app.run()
    

def main():
    parser = argparse.ArgumentParser(
        description=(
            "AI-powered semantic git commit tool using Groq's LLaMA models.\n\n"
            "This tool helps generate semantic commit messages in Conventional Commits format.\n"
            "To use this tool, you need a GROQ API key. You can get one by:\n"
            "1. Sign up at https://console.groq.com\n"
            "2. Navigate to API Keys section\n"
            "3. Create a new API key\n\n"
            "The tool will prompt you to enter your API key on first use.\n"
            "Your API key will be securely stored in your system's keyring.\n\n"
            "Available models (see https://console.groq.com/docs/models for details):\n"
            "- llama3-70b: LLaMA 3.3 70B Versatile (default, most capable)\n"
            "- llama3-8b: LLaMA 3.1 8B Instant (faster)\n"
            "- gemma-9b: Gemma 2 9B (alternative)\n\n"
            "Interactive options:\n"
            "- Select a number to use that commit message\n"
            "- 'c' to add more context for better suggestions\n"
            "- 'r' to rephrase with a new description\n"
            "- 'k' to update API key\n"
            "- 'q' to quit"
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
    args = parser.parse_args()

    # Handle API key setup if requested
    if args.api_key:
        keyring.set_password(APP_NAME, "groq_api_key", args.api_key)
        print("✅ API key updated successfully.")
        if not args.input:
            sys.exit(0)

    if not args.input:
        parser.print_help()
        sys.exit(1)


    api_key = check_api_key()
    user_input = " ".join(args.input)

    if user_input == "back":
        soft_reset_last_commit()
        sys.exit(0)
    else:
        check_git_repository()

    print(f"🧠 Generating semantic commit messages using {args.model}...")
    
    handle_commit_interaction(user_input, api_key, args.model)

if __name__ == "__main__":
    main() 