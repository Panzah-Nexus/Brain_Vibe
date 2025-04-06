#!/usr/bin/env python
"""
Test script for the Gemini Topic Analyzer
"""

import os
import sys
import json
import argparse
from dotenv import load_dotenv

# Add the backend directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from code_analyzer.gemini_analyzer import GeminiTopicAnalyzer

def main():
    """Main function for the test script"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Test the Gemini Topic Analyzer')
    parser.add_argument('diff_file', help='Path to a file containing a git diff')
    parser.add_argument('--completed', help='Path to a file containing completed topics (one per line)')
    parser.add_argument('--to-learn', help='Path to a file containing to-learn topics (one per line)')
    parser.add_argument('--api-key', help='Google Gemini API key (defaults to GEMINI_API_KEY env var)')
    parser.add_argument('--output', help='Output file for the analysis results (JSON format)')
    args = parser.parse_args()
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Get the API key
    api_key = args.api_key or os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("Error: Gemini API key not provided")
        print("Either set the GEMINI_API_KEY environment variable or use the --api-key option")
        return 1
    
    # Load the diff
    try:
        with open(args.diff_file, 'r') as f:
            diff_content = f.read()
    except FileNotFoundError:
        print(f"Error: Diff file '{args.diff_file}' not found")
        return 1
    
    # Load completed topics if provided
    completed_topics = []
    if args.completed:
        try:
            with open(args.completed, 'r') as f:
                completed_topics = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"Warning: Completed topics file '{args.completed}' not found")
    
    # Load to-learn topics if provided
    to_learn_topics = []
    if args.to_learn:
        try:
            with open(args.to_learn, 'r') as f:
                to_learn_topics = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"Warning: To-learn topics file '{args.to_learn}' not found")
    
    # Initialize the analyzer
    analyzer = GeminiTopicAnalyzer(api_key=api_key)
    
    # Analyze the diff
    print(f"Analyzing diff ({len(diff_content)} bytes)...")
    print(f"Completed topics: {len(completed_topics)}")
    print(f"To-learn topics: {len(to_learn_topics)}")
    
    result = analyzer.analyze_diff(
        diff_content,
        completed_topics=completed_topics,
        to_learn_topics=to_learn_topics
    )
    
    # Print the results
    print("\n=== Analysis Results ===")
    print(f"Found {len(result['topics'])} new topics:")
    
    for i, topic in enumerate(result['topics'], 1):
        print(f"\n{i}. {topic['title']}")
        print(f"   Description: {topic['description']}")
        if topic['prerequisites']:
            print(f"   Prerequisites: {', '.join(topic['prerequisites'])}")
        if topic['code_references']:
            print(f"   Code References: {topic['code_references']}")
    
    # Save the results to a file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\nResults saved to {args.output}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main()) 