# BrainVibe CLI

The BrainVibe CLI helps you track code changes and extract learning topics from your projects.

## Installation

Install the CLI tool with pip:

```bash
cd cli
pip install -e .
```

## Usage

### Create a project in the web interface

1. Go to http://localhost:5173/projects
2. Click "Create New Project"
3. Fill in the project details
4. After creating, note the project_id from the URL

### Initialize BrainVibe in your project directory

```bash
cd /path/to/your/project
brainvibe init --project-id <project_id>
```

This will:
- Create a `.brainvibe` directory with a configuration file
- Initialize Git if not already initialized
- Create an initial commit if none exists

### Track code changes

```bash
brainvibe track --watch
```

This will:
- Watch for changes in your project
- Create temporary commits to generate diffs
- Send diffs to the BrainVibe backend for analysis
- Extract learning topics from your code

### Run analysis once

If you don't want to watch continuously:

```bash
brainvibe track --one-shot
```

## Workflow

1. Create a project in the web UI to get a project_id
2. Run the CLI tool in your code folder with that project_id
3. The CLI sends code changes to the backend, which analyzes them
4. Topics appear in the web interface for that project

## How it works

The CLI uses a "shadow Git" approach to track changes. It:
1. Stages all files using `git add .`
2. Creates temporary commits with your changes
3. Extracts diffs from these commits
4. Sends diffs to the BrainVibe API for analysis
5. The backend uses Gemini to identify programming topics
6. Topics appear in your project's "Learning Topics" section

## Options

### Init Command

```
brainvibe init --project-id <project_id> [--api-url <api_url>]
```

- `--project-id`: Required. Project ID from the web interface
- `--api-url`: API URL. Default: http://localhost:8000/api

### Track Command

```
brainvibe track [--watch] [--one-shot]
```

- `--watch`: Watch for file changes continuously
- `--one-shot`: Run analysis once and exit 