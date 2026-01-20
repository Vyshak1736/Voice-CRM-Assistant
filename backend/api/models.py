from django.db import models
from django.utils import timezone


class Customer(models.Model):
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    locality = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customers'
        ordering = ['-created_at']

    def __str__(self):
        return self.full_name


class Interaction(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='interactions')
    summary = models.TextField(blank=True, null=True)
    transcription = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'interactions'
        ordering = ['-created_at']

    def __str__(self):
        return f"Interaction with {self.customer.full_name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class TestResult(models.Model):
    test_id = models.IntegerField()
    input_text = models.TextField()
    expected_output = models.JSONField()
    actual_output = models.JSONField()
    passed = models.BooleanField(default=False)
    confidence = models.FloatField(default=0.0)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'test_results'
        ordering = ['-timestamp']

    def __str__(self):
        return f"Test #{self.test_id} - {'PASS' if self.passed else 'FAIL'}"
