from django.core.management.base import BaseCommand
import sys
import os
from django.conf import settings
from django.apps import apps

class Command(BaseCommand):
    help = 'Checks that the Brain Vibe system is properly set up'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Brain Vibe Setup Check"))
        self.stdout.write("-" * 40)
        
        # Check Python version
        python_version = sys.version.split()[0]
        self.stdout.write(f"Python version: {python_version}")
        
        # Check Django version
        import django
        self.stdout.write(f"Django version: {django.get_version()}")
        
        # Check DRF
        try:
            import rest_framework
            self.stdout.write(f"Django REST Framework version: {rest_framework.VERSION}")
            drf_status = "✓"
        except ImportError:
            self.stdout.write(self.style.ERROR("Django REST Framework is not installed"))
            drf_status = "✗"
        
        # Check database connection
        try:
            from django.db import connection
            connection.cursor()
            db_status = "✓"
            self.stdout.write(f"Database connection: OK ({settings.DATABASES['default']['ENGINE']})")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Database connection error: {str(e)}"))
            db_status = "✗"
        
        # Check URL setup
        from django.urls import get_resolver
        resolver = get_resolver()
        patterns = resolver.url_patterns
        
        url_patterns = []
        for pattern in patterns:
            url_patterns.append(f"- {str(pattern.pattern)}")
        
        self.stdout.write("\nRegistered URL patterns:")
        for pattern in url_patterns:
            self.stdout.write(f"  {pattern}")
        
        # Check installed apps
        self.stdout.write("\nInstalled apps:")
        for app in sorted(settings.INSTALLED_APPS):
            self.stdout.write(f"  - {app}")
        
        # Summary
        self.stdout.write("\nSummary:")
        self.stdout.write(f"Django REST Framework: {drf_status}")
        self.stdout.write(f"Database connection: {db_status}")
        
        self.stdout.write("\nSetup is complete! You can run the server with:")
        self.stdout.write("python3 manage.py runserver") 