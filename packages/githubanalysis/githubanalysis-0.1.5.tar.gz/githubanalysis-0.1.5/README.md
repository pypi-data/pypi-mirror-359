# GitHub Analysis Tool

A powerful tool for analyzing Git repositories using LLM-powered insights. This tool provides detailed analysis of repository patterns, milestones, technical challenges, team dynamics, and more.

## What's New

- The report now always includes at least **three technical challenges** identified and described in detail.
- **All commits** (hash, author, message) are exported to a separate Excel file (`.xlsx`) alongside the main report.
- **Commit references** in the technical challenges section are now clickable URLs, allowing you to directly view the referenced commit on GitHub/GitLab.
- The **default report format is now Markdown** (if `--format` is not specified).

## Installation

```bash
pip install githubanalysis
```

## Usage

### Basic Analysis

```bash
githubanalysis https://github.com/username/repo.git
```

### Analysis with Date Range

```bash
githubanalysis https://github.com/username/repo.git \
    --start-date 2023-01-01 \
    --end-date 2024-03-20
```

### OpenAI API Key Configuration

You can provide your OpenAI API key in three ways:

1. Command line argument:
```bash
githubanalysis https://github.com/username/repo.git --openai-key your-api-key
```

2. Environment variable:
```bash
export OPENAI_API_KEY=your-api-key
githubanalysis https://github.com/username/repo.git
```

3. .env file:
Create a `.env` file in your working directory:
```
OPENAI_API_KEY=your-api-key
```

### Custom Prompts

You can customize the analysis prompts by providing a JSON file:

```bash
githubanalysis https://github.com/username/repo.git \
    --custom-prompts path/to/prompts.json
```

### Advanced Options

```bash
githubanalysis https://github.com/username/repo.git \
    --start-date 2023-01-01 \
    --end-date 2024-03-20 \
    --format markdown \
    --output-dir custom_reports \
    --openai-key your-api-key \
    --model gpt-4 \
    --custom-prompts path/to/prompts.json
```

## Output

The tool generates:

- A comprehensive report in Markdown (default) or JSON format, including:
  - Key technical challenges (minimum three, with detailed analysis)
  - Milestones
  - Team and contributor analysis
  - Code and commit statistics
  - Clickable commit links for easy navigation
- An **Excel file** with all commit hashes, authors, and messages for the analyzed period.

Reports and Excel files are saved in the specified output directory (default: `reports/`).

## Requirements

- Python 3.7+
- Git
- OpenAI API key (for LLM analysis)

## Dependencies

- gitpython
- openai
- python-dotenv
- argparse
- tqdm
- markdown
- pandas
- openpyxl
- matplotlib
- seaborn
- scikit-learn
- numpy
- nltk
- requests
- tiktoken