"""
Celery tasks for testing upgraded celery package
Tests fix for CVE-2021-23727 (command injection vulnerability)
"""

import numpy as np
import pandas as pd
import requests
from celery import shared_task
from .models import AnalysisResult


@shared_task
def process_large_dataset(size=10000):
    """
    Process a large dataset using numpy and pandas
    Tests celery task execution with data processing
    """
    # Generate random data
    data = np.random.randn(size)
    df = pd.DataFrame({'values': data})
    
    # Perform analysis
    analysis = {
        'size': size,
        'mean': float(df['values'].mean()),
        'median': float(df['values'].median()),
        'std': float(df['values'].std()),
        'min': float(df['values'].min()),
        'max': float(df['values'].max())
    }
    
    # Save to database
    AnalysisResult.objects.create(
        name=f"Celery_Task_{size}_points",
        dataset_size=size,
        mean_value=analysis['mean'],
        median_value=analysis['median'],
        std_deviation=analysis['std'],
        min_value=analysis['min'],
        max_value=analysis['max']
    )
    
    return analysis


@shared_task
def fetch_external_data(url):
    """
    Fetch data from external API using requests
    Tests celery with requests library (CVE fixes)
    """
    try:
        response = requests.get(url, timeout=10, verify=True)
        return {
            'success': True,
            'status_code': response.status_code,
            'content_length': len(response.content),
            'url': url
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'url': url
        }


@shared_task
def scheduled_cleanup():
    """
    Cleanup old analysis results
    Example of scheduled task
    """
    from django.utils import timezone
    from datetime import timedelta
    
    threshold = timezone.now() - timedelta(days=30)
    deleted_count = AnalysisResult.objects.filter(computed_at__lt=threshold).delete()[0]
    
    return {
        'deleted_count': deleted_count,
        'threshold': threshold.isoformat()
    }
