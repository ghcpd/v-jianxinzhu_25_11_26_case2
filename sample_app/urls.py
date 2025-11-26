"""
URL configuration for sample application
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.health_check, name='health_check'),
    path('health/', views.health_check, name='health'),
    path('analysis/', views.data_analysis, name='data_analysis'),
    path('external/', views.external_api_test, name='external_api'),
    path('celery/', views.celery_task_test, name='celery_task'),
    path('pandas/', views.pandas_operations, name='pandas_ops'),
    path('numpy-scipy/', views.numpy_scipy_operations, name='numpy_scipy'),
    path('results/', views.list_analyses, name='list_analyses'),
]
