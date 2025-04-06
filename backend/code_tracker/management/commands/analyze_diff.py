"""
Management command to analyze a Git diff and extract topics.
"""
import os
import json
from django.core.management.base import BaseCommand, CommandError
from code_tracker.utils.git_utils import get_git_diff, parse_diff_summary
from code_tracker.utils.llm_utils import analyze_diff, format_llm_prompt
from main.models import Project, Topic, CodeChange

class Command(BaseCommand):
    help = 'Analyze a Git diff and extract topics'

    def add_arguments(self, parser):
        parser.add_argument('repo_path', type=str, help='Path to the Git repository')
        parser.add_argument('--project-id', type=str, help='Project ID to associate topics with')
        parser.add_argument('--commit', type=str, help='Commit hash to analyze')
        parser.add_argument('--prev-commit', type=str, help='Previous commit hash to compare with')
        parser.add_argument('--output', type=str, help='Output file path for the analysis results')
        parser.add_argument('--save-db', action='store_true', help='Save analysis results to the database')
        parser.add_argument('--verbose', action='store_true', help='Display verbose output')

    def handle(self, *args, **options):
        repo_path = options['repo_path']
        project_id = options.get('project_id')
        commit_hash = options.get('commit')
        prev_commit = options.get('prev_commit')
        output_file = options.get('output')
        save_db = options.get('save_db', False)
        verbose = options.get('verbose', False)
        
        # Check if the repository path exists
        if not os.path.exists(repo_path):
            raise CommandError(f"Repository path '{repo_path}' does not exist")
        
        # Get the project if a project ID is specified
        project = None
        if project_id:
            try:
                project = Project.objects.get(project_id=project_id)
                if verbose:
                    self.stdout.write(f"Found project: {project.name}")
            except Project.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Project with ID '{project_id}' does not exist"))
                if save_db:
                    self.stdout.write(self.style.WARNING("Cannot save to database without a valid project"))
                    save_db = False
        
        # Get the diff
        self.stdout.write("Getting git diff...")
        diff_content = get_git_diff(repo_path, commit_hash, prev_commit)
        
        if not diff_content:
            self.stdout.write(self.style.WARNING("No diff content found"))
            return
        
        # Parse the diff summary
        diff_summary = parse_diff_summary(diff_content)
        self.stdout.write(f"Files changed: {diff_summary['files_changed']}")
        self.stdout.write(f"Insertions: {diff_summary['insertions']}")
        self.stdout.write(f"Deletions: {diff_summary['deletions']}")
        
        # Prepare project context
        project_context = None
        if project:
            # Get existing topics for the project
            existing_topics = list(Topic.objects.filter(project=project).values('topic_id', 'title', 'status'))
            
            project_context = {
                'project_id': project.project_id,
                'name': project.name,
                'existing_topics': existing_topics
            }
        
        # Show the prompt if verbose
        if verbose:
            prompt = format_llm_prompt(diff_content[:1000] + "..." if len(diff_content) > 1000 else diff_content, 
                                      project_context)
            self.stdout.write("LLM Prompt (truncated):")
            self.stdout.write(prompt[:500] + "..." if len(prompt) > 500 else prompt)
        
        # Analyze the diff
        self.stdout.write("Analyzing diff with LLM...")
        topics = analyze_diff(diff_content, project_context)
        
        if not topics:
            self.stdout.write(self.style.WARNING("No topics found in the diff"))
            return
        
        self.stdout.write(f"Found {len(topics)} topics:")
        for topic in topics:
            self.stdout.write(f"- {topic.get('title')} ({topic.get('topic_id')})")
            if verbose:
                self.stdout.write(f"  Description: {topic.get('description')}")
                prereqs = topic.get('prerequisites', [])
                if prereqs:
                    self.stdout.write(f"  Prerequisites: {', '.join(prereqs)}")
        
        # Save the analysis results to a file if specified
        if output_file:
            with open(output_file, 'w') as f:
                json.dump({
                    'diff_summary': diff_summary,
                    'topics': topics
                }, f, indent=2)
            self.stdout.write(f"Analysis results saved to {output_file}")
        
        # Save to database if specified
        if save_db and project:
            self.stdout.write("Saving to database...")
            
            # Create a CodeChange record
            code_change = CodeChange.objects.create(
                project=project,
                change_source='git_commit',
                change_id=commit_hash,
                diff_content=diff_content,
                metadata={
                    'summary': diff_summary,
                    'previous_commit': prev_commit
                },
                is_analyzed=True
            )
            
            # Create or update topics
            for topic_data in topics:
                topic_id = topic_data.get('topic_id')
                if not topic_id:
                    continue
                
                topic, created = Topic.objects.get_or_create(
                    topic_id=topic_id,
                    project=project,
                    defaults={
                        'title': topic_data.get('title', topic_id),
                        'description': topic_data.get('description', '')
                    }
                )
                
                # Add the topic to the code change
                code_change.extracted_topics.add(topic)
                
                # Handle prerequisites
                prereqs = topic_data.get('prerequisites', [])
                for prereq_id in prereqs:
                    prereq, _ = Topic.objects.get_or_create(
                        topic_id=prereq_id,
                        project=project,
                        defaults={
                            'title': prereq_id.replace('-', ' ').title(),
                            'description': ''
                        }
                    )
                    topic.prerequisites.add(prereq)
            
            self.stdout.write(self.style.SUCCESS(f"Saved code change and {len(topics)} topics to database"))
        
        self.stdout.write(self.style.SUCCESS("Analysis complete")) 