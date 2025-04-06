from rest_framework import serializers
from .models import Topic, TopicDependency

class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class TopicDependencySerializer(serializers.ModelSerializer):
    class Meta:
        model = TopicDependency
        fields = '__all__'
        read_only_fields = ('created_at',)


# Future serializers for Brain Vibe project:
# 1. ProjectSerializer - for project CRUD operations
# 2. CodeChangeSerializer - for tracking code changes 