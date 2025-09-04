from django.core.management.base import BaseCommand
from main.models import Project
# Scanner functionality removed - this command needs to be updated
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Scan projects for code changes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--project',
            help='Project ID to scan (if not specified, all projects will be scanned)'
        )
        parser.add_argument(
            '--due-only',
            action='store_true',
            help='Only scan projects that are due for scanning'
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=24,
            help='Interval in hours for due projects (default: 24)'
        )
        parser.add_argument(
            '--register-all',
            action='store_true',
            help='Register all projects for scanning'
        )

    def handle(self, *args, **options):
        project_id = options.get('project')
        due_only = options.get('due_only')
        interval = options.get('interval')
        register_all = options.get('register_all')
        
        # Register all projects if requested
        if register_all:
            self.stdout.write("Registering all projects for scanning...")
            projects = Project.objects.all()
            
            for project in projects:
                # The repo_path field should be added to the Project model
                # For now, we'll use a placeholder
                repo_path = project.metadata.get('repo_path') if hasattr(project, 'metadata') else None
                
                if not repo_path:
                    self.stdout.write(self.style.WARNING(
                        f"Project {project.project_id} does not have a repo_path, skipping"
                    ))
                    continue
                
                success = scanner.register_project(project.project_id, repo_path)
                if success:
                    self.stdout.write(self.style.SUCCESS(
                        f"Registered project {project.project_id} for scanning"
                    ))
                else:
                    self.stdout.write(self.style.ERROR(
                        f"Failed to register project {project.project_id} for scanning"
                    ))
        
        # Scan specific project
        if project_id:
            self.stdout.write(f"Scanning project {project_id}...")
            result = scanner.scan_project(project_id)
            
            if result.get('status') == 'success':
                self.stdout.write(self.style.SUCCESS(result.get('message')))
            else:
                self.stdout.write(self.style.ERROR(result.get('message')))
                
            # Print changed files
            changed_files = result.get('changed_files', 0)
            if changed_files > 0:
                self.stdout.write(f"Changed files: {changed_files}")
                
                results = result.get('results', [])
                for file_result in results:
                    file_path = file_result.get('file_path')
                    analysis = file_result.get('analysis_result', {})
                    
                    topics = analysis.get('topics', [])
                    topics_count = len(topics)
                    
                    self.stdout.write(f"  {file_path}: {topics_count} topics extracted")
                    
                    for topic in topics:
                        self.stdout.write(f"    - {topic.get('title')}: {topic.get('description')}")
            
            return
        
        # Scan due projects
        if due_only:
            self.stdout.write(f"Scanning projects due for scanning (interval: {interval} hours)...")
            result = scanner.scan_due_projects(interval)
            
            if result.get('status') == 'success':
                self.stdout.write(self.style.SUCCESS(result.get('message')))
            else:
                self.stdout.write(self.style.ERROR(result.get('message')))
                
            # Print results for each project
            projects_results = result.get('results', {})
            for project_id, project_result in projects_results.items():
                status = project_result.get('status')
                message = project_result.get('message')
                
                if status == 'success':
                    self.stdout.write(f"  Project {project_id}: {message}")
                else:
                    self.stdout.write(self.style.ERROR(f"  Project {project_id}: {message}"))
            
            return
        
        # Scan all projects
        self.stdout.write("Scanning all registered projects...")
        result = scanner.scan_all_projects()
        
        if result.get('status') == 'success':
            self.stdout.write(self.style.SUCCESS(result.get('message')))
        else:
            self.stdout.write(self.style.ERROR(result.get('message')))
            
        # Print results for each project
        projects_results = result.get('results', {})
        for project_id, project_result in projects_results.items():
            status = project_result.get('status')
            message = project_result.get('message')
            
            if status == 'success':
                self.stdout.write(f"  Project {project_id}: {message}")
            else:
                self.stdout.write(self.style.ERROR(f"  Project {project_id}: {message}")) 