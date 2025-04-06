from rest_framework import serializers
from .models import Topic, TopicDependency, Project, CodeChange

class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for the Project model
    """
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class TopicSerializer(serializers.ModelSerializer):
    """
    Serializer for the Topic model
    """
    class Meta:
        model = Topic
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class TopicDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for the Topic model that includes nested prerequisite topics
    """
    prerequisites = TopicSerializer(many=True, read_only=True)
    dependent_on = serializers.SerializerMethodField()
    project_name = serializers.SerializerMethodField()

    class Meta:
        model = Topic
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def get_dependent_on(self, obj):
        """Returns topics that depend on this topic"""
        return TopicSerializer(obj.dependent_on.all(), many=True).data
    
    def get_project_name(self, obj):
        """Returns the project name if available"""
        if obj.project:
            return obj.project.name
        return None


class TopicDependencySerializer(serializers.ModelSerializer):
    """
    Serializer for the TopicDependency model (legacy)
    """
    class Meta:
        model = TopicDependency
        fields = '__all__'
        read_only_fields = ('created_at',)


class CodeChangeSerializer(serializers.ModelSerializer):
    """
    Serializer for the CodeChange model
    """
    extracted_topics = TopicSerializer(many=True, read_only=True)
    project_name = serializers.SerializerMethodField()
    
    class Meta:
        model = CodeChange
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def get_project_name(self, obj):
        return obj.project.name if obj.project else None


class CodeChangeCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a CodeChange
    """
    class Meta:
        model = CodeChange
        fields = ('project', 'change_source', 'change_id', 'summary', 'diff_content', 'metadata')


# Future serializers for Brain Vibe project:
# 1. CodeChangeSerializer - for tracking code changes 