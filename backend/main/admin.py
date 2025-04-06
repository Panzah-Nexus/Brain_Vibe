from django.contrib import admin
from .models import Topic, TopicDependency, Project

class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'project_id', 'created_at', 'updated_at']
    list_filter = ['created_at']
    search_fields = ['name', 'project_id', 'description']
    readonly_fields = ['created_at', 'updated_at']

class TopicAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'get_project_name', 'created_at', 'updated_at']
    list_filter = ['status', 'project']
    search_fields = ['title', 'description', 'topic_id']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_project_name(self, obj):
        return obj.project.name if obj.project else '-'
    get_project_name.short_description = 'Project'

class TopicDependencyAdmin(admin.ModelAdmin):
    list_display = ['source', 'target', 'created_at']
    list_filter = ['source__project']
    search_fields = ['source__title', 'target__title']
    readonly_fields = ['created_at']

admin.site.register(Project, ProjectAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(TopicDependency, TopicDependencyAdmin)
