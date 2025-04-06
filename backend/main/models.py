from django.db import models

# Create your models here.

class Topic(models.Model):
    """
    Represents a learning topic in the knowledge graph
    """
    STATUS_CHOICES = (
        ('not_learned', 'Not Learned'),
        ('in_progress', 'In Progress'),
        ('learned', 'Learned'),
    )
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_learned')
    # Will be used to track which project this topic belongs to
    project_name = models.CharField(max_length=255, blank=True)
    # External identifier used to merge duplicate topics
    topic_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Topic"
        verbose_name_plural = "Topics"


class TopicDependency(models.Model):
    """
    Represents a dependency relationship between topics
    """
    source = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='dependencies')
    target = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='dependent_topics')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.source.title} -> {self.target.title}"
    
    class Meta:
        verbose_name = "Topic Dependency"
        verbose_name_plural = "Topic Dependencies"
        unique_together = ('source', 'target')


# Future models for Brain Vibe project:
# 1. Project - for managing different coding projects
# 2. CodeChange - for tracking changes in code
