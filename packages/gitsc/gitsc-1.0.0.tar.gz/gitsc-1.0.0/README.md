# gitsc (Git Semantic Commit)

A command-line tool that generates semantic commit messages using AI, following the Conventional Commits format.

## Features

- Generates semantic commit messages using Groq's LLaMA and Gemma models
- Multiple model options for different needs (speed vs. quality)
- Follows [Conventional Commits](https://www.conventionalcommits.org/) format
- Interactive mode with streamlined commit process
- Easy to use command-line interface
- Automatic API key management
- Command-line flags for quick configuration

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
2. Use the command-line flag: `gitsc --api-key "your-api-key"`
3. Create a `.env` file in your project with:
   ```
   GROQ_API_KEY=your_api_key_here
   ```

## Available Models

The tool supports multiple Groq models that you can choose from based on your needs. View the complete list of supported models at [Groq Models Documentation](https://console.groq.com/docs/models).

Currently supported models:
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

Running without arguments will show the help message and setup instructions:
```bash
gitsc
```

The tool will generate a semantic commit message and present you with options:
- Press `Enter` - Proceed with the commit (default action)
- `r` - Rephrase the commit message
- `k` - Reset/update API key
- `q` - Quit without committing

### Commit Message Format

The tool generates commit messages following the Conventional Commits format:
```
type(scope): summary
```

Where type is one of:
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