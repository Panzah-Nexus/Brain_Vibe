# BrainVibe Demo Guide

This guide will walk you through running the BrainVibe demo and understanding how the system works.

## Prerequisites

- Python 3.8 or higher
- Git installed
- Basic understanding of version control

## Running the Demo

1. Clone the BrainVibe repository:
```bash
git clone https://github.com/IbrahimMohammad-pi/brainvibe.git
cd brainvibe
```

2. Install the required dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Run the demo:
```bash
python3 -m code_tracker.demo
```

## What the Demo Shows

The demo creates a temporary project that demonstrates:

1. **Project Initialization**
   - Creates a new project with BrainVibe integration
   - Sets up git tracking
   - Configures Cursor integration

2. **Code Change Tracking**
   - Creates sample code files with different programming concepts
   - Demonstrates how changes are tracked automatically
   - Shows how the system captures code modifications

3. **Learning Graph Building**
   - The system analyzes code changes
   - Identifies programming topics and concepts
   - Updates the learning graph accordingly

## Sample Files Created

The demo creates two sample files:

1. `python_threading.py`
   - Demonstrates Python threading concepts
   - Shows error handling
   - Includes basic thread management

2. `js_async.js`
   - Shows JavaScript async/await patterns
   - Demonstrates error handling
   - Includes API fetching concepts

## What to Look For

After running the demo, you can:

1. Check the `.brainvibe` directory for:
   - Configuration files
   - Learning graph data
   - Change tracking information

2. Look at the git history:
```bash
cd brainvibe_demo
git log
```

3. View the learning graph updates in the `.brainvibe` directory

## Cleaning Up

To remove the demo project:
```bash
rm -rf brainvibe_demo
```

## Next Steps

After understanding the demo, you can:

1. Initialize your own project:
```bash
python -m code_tracker.cli init /path/to/your/project --cursor
```

2. Start using Cursor with BrainVibe integration
3. Monitor your learning progress through the web interface

## Troubleshooting

If you encounter any issues:

1. Make sure all dependencies are installed
2. Check that git is properly configured
3. Ensure you have write permissions in the demo directory
4. Check the console output for any error messages

## Support

For additional help or questions, please:
- Open an issue on GitHub
- Check the documentation
- Contact the development team 