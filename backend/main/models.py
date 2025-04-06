from django.db import models

# Create your models here.

class Project(models.Model):
    """
    Represents a coding project that contains topics to learn
    """
    project_id = models.CharField(max_length=100, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    # Metadata for the project (e.g., repository path, settings)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        indexes = [
            models.Index(fields=['project_id']),
        ]


class Topic(models.Model):
    """
    Represents a learning topic in the knowledge graph
    """
    STATUS_CHOICES = (
        ('not_learned', 'Not Learned'),
        ('in_progress', 'In Progress'),
        ('learned', 'Learned'),
    )
    
    topic_id = models.CharField(max_length=255, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_learned')
    # Relationship to Project
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='topics', null=True, blank=True)
    # Self-referential relationship for prerequisites
    prerequisites = models.ManyToManyField('self', symmetrical=False, related_name='dependent_on', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Topic"
        verbose_name_plural = "Topics"
        indexes = [
            models.Index(fields=['topic_id']),
            models.Index(fields=['status']),
        ]


class CodeChange(models.Model):
    """
    Tracks code changes and analysis results
    This model links code changes to projects and stores information about
    when and how the code changed, as well as what topics were extracted
    """
    CHANGE_SOURCE_CHOICES = (
        ('cursor_ai', 'Cursor AI Generation'),
        ('manual_edit', 'Manual Edit'),
        ('git_commit', 'Git Commit'),
        ('scheduled_scan', 'Scheduled Scan'),
    )
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='code_changes')
    change_source = models.CharField(max_length=20, choices=CHANGE_SOURCE_CHOICES)
    # Unique identifier for this change (could be git hash, cursor session ID, etc.)
    change_id = models.CharField(max_length=255, blank=True, null=True)
    # Summary of what changed
    summary = models.TextField(blank=True)
    # The actual diff content
    diff_content = models.TextField(blank=True)
    # Metadata and context about the change
    metadata = models.JSONField(default=dict, blank=True)
    # Tracks if this change has been analyzed
    is_analyzed = models.BooleanField(default=False)
    # Extracted topics (if any)
    extracted_topics = models.ManyToManyField(Topic, related_name='source_changes', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Change {self.id} for {self.project.name}"
    
    class Meta:
        verbose_name = "Code Change"
        verbose_name_plural = "Code Changes"
        ordering = ['-created_at']


# Note: The TopicDependency model is superseded by the ManyToMany relationship in Topic
# Keeping for backward compatibility temporarily
class TopicDependency(models.Model):
    """
    Represents a dependency relationship between topics
    This model is deprecated in favor of the ManyToMany field in Topic
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
# 1. CodeChange - for tracking changes in code
