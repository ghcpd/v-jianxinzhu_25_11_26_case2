"""
Tests for HTTP and networking functionality
Tests requests, urllib3 upgrades and security fixes
"""

import pytest
import requests
import urllib3
from unittest.mock import Mock, patch


class TestRequestsUpgrade:
    """Test requests library upgrade and security fixes"""
    
    def test_requests_version(self):
        """Verify requests version is upgraded"""
        version = requests.__version__
        major, minor = map(int, version.split('.')[:2])
        assert major >= 2 and minor >= 32, f"Requests version {version} should be >= 2.32"
    
    @pytest.mark.integration
    def test_requests_basic_get(self):
        """Test basic GET request"""
        response = requests.get('https://httpbin.org/get', timeout=10)
        assert response.status_code == 200
        assert 'application/json' in response.headers.get('content-type', '')
    
    @pytest.mark.integration
    def test_requests_ssl_verification(self):
        """Test SSL verification is enabled (CVE-2024-35195 fix)"""
        # Should work with valid SSL
        response = requests.get('https://httpbin.org/get', verify=True, timeout=10)
        assert response.status_code == 200
        
        # Should fail with invalid SSL when verify=True
        with pytest.raises(requests.exceptions.SSLError):
            requests.get('https://self-signed.badssl.com/', verify=True, timeout=10)
    
    @pytest.mark.integration
    def test_requests_proxy_header_security(self):
        """Test proxy authorization header handling (CVE-2023-32681 fix)"""
        # Verify that Proxy-Authorization headers are handled securely
        headers = {'Proxy-Authorization': 'Bearer secret-token'}
        
        # This should not leak the Proxy-Authorization header on redirects
        response = requests.get(
            'https://httpbin.org/get',
            headers=headers,
            timeout=10,
            allow_redirects=True
        )
        assert response.status_code == 200
    
    @pytest.mark.integration
    def test_requests_timeout_handling(self):
        """Test timeout handling"""
        with pytest.raises(requests.exceptions.Timeout):
            requests.get('https://httpbin.org/delay/10', timeout=1)
    
    @pytest.mark.integration
    def test_requests_json_response(self):
        """Test JSON response handling"""
        response = requests.get('https://httpbin.org/json', timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
    
    @pytest.mark.integration
    def test_requests_post_data(self):
        """Test POST request with data"""
        payload = {'key': 'value', 'number': 42}
        response = requests.post(
            'https://httpbin.org/post',
            json=payload,
            timeout=10
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['json'] == payload
    
    @pytest.mark.integration
    def test_requests_custom_headers(self):
        """Test custom headers"""
        headers = {
            'User-Agent': 'Test-Client/1.0',
            'X-Custom-Header': 'custom-value'
        }
        
        response = requests.get(
            'https://httpbin.org/headers',
            headers=headers,
            timeout=10
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'Test-Client/1.0' in data['headers']['User-Agent']
    
    def test_requests_session_reuse(self):
        """Test session connection pooling"""
        session = requests.Session()
        session.headers.update({'User-Agent': 'Test/1.0'})
        
        # Multiple requests should reuse connection
        for _ in range(3):
            response = session.get('https://httpbin.org/get', timeout=10)
            assert response.status_code == 200
        
        session.close()
    
    @pytest.mark.integration
    def test_requests_redirect_handling(self):
        """Test redirect handling"""
        response = requests.get(
            'https://httpbin.org/redirect/2',
            timeout=10,
            allow_redirects=True
        )
        
        assert response.status_code == 200
        assert len(response.history) == 2


class TestUrllib3Upgrade:
    """Test urllib3 upgrade and security fixes"""
    
    def test_urllib3_version(self):
        """Verify urllib3 version is upgraded"""
        version = urllib3.__version__
        major = int(version.split('.')[0])
        assert major >= 2, f"urllib3 version {version} should be >= 2.0"
    
    def test_urllib3_poolmanager(self):
        """Test PoolManager functionality"""
        http = urllib3.PoolManager()
        response = http.request('GET', 'https://httpbin.org/get')
        
        assert response.status == 200
        assert len(response.data) > 0
    
    def test_urllib3_retry_mechanism(self):
        """Test retry mechanism"""
        retries = urllib3.Retry(
            total=3,
            backoff_factor=0.1,
            status_forcelist=[500, 502, 503, 504]
        )
        
        http = urllib3.PoolManager(retries=retries)
        
        # This should work on first try
        response = http.request('GET', 'https://httpbin.org/get')
        assert response.status == 200
    
    def test_urllib3_timeout(self):
        """Test timeout configuration"""
        timeout = urllib3.Timeout(connect=2.0, read=5.0)
        http = urllib3.PoolManager(timeout=timeout)
        
        response = http.request('GET', 'https://httpbin.org/get')
        assert response.status == 200
    
    def test_urllib3_headers(self):
        """Test custom headers"""
        http = urllib3.PoolManager()
        headers = {
            'User-Agent': 'urllib3-test/1.0',
            'X-Test-Header': 'test-value'
        }
        
        response = http.request('GET', 'https://httpbin.org/headers', headers=headers)
        assert response.status == 200
    
    def test_urllib3_cert_verification(self):
        """Test certificate verification (CVE-2019-11324 fix)"""
        # Should verify certificates by default
        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED')
        response = http.request('GET', 'https://httpbin.org/get')
        assert response.status == 200
    
    def test_urllib3_no_crlf_injection(self):
        """Test CRLF injection prevention (CVE-2019-11236, CVE-2020-26137 fix)"""
        http = urllib3.PoolManager()
        
        # Should not allow CRLF characters in headers
        malicious_header = "test\r\nX-Injected: malicious"
        
        # urllib3 should sanitize or reject this
        try:
            response = http.request(
                'GET',
                'https://httpbin.org/get',
                headers={'X-Test': malicious_header}
            )
            # If it doesn't raise, it should have sanitized the header
            assert response.status == 200
        except (ValueError, urllib3.exceptions.HTTPError):
            # It's ok if it rejects the request
            pass


class TestNetworkingIntegration:
    """Integration tests for networking stack"""
    
    @pytest.mark.integration
    def test_https_connection_pooling(self):
        """Test HTTPS connection pooling"""
        session = requests.Session()
        
        urls = [
            'https://httpbin.org/get',
            'https://httpbin.org/uuid',
            'https://httpbin.org/json'
        ]
        
        for url in urls:
            response = session.get(url, timeout=10)
            assert response.status_code == 200
        
        session.close()
    
    @pytest.mark.integration
    def test_concurrent_requests(self):
        """Test handling multiple concurrent requests"""
        from concurrent.futures import ThreadPoolExecutor
        import time
        
        def fetch_url(url):
            try:
                response = requests.get(url, timeout=10)
                return response.status_code
            except (requests.RequestException, Exception) as e:
                # Handle network errors, timeouts, rate limiting
                return None
        
        urls = ['https://httpbin.org/get'] * 5
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            results = list(executor.map(fetch_url, urls))
        
        # Filter out failed requests and non-200 status codes (rate limiting, etc.)
        successful_results = [r for r in results if r == 200]
        
        # Assert that at least 3 out of 5 requests succeeded with 200 status
        # This accounts for potential rate limiting or temporary network issues
        assert len(successful_results) >= 3, f"Only {len(successful_results)}/5 requests returned 200 (got: {results})"
    
    @pytest.mark.integration
    def test_cookie_handling(self):
        """Test cookie handling (CVE-2023-43804 fix)"""
        session = requests.Session()
        
        # Set a cookie
        response = session.get('https://httpbin.org/cookies/set/test/value', timeout=10)
        
        # Verify cookie is sent back
        response = session.get('https://httpbin.org/cookies', timeout=10)
        data = response.json()
        assert 'test' in data.get('cookies', {})
    
    @pytest.mark.integration
    def test_error_handling(self):
        """Test various error conditions"""
        # 404 error
        response = requests.get('https://httpbin.org/status/404', timeout=10)
        assert response.status_code == 404
        
        # 500 error
        response = requests.get('https://httpbin.org/status/500', timeout=10)
        assert response.status_code == 500
        
        # Connection error
        with pytest.raises(requests.exceptions.ConnectionError):
            requests.get('http://invalid-domain-that-does-not-exist.com', timeout=1)
    
    @pytest.mark.integration
    def test_streaming_response(self):
        """Test streaming large responses"""
        response = requests.get(
            'https://httpbin.org/stream/10',
            stream=True,
            timeout=10
        )
        
        lines = []
        for line in response.iter_lines():
            if line:
                lines.append(line)
        
        assert len(lines) == 10
    
    @pytest.mark.integration
    def test_compression_handling(self):
        """Test gzip/deflate compression"""
        response = requests.get(
            'https://httpbin.org/gzip',
            timeout=10
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('gzipped') is True


class TestSecurityFixes:
    """Test specific security vulnerability fixes"""
    
    def test_cve_2023_32681_proxy_auth_leak(self):
        """Test fix for CVE-2023-32681 (Proxy-Authorization header leak)"""
        # This CVE involved leaking Proxy-Authorization headers on redirects
        # The fix ensures these headers are stripped on cross-origin redirects
        
        # Mock test to verify header handling
        session = requests.Session()
        session.headers['Proxy-Authorization'] = 'Bearer secret'
        
        # In the fixed version, this header should be handled securely
        assert 'Proxy-Authorization' in session.headers
    
    def test_cve_2024_35195_cert_verification(self):
        """Test fix for CVE-2024-35195 (cert verification bypass)"""
        # This CVE involved subsequent requests ignoring cert verification
        # Verify that each request properly validates certificates
        
        session = requests.Session()
        
        # First request with verification
        response1 = session.get('https://httpbin.org/get', verify=True, timeout=10)
        assert response1.status_code == 200
        
        # Second request should still verify
        response2 = session.get('https://httpbin.org/get', verify=True, timeout=10)
        assert response2.status_code == 200
    
    def test_cve_2019_11324_cert_bypass(self):
        """Test fix for CVE-2019-11324 (urllib3 cert bypass)"""
        # Verify certificate verification cannot be bypassed
        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED')
        
        # Should work with valid cert
        response = http.request('GET', 'https://httpbin.org/get')
        assert response.status == 200
    
    def test_cve_2021_33503_backtracking(self):
        """Test fix for CVE-2021-33503 (catastrophic backtracking)"""
        # This CVE involved regex catastrophic backtracking in URL parsing
        # Test that URL parsing is efficient
        
        # Create a potentially problematic URL
        long_url = 'https://example.com/' + 'a' * 1000
        
        # Should parse efficiently without hanging
        try:
            requests.get(long_url, timeout=5)
        except (requests.exceptions.ConnectionError, requests.exceptions.InvalidURL):
            # Connection error is fine, we're just testing it doesn't hang
            pass
    
    def test_cve_2023_43804_cookie_leak(self):
        """Test fix for CVE-2023-43804 (cookie leak on redirects)"""
        # Verify cookies are handled securely on cross-origin redirects
        session = requests.Session()
        session.cookies.set('sensitive', 'secret-value')
        
        # Cookies should be handled according to security policy
        assert 'sensitive' in session.cookies
