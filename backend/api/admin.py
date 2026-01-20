from django.contrib import admin
from .models import Customer, Interaction, TestResult


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'city', 'locality', 'created_at']
    list_filter = ['city', 'locality', 'created_at']
    search_fields = ['full_name', 'phone', 'city']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ['customer', 'summary_preview', 'created_at']
    list_filter = ['created_at', 'customer']
    search_fields = ['customer__full_name', 'transcription', 'summary']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    def summary_preview(self, obj):
        return obj.summary[:50] + "..." if obj.summary and len(obj.summary) > 50 else obj.summary
    summary_preview.short_description = 'Summary'


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ['test_id', 'passed', 'confidence', 'timestamp']
    list_filter = ['passed', 'timestamp']
    search_fields = ['input_text']
    ordering = ['-timestamp']
    readonly_fields = ['timestamp']
    
    def has_add_permission(self, request):
        return False  # Tests are run programmatically
