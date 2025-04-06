from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.http import JsonResponse
from .models import Topic, TopicDependency, Project, CodeChange
from .serializers import (
    TopicSerializer, TopicDependencySerializer, ProjectSerializer, 
    TopicDetailSerializer, CodeChangeSerializer, CodeChangeCreateSerializer
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from . import services
from code_tracker import cursor_integration
from code_tracker.utils import git_utils
from .utils import llm_utils
from .utils.llm_utils import analyze_diff, extract_topics_from_diff
import logging
import uuid
from django.utils import timezone

logger = logging.getLogger(__name__)

# Create your views here.
class HelloWorldView(APIView):
    """
    A simple API view that returns a hello world message
    """
    permission_classes = []  # Allow any user to access this endpoint
    
    def get(self, request, format=None):
        return Response(
            {"message": "Hello, World!"}, 
            status=status.HTTP_200_OK
        )


class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Projects
    
    list:
    Return a list of all projects
    
    create:
    Create a new project
    
    retrieve:
    Return a specific project
    
    update:
    Update a project
    
    partial_update:
    Update part of a project
    
    destroy:
    Delete a project
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [AllowAny]  # Temporarily allow any user for testing
    filterset_fields = ['name']
    search_fields = ['name', 'description']
    lookup_field = 'project_id'  # Use project_id instead of id for lookups
    
    @action(detail=True, methods=['get'])
    def topics(self, request, project_id=None):
        """
        Returns all topics associated with a project
        """
        try:
            logger.info(f"Fetching topics for project_id: {project_id}")
            project = self.get_object()
            logger.info(f"Found project: {project.name} (ID: {project.project_id})")
            topics = Topic.objects.filter(project=project)
            logger.info(f"Found {topics.count()} topics for project")
            serializer = TopicSerializer(topics, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error fetching topics for project {project_id}: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Returns statistics about all projects
        
        Future implementation will include:
        - Number of topics per project
        - Number of topics by status
        - Most common topic dependencies
        """
        project_count = Project.objects.count()
        return Response({
            'total_projects': project_count,
            'message': 'More detailed stats will be implemented in future versions'
        })
    
    @action(detail=True, methods=['post'])
    def analyze_changes(self, request, pk=None):
        """
        Analyze changes in a project's repository and extract learning topics
        
        Required parameters:
        - repo_path: Path to the project's Git repository
        """
        project = self.get_object()
        repo_path = request.data.get('repo_path')
        
        if not repo_path:
            return Response(
                {"error": "repo_path parameter is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Call the service function
        result = services.analyze_project_changes(project.project_id, repo_path)
        
        # Handle errors
        if "error" in result:
            return Response(
                {"error": result["error"]}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(result)
    
    @action(detail=True, methods=['post'])
    def submit_cursor_change(self, request, pk=None):
        """
        Submit a code change from Cursor IDE
        
        Required parameters:
        - file_path: Path to the changed file
        - original_content: Original content of the file
        - new_content: New content of the file
        
        Optional parameters:
        - cursor_session_id: ID of the Cursor session
        - metadata: Additional metadata about the change
        """
        project = self.get_object()
        file_path = request.data.get('file_path')
        original_content = request.data.get('original_content', '')
        new_content = request.data.get('new_content')
        cursor_session_id = request.data.get('cursor_session_id')
        metadata = request.data.get('metadata')
        
        # Validate required parameters
        if not file_path or new_content is None:
            return Response(
                {"error": "file_path and new_content parameters are required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Process the change using the cursor integration module
        result = cursor_integration.process_cursor_change(
            project.project_id,
            file_path,
            original_content,
            new_content,
            cursor_session_id,
            metadata
        )
        
        # Check if there was an error
        if result.get('status') == 'error':
            return Response(
                {"error": result.get('message', 'Unknown error')}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(result)

    def create(self, request, *args, **kwargs):
        logger.info(f"Received project creation request with data: {request.data}")
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            logger.info(f"Project created successfully: {serializer.data}")
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class TopicViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Topics
    
    list:
    Return a list of all topics
    
    create:
    Create a new topic
    
    retrieve:
    Return a specific topic
    
    update:
    Update a topic
    
    partial_update:
    Update part of a topic
    
    destroy:
    Delete a topic
    """
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = [AllowAny]  # For development, change to IsAuthenticated in production
    filterset_fields = ['status', 'project']
    search_fields = ['title', 'description', 'topic_id']
    lookup_field = 'topic_id'  # Use topic_id for lookups
    
    def get_queryset(self):
        queryset = Topic.objects.all()
        project_id = self.request.query_params.get('project_id')
        if project_id:
            queryset = queryset.filter(project__project_id=project_id)
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TopicDetailSerializer
        return TopicSerializer
    
    @action(detail=True, methods=['post'])
    def mark_as_learned(self, request, topic_id=None):
        """
        Mark a topic as learned
        
        Future implementation will include:
        - Updating the status of the topic
        - Recording when the topic was learned
        - Potentially suggesting next topics to learn
        """
        try:
            logger.info(f"Marking topic {topic_id} as learned")
            topic = self.get_object()
            topic.status = 'learned'
            topic.save()
            logger.info(f"Topic {topic_id} marked as learned successfully")
            return Response({'status': 'Topic marked as learned'})
        except Exception as e:
            logger.error(f"Error marking topic {topic_id} as learned: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def prerequisites(self, request, topic_id=None):
        """
        Returns all prerequisites for a topic
        """
        try:
            logger.info(f"Fetching prerequisites for topic {topic_id}")
            topic = self.get_object()
            prerequisites = topic.prerequisites.all()
            logger.info(f"Found {prerequisites.count()} prerequisites for topic {topic_id}")
            serializer = TopicSerializer(prerequisites, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error fetching prerequisites for topic {topic_id}: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, *args, **kwargs):
        try:
            logger.info(f"Retrieving topic with topic_id: {kwargs.get('topic_id')}")
            return super().retrieve(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error retrieving topic: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            logger.info(f"Listing topics. Found {queryset.count()} topics.")
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error listing topics: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TopicDependencyViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Topic Dependencies (legacy)
    """
    queryset = TopicDependency.objects.all()
    serializer_class = TopicDependencySerializer
    permission_classes = [AllowAny]  # For development, change to IsAuthenticated in production


class CodeAnalysisView(APIView):
    """
    API view for analyzing code changes without linking to a specific project
    """
    permission_classes = [AllowAny]  # For development, change to IsAuthenticated in production
    
    def post(self, request, format=None):
        code = request.data.get('code', '')
        
        if not code:
            return Response(
                {"error": "code parameter is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Placeholder for code analysis logic
        # In the future, this will analyze the code and extract topics
        # For now, return a dummy response
        
        return Response({
            "message": "Code analyzed successfully",
            "topics": [
                {
                    "topic_id": "example-topic",
                    "title": "Example Topic",
                    "description": "This is a placeholder for future implementation"
                }
            ]
        })


class AnalyzeDiffView(APIView):
    """
    API view for analyzing code diffs for a specific project.
    This endpoint accepts either:
    1. A repository path to extract diffs locally
    2. A diff content directly from the CLI tool
    """
    permission_classes = [AllowAny]
    
    def post(self, request, project_id, format=None):
        """
        Analyze a diff for a specific project and update topics in the database.
        
        Args:
            request: The HTTP request
            project_id: The ID of the project
            format: The format of the response
            
        Returns:
            Response with the analysis results
        """
        try:
            logger.info(f"Analyzing diff for project_id: {project_id}")
            # Get the project from the database
            try:
                project = Project.objects.get(project_id=project_id)
                logger.info(f"Found project: {project.name} (ID: {project.project_id})")
            except Project.DoesNotExist:
                logger.error(f"Project with ID {project_id} not found")
                return Response(
                    {"error": f"Project with ID {project_id} not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check if diff_content is provided directly (from CLI)
            diff_text = request.data.get('diff_content')
            repo_path = request.data.get('repo_path')
            change_id = request.data.get('change_id', str(uuid.uuid4())[:8])
            
            if not diff_text and not repo_path:
                logger.error("Either diff_content or repo_path parameter is required")
                return Response(
                    {"error": "Either diff_content or repo_path parameter is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # If no diff_content provided but repo_path is, get diffs from the repo
            if not diff_text and repo_path:
                logger.info(f"Getting diffs from repository: {repo_path}")
                diff_text = git_utils.get_repo_diffs(repo_path)
                
            if not diff_text:
                logger.info(f"No changes found to analyze")
                return Response(
                    {"warning": "No changes found to analyze"}, 
                    status=status.HTTP_200_OK
                )
            
            # Track the code change in the database
            code_change = CodeChange.objects.create(
                project=project,
                change_source='cli' if 'diff_content' in request.data else 'web',
                change_id=change_id,
                diff_content=diff_text,
                metadata={
                    'repo_path': repo_path,
                    'timestamp': timezone.now().isoformat()
                }
            )
            
            # Extract and save topics
            topics_data = extract_topics_from_diff(diff_text, project)
            
            # Save extracted topics and link to the code change
            topics_created = []
            for topic_data in topics_data:
                try:
                    # Check if the topic already exists
                    topic_id = topic_data['topic_id']
                    topic, created = Topic.objects.get_or_create(
                        topic_id=topic_id,
                        defaults={
                            'title': topic_data['title'],
                            'description': topic_data['description'],
                            'project': project,
                            'status': 'not_learned'
                        }
                    )
                    
                    # Link the topic to the code change
                    code_change.extracted_topics.add(topic)
                    
                    # Only add to the topics_created list if it's a new topic
                    if created:
                        topics_created.append(topic_id)
                        
                        # Create prerequisite relationships
                        for prereq_id in topic_data.get('prerequisites', []):
                            try:
                                prereq = Topic.objects.get(topic_id=prereq_id)
                                topic.prerequisites.add(prereq)
                            except Topic.DoesNotExist:
                                logger.warning(f"Prerequisite topic {prereq_id} not found")
                    
                except Exception as e:
                    logger.error(f"Error processing topic {topic_data.get('topic_id')}: {str(e)}")
            
            logger.info(f"Analysis complete. Created {len(topics_created)} new topics")
            
            return Response({
                'success': True,
                'project_id': project_id,
                'topics_created': topics_created,
                'change_id': code_change.change_id,
                'analysis_details': [
                    f"Analyzed diff with {len(diff_text.splitlines())} lines",
                    f"Created {len(topics_created)} new topics",
                    f"The topics are now visible in your project"
                ]
            })
            
        except Exception as e:
            logger.error(f"Error analyzing diff for project {project_id}: {str(e)}")
            return Response(
                {"error": f"Failed to analyze diff: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


def home_view(request):
    """
    Simple view for the root URL that provides project information and available endpoints
    """
    # Uncomment the following line to use the HTML template instead of JSON response
    return render(request, 'main/home.html')
    
    # JSON API response option (comment out if using the template above)
    # return JsonResponse({
    #     "project": "Brain Vibe",
    #     "description": "A learning topic tracking tool for AI-generated code",
    #     "version": "0.1.0",
    #     "available_endpoints": {
    #         "api/hello/": "Test endpoint that returns a hello world message",
    #         "admin/": "Django admin interface",
    #         "api-auth/": "Authentication endpoints"
    #     }
    # })


class CodeChangeViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Code Changes
    """
    queryset = CodeChange.objects.all()
    permission_classes = [AllowAny]  # For development, change to IsAuthenticated in production
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CodeChangeCreateSerializer
        return CodeChangeSerializer
    
    def get_queryset(self):
        queryset = CodeChange.objects.all()
        project_id = self.request.query_params.get('project_id')
        if project_id:
            queryset = queryset.filter(project__project_id=project_id)
        return queryset
    
    @action(detail=False, methods=['post'])
    def submit_change(self, request):
        """
        Submit a code change from any source
        
        This is a generic endpoint that can accept code changes from various sources.
        The source should be specified in the request data.
        """
        # Extract parameters
        project_id = request.data.get('project_id')
        file_path = request.data.get('file_path')
        change_source = request.data.get('change_source', 'manual_edit')
        original_content = request.data.get('original_content', '')
        new_content = request.data.get('new_content')
        
        # Validate required parameters
        if not project_id or not file_path or new_content is None:
            return Response(
                {"error": "project_id, file_path, and new_content parameters are required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Process the change
        if change_source == 'cursor_ai':
            # Use the cursor integration module
            cursor_session_id = request.data.get('cursor_session_id')
            metadata = request.data.get('metadata')
            
            result = cursor_integration.process_cursor_change(
                project_id,
                file_path,
                original_content,
                new_content,
                cursor_session_id,
                metadata
            )
        else:
            # For other sources, compute the diff and analyze it
            from code_tracker.cursor_integration import compute_diff
            diff_content = compute_diff(original_content, new_content)
            
            # Import the services module
            result = services.analyze_code_change(
                project_id,
                file_path,
                diff_content,
                change_source
            )
        
        return Response(result)


class MasterGraphView(APIView):
    """
    API view for retrieving the master graph of all topics
    
    This endpoint provides access to the "Master Brain" - a consolidated view of all topics
    across all projects, with duplicates grouped by topic_id.
    
    Future enhancements:
    - Implement more sophisticated duplicate detection (beyond exact topic_id matches)
    - Add relationship information between topics
    - Provide filtering options (by status, project, etc.)
    - Add hierarchy visualization data
    """
    permission_classes = [AllowAny]  # For development, change to IsAuthenticated in production
    
    def get(self, request, format=None):
        """
        Retrieve all topics from the system, grouped by topic_id to avoid duplication
        
        Returns:
            A JSON response with the consolidated topics
        """
        # Get all topics from the database
        all_topics = Topic.objects.all()
        
        # Group topics by topic_id (simple approach for now)
        topic_groups = {}
        for topic in all_topics:
            if topic.topic_id not in topic_groups:
                # First time seeing this topic_id
                topic_groups[topic.topic_id] = {
                    'topic_id': topic.topic_id,
                    'title': topic.title,
                    'description': topic.description,
                    'status': topic.status,
                    'projects': [topic.project.project_id] if topic.project else [],
                    'prerequisites': [prereq.topic_id for prereq in topic.prerequisites.all()],
                    'dependent_topics': [dep.topic_id for dep in topic.dependent_on.all()],
                    'created_at': topic.created_at,
                    'updated_at': topic.updated_at
                }
            else:
                # Topic with this ID already exists, merge project information
                if topic.project and topic.project.project_id not in topic_groups[topic.topic_id]['projects']:
                    topic_groups[topic.topic_id]['projects'].append(topic.project.project_id)
                
                # Use most recent status (learned > in_progress > not_learned)
                if (topic.status == 'learned' or 
                    (topic.status == 'in_progress' and topic_groups[topic.topic_id]['status'] == 'not_learned')):
                    topic_groups[topic.topic_id]['status'] = topic.status
                
                # Use the most recent updated_at
                if topic.updated_at > topic_groups[topic.topic_id]['updated_at']:
                    topic_groups[topic.topic_id]['updated_at'] = topic.updated_at
                
                # TODO: More sophisticated merging logic for future implementation
        
        # Convert the dictionary to a list
        consolidated_topics = list(topic_groups.values())
        
        return Response({
            'total_topics': len(consolidated_topics),
            'topics': consolidated_topics
        })


class MarkTopicAsLearnedView(APIView):
    """
    API view for marking a topic as learned.
    """
    permission_classes = [AllowAny]  # For development, change to IsAuthenticated in production
    
    def post(self, request, topic_id, format=None):
        """
        Mark a topic as learned.
        
        Args:
            request: The HTTP request
            topic_id: The ID of the topic to mark as learned
            format: The format of the response
            
        Returns:
            Response with success message and updated status
        """
        try:
            logger.info(f"Marking topic {topic_id} as learned via API view")
            try:
                topic = Topic.objects.get(topic_id=topic_id)
                logger.info(f"Found topic: {topic.title}")
            except Topic.DoesNotExist:
                logger.error(f"Topic with ID {topic_id} not found")
                return Response(
                    {"error": f"Topic with ID {topic_id} not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Update the topic status
            topic.status = 'learned'
            topic.save()
            logger.info(f"Topic {topic_id} marked as learned successfully")
            
            # Return success response
            return Response({
                "message": f"Topic '{topic.title}' marked as learned",
                "topic_id": topic.topic_id,
                "status": topic.status
            })
        except Exception as e:
            logger.error(f"Error marking topic {topic_id} as learned: {str(e)}")
            return Response(
                {"error": f"Failed to mark topic as learned: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
