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
    path('', include(router.urls)),
] 