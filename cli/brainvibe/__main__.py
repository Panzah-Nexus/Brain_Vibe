#!/usr/bin/env python3
"""
BrainVibe CLI entry point
"""

import sys
import argparse
from .commands import init_command, track_command

def main():
    """Main entry point for the BrainVibe CLI"""
    parser = argparse.ArgumentParser(
        description='BrainVibe - Track code changes and extract learning topics'
    )
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize BrainVibe in a project')
    init_parser.add_argument('--project-id', required=True, help='Project ID from the web interface')
    init_parser.add_argument('--api-url', default='http://localhost:8000/api', help='URL of the BrainVibe API')
    
    # Track command
    track_parser = subparsers.add_parser('track', help='Track code changes in real-time')
    track_parser.add_argument('--watch', action='store_true', help='Watch for file changes continuously')
    track_parser.add_argument('--one-shot', action='store_true', help='Run analysis once and exit')
    track_parser.add_argument('--interval', type=int, default=120000, 
                             help='Interval in milliseconds between commits (default: 120000 = 2 minutes)')
    track_parser.add_argument('--ignore-file', type=str, 
                             help='Custom ignore file path (default: .brainvibeignore)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run the appropriate command
    if args.command == 'init':
        init_command(args)
    elif args.command == 'track':
        track_command(args)
    else:
        parser.print_help()
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main()) 