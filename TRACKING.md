# BrainVibe Git Tracking System

BrainVibe uses a "ghost git" tracking system to monitor your code changes in real-time and analyze them for learning topics. This document explains the tracking mechanism and its configuration options.

## How It Works

1. **File Change Detection**: BrainVibe watches your project directory for file changes using the [chokidar](https://github.com/paulmillr/chokidar) library.

2. **Temporary Commits**: When changes are detected, BrainVibe creates temporary git commits to generate diffs, then immediately resets them, ensuring your actual git history remains unchanged.

3. **Change Analysis**: The generated diffs are sent to the BrainVibe backend for topic extraction using Gemini AI.

## Configuration Options

### Commit Interval

By default, BrainVibe analyzes code changes:
- Immediately after detecting a file change (with a 3-second debounce delay)
- Every 2 minutes if there are pending changes

You can customize the interval using the `--interval` option:

```bash
brainvibe track --interval 300000  # Analyze every 5 minutes (300,000 ms)
```

### Ignore Patterns

BrainVibe automatically ignores certain files and directories to avoid analyzing irrelevant content:

- Dependencies (node_modules, venv, etc.)
- Build artifacts (dist, build, etc.)
- Configuration files
- Binary files
- Documentation

#### Custom Ignore Patterns

You can customize which files to ignore by creating a `.brainvibeignore` file in your project root. This file follows a format similar to `.gitignore`:

```
# Dependencies
node_modules
package-lock.json

# Build directories
dist
build

# Documentation
*.md
*.txt
```

You can also specify a custom ignore file path:

```bash
brainvibe track --ignore-file .custom_ignore
```

## Best Practices

1. **Granular Tracking**: For the best learning experience, make small, focused code changes that introduce one concept at a time.

2. **Ignore Irrelevant Content**: Keep your `.brainvibeignore` file updated to exclude files that don't contain valuable learning content.

3. **Customize the Interval**: If you find the default 2-minute interval too frequent or not frequent enough, adjust it to match your workflow.

4. **Project-Specific Tuning**: Different projects may benefit from different tracking configurations - experiment to find what works best.

## Debugging Tracking Issues

If you encounter issues with topic extraction:

1. Check your `.brainvibeignore` file to ensure you're not excluding relevant files.

2. Use the BrainVibe CLI with verbose logging:

```bash
DEBUG=true brainvibe track
```

3. Review the terminal output for information about which files are being tracked and analyzed.

## How to Stop Tracking

To stop BrainVibe from tracking your code, press `Ctrl+C` in the terminal where you're running the `brainvibe track` command. 