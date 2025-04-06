# BrainVibe Troubleshooting Guide

## 500 Internal Server Error in Analyze-Diff API

### Issue Description

The CLI was receiving a 500 Internal Server Error when sending changes to the API endpoint `/api/projects/{project_id}/analyze-diff/`. The server logs showed:

```
ERROR: Failed to analyze diff: name 'extract_topics_from_diff' is not defined
```

### Root Cause

The `extract_topics_from_diff` function was defined in `backend/main/utils/llm_utils.py` but wasn't properly imported in `backend/main/views.py` where the `AnalyzeDiffView` was trying to use it.

### Solution

1. Updated the imports in `backend/main/views.py`:

```python
from .utils.llm_utils import analyze_diff, extract_topics_from_diff
```

2. Enhanced error handling in the CLI's `track.py` file:
   - Added more detailed error reporting
   - Improved the user experience with better error messages
   - Added specific handling for connection errors

### How to Apply This Fix

1. Make sure both the function import and the function definition names match exactly
2. Restart the Django server after making changes
3. Test with a sample API call to ensure it's working properly
4. If API responses indicate any other errors, check the Django server logs

### Testing the Fix

You can test if the fix is working by running the provided test script:

```bash
python test_api.py YOUR_PROJECT_ID
```

This will send a simulated code diff to the API and verify it's processed correctly.

## "externally-managed-environment" Error When Installing CLI

### Issue Description

When trying to install the BrainVibe CLI with `pip install -e .`, you might get this error:

```
error: externally-managed-environment
```

### Root Cause

This happens on Linux distributions (like Ubuntu) that protect the system Python against direct package installations (PEP 668).

### Solution

Use a virtual environment for the CLI:

```bash
# Create a dedicated virtual environment for the CLI
python3 -m venv cli/venv
source cli/venv/bin/activate
cd cli
pip install -e .
```

OR use pipx for isolated application installation:

```bash
# Install pipx if not already installed
sudo apt install pipx

# Install the CLI tool
cd ~/personalgit/student_hack_25/Brain_Vibe
pipx install ./cli/
```

## General Troubleshooting Tips

### Backend Issues

1. Check the Django logs in the terminal where the server is running
2. Increase logging verbosity in `settings.py` for detailed error information
3. Test API endpoints directly using curl or Postman before using the CLI

### CLI Issues

1. Make sure the backend server is running before using the CLI
2. Check your project ID - it should match a project in the database
3. Try using the `--debug` flag with CLI commands for more verbose output 