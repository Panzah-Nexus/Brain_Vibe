import argparse
import sys
from pathlib import Path
from .management.commands.init_project import init_project
from .cursor_integration import setup_cursor_workspace

def main():
    parser = argparse.ArgumentParser(description='BrainVibe Project Management')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize a new project')
    init_parser.add_argument('path', help='Path to project directory')
    init_parser.add_argument('--github', help='GitHub repository URL')
    init_parser.add_argument('--cursor', action='store_true', help='Set up Cursor integration')
    
    args = parser.parse_args()
    
    if args.command == 'init':
        project_path = Path(args.path).absolute()
        
        # Initialize project
        if not init_project(str(project_path), args.github):
            print("Failed to initialize project")
            sys.exit(1)
        
        # Set up Cursor integration if requested
        if args.cursor:
            if not setup_cursor_workspace(str(project_path)):
                print("Failed to set up Cursor integration")
                sys.exit(1)
        
        print(f"Successfully initialized project at {project_path}")
        if args.github:
            print(f"Linked to GitHub repository: {args.github}")
        if args.cursor:
            print("Cursor integration enabled")
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main() 