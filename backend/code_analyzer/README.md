# BrainVibe Code Analyzer with Google Gemini

This module provides integration with Google's Gemini AI to analyze code diffs and extract programming topics for the BrainVibe learning platform.

## Overview

The code analyzer uses Google Gemini AI to:

1. Analyze code diffs generated from git or code editors
2. Identify new programming concepts, libraries, and patterns
3. Establish prerequisite relationships between topics
4. Filter out topics the user has already learned or already knows they need to learn
5. Handle duplicates and unify similar topics

## Setup

### Requirements

- Python 3.8+
- Google Gemini API key

### Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set the Gemini API key:
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```

   Or create a `.env` file with:
   ```
   GEMINI_API_KEY=your-api-key-here
   ```

## Usage

### Command Line

You can use the test script to analyze a diff file:

```bash
python scripts/test_gemini_analyzer.py path/to/diff/file.diff
```

Options:
- `--completed path/to/completed_topics.txt` - File with already learned topics (one per line)
- `--to-learn path/to/to_learn_topics.txt` - File with topics already in the to-learn state
- `--api-key YOUR_API_KEY` - Specify Gemini API key (alternative to environment variable)
- `--output results.json` - Save analysis results to a JSON file

### API Integration

The analyzer is integrated into the BrainVibe API through the following endpoints:

- `POST /api/projects/{project_id}/analyze-diff/` - Analyze a code diff for a project

Example request:
```json
{
  "diff_content": "diff --git a/main.py b/main.py\n...",
  "file_path": "main.py",
  "change_id": "commit-123456"
}
```

## Prompt Template

The analyzer uses a carefully crafted prompt template to communicate with Gemini AI. The template:

1. Instructs Gemini to identify programming concepts from code diffs
2. Filters out topics the user already knows
3. Unifies similar or duplicate topics
4. Establishes prerequisite relationships

The prompt is designed to produce structured output that can be parsed and integrated into the BrainVibe knowledge graph.

## Response Format

Gemini returns a structured list of topics, which are parsed into the following JSON format:

```json
{
  "topics": [
    {
      "title": "React Context API",
      "description": "A way to share state across the component tree without prop drilling.",
      "prerequisites": ["React Basics", "React State Management"],
      "code_references": "Used in UserContext.js to manage global user state"
    },
    ...
  ]
}
```

## Extending the Analyzer

You can extend the analyzer by:

1. Modifying the prompt template in `gemini_analyzer.py`
2. Enhancing the response parser to extract additional information
3. Adding pre-processing steps to filter or enrich the diff content

## Troubleshooting

Common issues:

- **API Key Errors**: Ensure your Gemini API key is correctly set and has proper permissions
- **Empty Results**: Check the diff content for actual code changes (not just comments or whitespace)
- **Parsing Errors**: If Gemini's output format changes, you may need to update the response parser

For more help, see the Gemini API documentation. 