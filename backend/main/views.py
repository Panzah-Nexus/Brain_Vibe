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
    permission_classes = [AllowAny]  # For development, change to IsAuthenticated in production
    filterset_fields = ['name']
    search_fields = ['name', 'description']
    
    @action(detail=True, methods=['get'])
    def topics(self, request, pk=None):
        """
        Returns all topics associated with a project
        """
        project = self.get_object()
        topics = Topic.objects.filter(project=project)
        serializer = TopicSerializer(topics, many=True)
        return Response(serializer.data)
    
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
    def mark_as_learned(self, request, pk=None):
        """
        Mark a topic as learned
        
        Future implementation will include:
        - Updating the status of the topic
        - Recording when the topic was learned
        - Potentially suggesting next topics to learn
        """
        topic = self.get_object()
        topic.status = 'learned'
        topic.save()
        return Response({'status': 'Topic marked as learned'})
    
    @action(detail=True, methods=['get'])
    def prerequisites(self, request, pk=None):
        """
        Returns all prerequisites for a topic
        """
        topic = self.get_object()
        serializer = TopicSerializer(topic.prerequisites.all(), many=True)
        return Response(serializer.data)


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
        """
        Analyze code changes provided in the request
        
        Request body:
        - code_diff: The Git diff to analyze
        - context: Optional context information
        """
        code_diff = request.data.get('code_diff')
        context = request.data.get('context', {})
        
        if not code_diff:
            return Response(
                {"error": "code_diff parameter is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Import here to avoid circular imports
        from .utils import llm_utils
        
        # Analyze the diff
        topics = llm_utils.analyze_diff(code_diff, context)
        
        return Response({
            "message": "Code analysis completed",
            "topics_extracted": len(topics),
            "topics": topics
        })


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
