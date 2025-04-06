from django.core.management.base import BaseCommand
from main.models import Project, Topic
import random

class Command(BaseCommand):
    help = 'Creates test data for the Brain Vibe project'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Creating test data for Brain Vibe"))
        
        # Delete existing data
        self.stdout.write("Deleting existing data...")
        Project.objects.all().delete()
        Topic.objects.all().delete()
        
        # Create projects
        self.stdout.write("Creating projects...")
        projects = [
            Project(
                project_id="web-app-1",
                name="Web Application",
                description="A full-stack web application built with React and Django"
            ),
            Project(
                project_id="mobile-app-1",
                name="Mobile Application",
                description="A mobile app built with React Native"
            ),
            Project(
                project_id="ml-project-1",
                name="Machine Learning Project",
                description="A machine learning project for image classification"
            )
        ]
        
        for project in projects:
            project.save()
            self.stdout.write(f"  - Created project: {project.name}")
        
        # Create topics for web app project
        web_topics = [
            {
                "topic_id": "react-basics",
                "title": "React Basics",
                "description": "Fundamentals of React including components, props, and state",
                "status": "not_learned"
            },
            {
                "topic_id": "react-hooks",
                "title": "React Hooks",
                "description": "Using hooks in functional components",
                "status": "not_learned"
            },
            {
                "topic_id": "django-rest-framework",
                "title": "Django REST Framework",
                "description": "Building APIs with Django REST Framework",
                "status": "in_progress"
            },
            {
                "topic_id": "authentication-jwt",
                "title": "JWT Authentication",
                "description": "Implementing JWT authentication",
                "status": "not_learned"
            }
        ]
        
        # Create topics for mobile app project
        mobile_topics = [
            {
                "topic_id": "react-native-basics",
                "title": "React Native Basics",
                "description": "Fundamentals of React Native",
                "status": "not_learned"
            },
            {
                "topic_id": "mobile-navigation",
                "title": "Mobile Navigation",
                "description": "Navigation in mobile apps",
                "status": "not_learned"
            },
            {
                "topic_id": "mobile-styling",
                "title": "Mobile Styling",
                "description": "Styling in React Native",
                "status": "not_learned"
            }
        ]
        
        # Create topics for ML project
        ml_topics = [
            {
                "topic_id": "python-numpy",
                "title": "NumPy",
                "description": "Numerical computing with NumPy",
                "status": "learned"
            },
            {
                "topic_id": "python-pandas",
                "title": "Pandas",
                "description": "Data manipulation with Pandas",
                "status": "in_progress"
            },
            {
                "topic_id": "tensorflow-basics",
                "title": "TensorFlow Basics",
                "description": "Basics of TensorFlow",
                "status": "not_learned"
            },
            {
                "topic_id": "cnn",
                "title": "Convolutional Neural Networks",
                "description": "Convolutional Neural Networks for image processing",
                "status": "not_learned"
            }
        ]
        
        # Save topics and assign to projects
        self.stdout.write("Creating topics for Web Application project...")
        web_project = Project.objects.get(project_id="web-app-1")
        for topic_data in web_topics:
            topic = Topic.objects.create(
                project=web_project,
                **topic_data
            )
            self.stdout.write(f"  - Created topic: {topic.title}")
        
        self.stdout.write("Creating topics for Mobile Application project...")
        mobile_project = Project.objects.get(project_id="mobile-app-1")
        for topic_data in mobile_topics:
            topic = Topic.objects.create(
                project=mobile_project,
                **topic_data
            )
            self.stdout.write(f"  - Created topic: {topic.title}")
        
        self.stdout.write("Creating topics for Machine Learning project...")
        ml_project = Project.objects.get(project_id="ml-project-1")
        for topic_data in ml_topics:
            topic = Topic.objects.create(
                project=ml_project,
                **topic_data
            )
            self.stdout.write(f"  - Created topic: {topic.title}")
        
        # Add prerequisites
        self.stdout.write("Setting up topic prerequisites...")
        # React hooks depends on React basics
        Topic.objects.get(topic_id="react-hooks").prerequisites.add(
            Topic.objects.get(topic_id="react-basics")
        )
        
        # JWT Authentication depends on Django REST Framework
        Topic.objects.get(topic_id="authentication-jwt").prerequisites.add(
            Topic.objects.get(topic_id="django-rest-framework")
        )
        
        # Mobile Navigation depends on React Native Basics
        Topic.objects.get(topic_id="mobile-navigation").prerequisites.add(
            Topic.objects.get(topic_id="react-native-basics")
        )
        
        # Mobile Styling depends on React Native Basics
        Topic.objects.get(topic_id="mobile-styling").prerequisites.add(
            Topic.objects.get(topic_id="react-native-basics")
        )
        
        # TensorFlow depends on NumPy
        Topic.objects.get(topic_id="tensorflow-basics").prerequisites.add(
            Topic.objects.get(topic_id="python-numpy")
        )
        
        # CNN depends on TensorFlow
        Topic.objects.get(topic_id="cnn").prerequisites.add(
            Topic.objects.get(topic_id="tensorflow-basics")
        )
        
        self.stdout.write(self.style.SUCCESS("Successfully created test data!"))