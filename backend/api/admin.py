from django.contrib import admin
from .models import Customer, Interaction, TestResult


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'city', 'locality', 'created_at')
    list_filter = ('city', 'locality', 'created_at')
    search_fields = ('full_name', 'phone', 'city')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ('created_at', 'updated_at')
        return ()


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ('customer', 'summary_preview', 'transcription_preview', 'created_at')
    list_filter = ('created_at', 'customer')
    search_fields = ('customer__full_name', 'transcription', 'summary')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ('created_at', 'updated_at')
        return ()
    
    def summary_preview(self, obj):
        if obj.summary and len(obj.summary) > 50:
            return obj.summary[:50] + "..."
        return obj.summary or "-"
    summary_preview.short_description = 'Summary'
    
    def transcription_preview(self, obj):
        if obj.transcription and len(obj.transcription) > 50:
            return obj.transcription[:50] + "..."
        return obj.transcription or "-"
    transcription_preview.short_description = 'Transcription'


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ('test_id', 'passed', 'confidence', 'timestamp')
    list_filter = ('passed', 'timestamp')
    search_fields = ('input_text',)
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp',)
    
    def has_add_permission(self, request):
        return False  # Tests are run programmatically
    
    def get_readonly_fields(self, request, obj=None):
        return ('timestamp',)
