from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'projects', views.ProjectViewSet)
router.register(r'topics', views.TopicViewSet)
router.register(r'dependencies', views.TopicDependencyViewSet)
router.register(r'changes', views.CodeChangeViewSet)

urlpatterns = [
    path('hello/', views.HelloWorldView.as_view(), name='hello_world'),
    path('analysis/code/', views.CodeAnalysisView.as_view(), name='code_analysis'),
    path('projects/<str:project_id>/analyze-diff/', views.AnalyzeDiffView.as_view(), name='analyze_diff'),
    path('master-graph/', views.MasterGraphView.as_view(), name='master_graph'),
    path('topics/<str:topic_id>/complete/', views.MarkTopicAsLearnedView.as_view(), name='mark_topic_as_learned'),
    path('', include(router.urls)),
] 