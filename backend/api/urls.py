from django.urls import path
from .views import (
    HealthView, TranscriptionView, ExtractionView,
    EvaluationResultsView, EvaluationRunView
)

urlpatterns = [
    path('health/', HealthView.as_view(), name='health'),
    path('transcribe/', TranscriptionView.as_view(), name='transcribe'),
    path('extract/', ExtractionView.as_view(), name='extract'),
    path('evaluation/results/', EvaluationResultsView.as_view(), name='evaluation-results'),
    path('evaluation/run/', EvaluationRunView.as_view(), name='evaluation-run'),
]
