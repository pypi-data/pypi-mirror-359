# gitsc (Git Semantic Commit)

A command-line tool that generates semantic commit messages using AI, following the Conventional Commits format.

## Features

- Generates 3 different semantic commit message suggestions
- Interactive UI with keyboard navigation (up/down arrows)
- Uses Groq's LLaMA and Gemma models
- Multiple model options for different needs (speed vs. quality)
- Follows [Conventional Commits](https://www.conventionalcommits.org/) format
- Interactive mode with streamlined commit process
- Easy to use command-line interface
- Secure API key storage using system keyring
- Command-line flags for quick configuration
- Support for undoing last commit

## Installation

You can install gitsc directly from PyPI:
```bash
pip install gitsc
```

Or install from source:
```bash
git clone https://github.com/prxdyut/gitsc.git
cd gitsc
pip install -e .
```

## GROQ API Key Setup

You'll need a GROQ API key to use this tool. Here's how to get one:

1. Sign up at [Groq Console](https://console.groq.com)
2. Navigate to the API Keys section
3. Create a new API key

You can set up your API key in several ways:
1. Let the tool prompt you on first use
2. Use the command-line flag: `gitsc --api-key "your-api-key"` or `-k`
3. Use the interactive menu to update the key at any time

Your API key will be securely stored in your system's keyring.

## Available Models

The tool supports multiple Groq models that you can choose from based on your needs:

- `llama3-70b` (default): LLaMA 3.3 70B Versatile - Most capable, best quality
- `llama3-8b`: LLaMA 3.1 8B Instant - Faster response time
- `gemma-9b`: Gemma 2 9B - Alternative model

Select a model using the `--model` or `-m` flag:
```bash
gitsc -m llama3-8b "your commit message"
```

## Usage

Basic usage:
```bash
gitsc "Your commit description here"
```

With model selection:
```bash
gitsc -m llama3-8b "add new user authentication feature"
```

Update API key:
```bash
gitsc -k "your-new-api-key"
```

Undo last commit:
```bash
gitsc back
```

Running without arguments will show the help message and setup instructions:
```bash
gitsc
```

### Interactive Interface

The tool provides an interactive interface with the following controls:

- `↑/↓` - Navigate between suggestions
- `Enter` - Select and use the highlighted commit message
- `Space` - Toggle additional options menu
- `c` - Add more context to get better suggestions
- `r` - Generate new suggestions with a different description
- `b` - Undo last commit (soft reset)
- `k` - Reset/update API key
- `q` - Quit without committing

### Interactive Context Refinement

If none of the initial suggestions match what you're looking for, you can use the `c` option to provide additional context. This allows you to:
1. Add more details about the changes
2. Explain the purpose or impact
3. Provide technical context
4. Clarify the scope

The tool will then generate new suggestions taking this additional context into account. You can add context multiple times to refine the suggestions further.

### Commit Message Format

The tool generates commit messages following the Conventional Commits format:
```
type(scope): summary
```

Common types include:
- feat: New features
- fix: Bug fixes
- chore: Maintenance tasks
- docs: Documentation changes
- refactor: Code restructuring
- test: Adding or modifying tests
- style: Code style changes
- perf: Performance improvements
- ci: CI/CD changes

## Requirements

- Python 3.6+
- Groq API key
- Git installed and configured

## License

MIT License - See LICENSE file for details 