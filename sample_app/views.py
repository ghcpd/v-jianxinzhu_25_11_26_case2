"""
Django views demonstrating web endpoints using upgraded dependencies
"""

import json
import numpy as np
import pandas as pd
import requests
from scipy import stats
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from .models import DataRecord, AnalysisResult
from .tasks import process_large_dataset, fetch_external_data


@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'message': 'All dependencies loaded successfully'
    })


@require_http_methods(["GET", "POST"])
@csrf_exempt
def data_analysis(request):
    """
    Endpoint for data analysis using pandas, numpy, and scipy
    POST: Accepts JSON array of numbers for analysis
    GET: Returns sample analysis
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            numbers = data.get('numbers', [])
            
            if not numbers:
                return JsonResponse({'error': 'No data provided'}, status=400)
            
            # Use pandas for data manipulation
            df = pd.DataFrame({'values': numbers})
            
            # Use numpy for calculations
            np_array = np.array(numbers)
            
            # Use scipy for statistical analysis
            scipy_stats = stats.describe(np_array)
            
            # Compute statistics
            analysis = {
                'count': len(numbers),
                'mean': float(df['values'].mean()),
                'median': float(df['values'].median()),
                'std': float(df['values'].std()),
                'min': float(df['values'].min()),
                'max': float(df['values'].max()),
                'sum': float(df['values'].sum()),
                'variance': float(scipy_stats.variance),
                'skewness': float(scipy_stats.skewness),
                'kurtosis': float(scipy_stats.kurtosis)
            }
            
            # Save to database
            AnalysisResult.objects.create(
                name=f"Analysis_{len(numbers)}_points",
                dataset_size=len(numbers),
                mean_value=analysis['mean'],
                median_value=analysis['median'],
                std_deviation=analysis['std'],
                min_value=analysis['min'],
                max_value=analysis['max']
            )
            
            return JsonResponse({
                'success': True,
                'analysis': analysis
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    else:  # GET request
        # Generate sample data
        sample_data = np.random.normal(100, 15, 1000).tolist()
        return JsonResponse({
            'message': 'POST numbers array to this endpoint for analysis',
            'example': {
                'numbers': sample_data[:10]
            }
        })


@require_http_methods(["GET"])
def external_api_test(request):
    """
    Test endpoint using requests library to fetch external data
    Tests upgraded urllib3 and requests packages
    """
    test_url = request.GET.get('url', 'https://httpbin.org/json')
    
    try:
        # Use requests with proper SSL verification
        response = requests.get(
            test_url,
            timeout=10,
            verify=True,  # Ensure SSL verification (fixes CVE-2024-35195)
            headers={'User-Agent': 'Dependency-Test/1.0'}
        )
        
        return JsonResponse({
            'success': True,
            'url': test_url,
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'content_length': len(response.content),
            'encoding': response.encoding
        })
        
    except requests.exceptions.Timeout:
        return JsonResponse({'error': 'Request timeout'}, status=504)
    except requests.exceptions.SSLError as e:
        return JsonResponse({'error': f'SSL error: {str(e)}'}, status=502)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': f'Request error: {str(e)}'}, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def celery_task_test(request):
    """
    Endpoint to test Celery task execution
    Tests upgraded celery package (fixes CVE-2021-23727)
    """
    try:
        data = json.loads(request.body)
        task_type = data.get('task_type', 'dataset')
        
        if task_type == 'dataset':
            size = data.get('size', 1000)
            result = process_large_dataset.delay(size)
            
            return JsonResponse({
                'success': True,
                'task_id': result.id,
                'task_type': 'dataset_processing',
                'status': result.status,
                'result': result.get() if result.ready() else None
            })
            
        elif task_type == 'external':
            url = data.get('url', 'https://httpbin.org/json')
            result = fetch_external_data.delay(url)
            
            return JsonResponse({
                'success': True,
                'task_id': result.id,
                'task_type': 'external_fetch',
                'status': result.status,
                'result': result.get() if result.ready() else None
            })
            
        else:
            return JsonResponse({'error': 'Invalid task type'}, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def pandas_operations(request):
    """
    Endpoint demonstrating pandas 2.x operations
    Tests upgraded pandas with copy-on-write and nullable dtypes
    """
    try:
        # Create sample dataframe with nullable types (pandas 2.x feature)
        df = pd.DataFrame({
            'id': pd.array([1, 2, 3, 4, 5], dtype='Int64'),  # Nullable integer
            'name': pd.array(['Alice', 'Bob', None, 'David', 'Eve'], dtype='string'),  # Nullable string
            'score': [95.5, 87.3, pd.NA, 92.1, 88.9],
            'passed': pd.array([True, True, pd.NA, True, True], dtype='boolean')  # Nullable boolean
        })
        
        # Perform operations
        summary = {
            'shape': df.shape,
            'dtypes': df.dtypes.astype(str).to_dict(),
            'mean_score': float(df['score'].mean()) if not df['score'].isna().all() else None,
            'null_counts': df.isna().sum().to_dict(),
            'memory_usage': int(df.memory_usage(deep=True).sum())
        }
        
        # Test copy-on-write behavior (pandas 2.x default)
        df2 = df.copy()
        df2.loc[0, 'score'] = 100.0
        
        summary['copy_on_write_test'] = {
            'original_first_score': float(df.loc[0, 'score']) if pd.notna(df.loc[0, 'score']) else None,
            'modified_copy_first_score': float(df2.loc[0, 'score']),
            'copy_on_write_working': float(df.loc[0, 'score']) != float(df2.loc[0, 'score'])
        }
        
        return JsonResponse({
            'success': True,
            'pandas_version': pd.__version__,
            'summary': summary,
            'data': df.to_dict(orient='records')
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def numpy_scipy_operations(request):
    """
    Endpoint demonstrating numpy and scipy operations
    Tests upgraded numpy (fixes CVE-2021-33430, CVE-2021-41495, CVE-2021-41496)
    """
    try:
        # Create sample data
        size = int(request.GET.get('size', 1000))
        data = np.random.randn(size)
        
        # NumPy operations
        numpy_results = {
            'mean': float(np.mean(data)),
            'std': float(np.std(data)),
            'median': float(np.median(data)),
            'percentile_25': float(np.percentile(data, 25)),
            'percentile_75': float(np.percentile(data, 75))
        }
        
        # SciPy statistical tests
        scipy_results = {
            'shapiro_test': {
                'statistic': float(stats.shapiro(data[:min(size, 5000)])[0]),
                'p_value': float(stats.shapiro(data[:min(size, 5000)])[1])
            },
            'describe': {
                'nobs': int(stats.describe(data).nobs),
                'minmax': [float(x) for x in stats.describe(data).minmax],
                'mean': float(stats.describe(data).mean),
                'variance': float(stats.describe(data).variance),
                'skewness': float(stats.describe(data).skewness),
                'kurtosis': float(stats.describe(data).kurtosis)
            }
        }
        
        return JsonResponse({
            'success': True,
            'numpy_version': np.__version__,
            'scipy_version': stats.__version__ if hasattr(stats, '__version__') else 'N/A',
            'data_size': size,
            'numpy_results': numpy_results,
            'scipy_results': scipy_results
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def list_analyses(request):
    """List all stored analysis results"""
    results = AnalysisResult.objects.all()[:20]
    
    return JsonResponse({
        'count': results.count(),
        'results': [
            {
                'id': r.id,
                'name': r.name,
                'dataset_size': r.dataset_size,
                'mean': r.mean_value,
                'median': r.median_value,
                'std': r.std_deviation,
                'computed_at': r.computed_at.isoformat()
            }
            for r in results
        ]
    })
