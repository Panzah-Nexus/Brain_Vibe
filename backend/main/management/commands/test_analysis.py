from django.core.management.base import BaseCommand
import os
import json
from main.utils import git_utils, llm_utils

class Command(BaseCommand):
    help = 'Test the Git diff and LLM utils'

    def add_arguments(self, parser):
        parser.add_argument('--repo-path', type=str, help='Path to the Git repository')
        parser.add_argument('--from-commit', type=str, help='Starting commit hash')
        parser.add_argument('--to-commit', type=str, default='HEAD', help='Ending commit hash')
        parser.add_argument('--output', type=str, help='Path to save the output JSON')

    def handle(self, *args, **options):
        repo_path = options.get('repo_path')
        from_commit = options.get('from_commit')
        to_commit = options.get('to_commit', 'HEAD')
        output_path = options.get('output')
        
        # Use the current directory if no repo path is provided
        if not repo_path:
            repo_path = os.getcwd()
            self.stdout.write(f"Using current directory as repo path: {repo_path}")
        
        # Get the diff
        self.stdout.write(self.style.SUCCESS(f"Getting diff for {repo_path} from {from_commit} to {to_commit}"))
        diff = git_utils.get_repo_diffs(repo_path, from_commit, to_commit)
        
        # Print a summary of the diff
        diff_lines = diff.split('\n')
        self.stdout.write(f"Diff has {len(diff_lines)} lines")
        
        # Show a snippet of the diff
        if len(diff_lines) > 10:
            self.stdout.write("First 10 lines of the diff:")
            for line in diff_lines[:10]:
                self.stdout.write(f"  {line}")
            self.stdout.write("...")
        else:
            self.stdout.write("Full diff:")
            for line in diff_lines:
                self.stdout.write(f"  {line}")
        
        # Analyze the diff
        self.stdout.write(self.style.SUCCESS("Analyzing diff with LLM"))
        topics = llm_utils.analyze_diff(diff)
        
        # Print the results
        self.stdout.write(f"Found {len(topics)} topics:")
        for topic in topics:
            self.stdout.write(f"  Topic ID: {topic.get('topic_id')}")
            self.stdout.write(f"  Title: {topic.get('title')}")
            self.stdout.write(f"  Description: {topic.get('description')}")
            prereqs = topic.get('prerequisites', [])
            self.stdout.write(f"  Prerequisites: {', '.join(prereqs) if prereqs else 'None'}")
            self.stdout.write("")
        
        # Save the results to a file if requested
        if output_path:
            result = {
                "diff_summary": {
                    "lines": len(diff_lines),
                    "repo_path": repo_path,
                    "from_commit": from_commit,
                    "to_commit": to_commit
                },
                "topics": topics
            }
            with open(output_path, 'w') as f:
                json.dump(result, f, indent=2)
            self.stdout.write(self.style.SUCCESS(f"Results saved to {output_path}"))
        
        self.stdout.write(self.style.SUCCESS("Analysis complete!")) 