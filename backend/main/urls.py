from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'topics', views.TopicViewSet)
router.register(r'dependencies', views.TopicDependencyViewSet)

urlpatterns = [
    path('hello/', views.HelloWorldView.as_view(), name='hello_world'),
    path('', include(router.urls)),
] 