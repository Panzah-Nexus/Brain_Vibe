from django.contrib import admin
from .models import Topic, TopicDependency

class TopicAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'project_name', 'created_at', 'updated_at']
    list_filter = ['status', 'project_name']
    search_fields = ['title', 'description', 'topic_id']
    readonly_fields = ['created_at', 'updated_at']

class TopicDependencyAdmin(admin.ModelAdmin):
    list_display = ['source', 'target', 'created_at']
    list_filter = ['source__project_name']
    search_fields = ['source__title', 'target__title']
    readonly_fields = ['created_at']

admin.site.register(Topic, TopicAdmin)
admin.site.register(TopicDependency, TopicDependencyAdmin)
