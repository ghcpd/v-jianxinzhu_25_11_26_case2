"""
Django models for testing upgraded dependencies
"""

from django.db import models
from django.contrib.auth.models import User


class DataRecord(models.Model):
    """Sample model for testing database operations"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    value = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['value']),
        ]
    
    def __str__(self):
        return self.title


class AnalysisResult(models.Model):
    """Model for storing data analysis results"""
    name = models.CharField(max_length=100)
    dataset_size = models.IntegerField()
    mean_value = models.FloatField()
    median_value = models.FloatField()
    std_deviation = models.FloatField()
    min_value = models.FloatField()
    max_value = models.FloatField()
    computed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-computed_at']
    
    def __str__(self):
        return f"{self.name} - {self.computed_at}"
