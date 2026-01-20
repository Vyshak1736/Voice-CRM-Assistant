from rest_framework import serializers
from .models import Customer, Interaction, TestResult


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'full_name', 'phone', 'address', 'city', 'locality', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class InteractionSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    customer_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Interaction
        fields = ['id', 'customer', 'customer_id', 'summary', 'transcription', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class TestResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestResult
        fields = ['id', 'test_id', 'input_text', 'expected_output', 'actual_output', 'passed', 'confidence', 'timestamp']
        read_only_fields = ['id', 'timestamp']
