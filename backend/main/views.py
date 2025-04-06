from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.http import JsonResponse
from .models import Topic, TopicDependency
from .serializers import TopicSerializer, TopicDependencySerializer
from rest_framework.permissions import IsAuthenticated, AllowAny

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

class TopicViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Topics
    """
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = [AllowAny]  # For development, change to IsAuthenticated in production
    filterset_fields = ['status', 'project_name']
    search_fields = ['title', 'description']
    
    def get_queryset(self):
        queryset = Topic.objects.all()
        project = self.request.query_params.get('project_name')
        if project:
            queryset = queryset.filter(project_name=project)
        return queryset


class TopicDependencyViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Topic Dependencies
    """
    queryset = TopicDependency.objects.all()
    serializer_class = TopicDependencySerializer
    permission_classes = [AllowAny]  # For development, change to IsAuthenticated in production


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
