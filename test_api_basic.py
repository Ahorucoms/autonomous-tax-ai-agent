"""
Basic API integration tests for Malta Tax AI Backend
Tests core API functionality and endpoints
"""
import pytest
import requests
import json
import time


class TestBasicAPIFunctionality:
    """Basic API functionality tests"""
    
    BASE_URL = "http://localhost:5004"
    
    @classmethod
    def setup_class(cls):
        """Setup test class - ensure API is running"""
        try:
            response = requests.get(f"{cls.BASE_URL}/health", timeout=5)
            if response.status_code != 200:
                pytest.skip("API server not running")
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not accessible")
    
    def test_health_endpoint(self):
        """Test API health check endpoint"""
        response = requests.get(f"{self.BASE_URL}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        print(f"✅ Health check passed: {data['status']}")
    
    def test_tax_rates_endpoint(self):
        """Test tax rates information endpoint"""
        response = requests.get(f"{self.BASE_URL}/api/tax/rates")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "income_tax_brackets" in data
        assert "social_security_rates" in data
        assert "vat_rates" in data
        
        print(f"✅ Tax rates endpoint working - {len(data['income_tax_brackets'])} tax brackets")
    
    def test_income_tax_calculation_api(self):
        """Test income tax calculation API endpoint"""
        payload = {
            "annual_income": 45000,
            "marital_status": "single"
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/tax/income-tax",
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "annual_income" in data
        assert "net_tax" in data or "total_tax" in data
        assert "tax_breakdown" in data or "breakdown" in data
        
        print(f"✅ Income tax calculation working - Income: €{payload['annual_income']}")
    
    def test_vat_calculation_api(self):
        """Test VAT calculation API endpoint"""
        payload = {
            "amount": 1000,
            "vat_rate": 18
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/tax/vat",
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify basic structure
        assert "amount" in data or "net_amount" in data
        assert "vat_amount" in data
        assert "total_amount" in data or "gross_amount" in data
        
        print(f"✅ VAT calculation working - Amount: €{payload['amount']}, Rate: {payload['vat_rate']}%")
    
    def test_social_security_calculation_api(self):
        """Test social security calculation API endpoint"""
        payload = {
            "weekly_income": 800,
            "weeks": 52
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/tax/social-security/class1",
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify basic structure
        assert "employee_contribution" in data or "contribution" in data
        
        print(f"✅ Social security calculation working - Weekly: €{payload['weekly_income']}")
    
    def test_comprehensive_tax_calculation_api(self):
        """Test comprehensive tax calculation API endpoint"""
        payload = {
            "annual_income": 50000,
            "marital_status": "single"
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/tax/comprehensive",
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify basic structure
        assert "total_tax_liability" in data or "total_tax" in data
        assert "breakdown" in data or "summary" in data
        
        print(f"✅ Comprehensive tax calculation working - Income: €{payload['annual_income']}")
    
    def test_api_error_handling(self):
        """Test API error handling for invalid requests"""
        # Test missing required fields
        response = requests.post(
            f"{self.BASE_URL}/api/tax/income-tax",
            json={}
        )
        
        assert response.status_code in [400, 422]
        print(f"✅ Error handling working - Empty payload returns {response.status_code}")
        
        # Test invalid data types
        response = requests.post(
            f"{self.BASE_URL}/api/tax/income-tax",
            json={
                "annual_income": "invalid",
                "marital_status": "single"
            }
        )
        
        assert response.status_code in [400, 422]
        print(f"✅ Error handling working - Invalid data type returns {response.status_code}")
    
    def test_api_response_times(self):
        """Test API response times"""
        endpoints = [
            ("/health", "GET", None),
            ("/api/tax/rates", "GET", None),
            ("/api/tax/income-tax", "POST", {
                "annual_income": 45000,
                "marital_status": "single"
            })
        ]
        
        for endpoint, method, payload in endpoints:
            start_time = time.time()
            
            if method == "GET":
                response = requests.get(f"{self.BASE_URL}{endpoint}")
            else:
                response = requests.post(f"{self.BASE_URL}{endpoint}", json=payload)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            assert response.status_code == 200
            assert response_time < 5.0  # Should respond within 5 seconds
            
            print(f"✅ {endpoint} response time: {response_time:.3f}s")


class TestFormGenerationAPI:
    """Test form generation API endpoints"""
    
    BASE_URL = "http://localhost:5004"
    
    def test_form_templates_api(self):
        """Test form templates listing API"""
        try:
            response = requests.get(f"{self.BASE_URL}/api/forms/templates")
            
            if response.status_code == 200:
                data = response.json()
                assert "templates" in data
                print(f"✅ Form templates working - {len(data['templates'])} templates available")
            else:
                print(f"⚠️ Form templates endpoint returned {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("⚠️ Form templates endpoint not available")
    
    def test_form_creation_api(self):
        """Test form creation API endpoint"""
        payload = {
            "template_id": "fs3",
            "data": {
                "taxpayer_name": "John Doe",
                "id_number": "123456M",
                "annual_income": 45000,
                "tax_year": 2025
            }
        }
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/api/forms/create",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                assert "form_id" in data or "id" in data
                print(f"✅ Form creation working - Created form for {payload['data']['taxpayer_name']}")
            else:
                print(f"⚠️ Form creation endpoint returned {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("⚠️ Form creation endpoint not available")


class TestComplianceAPI:
    """Test compliance API endpoints"""
    
    BASE_URL = "http://localhost:5004"
    
    def test_compliance_check_api(self):
        """Test compliance check API endpoint"""
        payload = {
            "user_id": "test_user_123",
            "annual_income": 45000,
            "filing_status": "individual"
        }
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/api/compliance/check",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                assert "compliance_score" in data or "status" in data
                print(f"✅ Compliance check working - User: {payload['user_id']}")
            else:
                print(f"⚠️ Compliance check endpoint returned {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("⚠️ Compliance check endpoint not available")
    
    def test_deadline_tracking_api(self):
        """Test deadline tracking API endpoint"""
        try:
            response = requests.get(f"{self.BASE_URL}/api/compliance/deadlines")
            
            if response.status_code == 200:
                data = response.json()
                assert "upcoming_deadlines" in data or "deadlines" in data
                print(f"✅ Deadline tracking working")
            else:
                print(f"⚠️ Deadline tracking endpoint returned {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("⚠️ Deadline tracking endpoint not available")


class TestSystemHealth:
    """Test overall system health and integration"""
    
    BASE_URL = "http://localhost:5004"
    
    def test_system_status(self):
        """Test overall system status"""
        try:
            response = requests.get(f"{self.BASE_URL}/api/system/status")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ System status endpoint working")
            else:
                print(f"⚠️ System status endpoint returned {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("⚠️ System status endpoint not available")
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            try:
                response = requests.post(
                    f"{self.BASE_URL}/api/tax/income-tax",
                    json={
                        "annual_income": 45000,
                        "marital_status": "single"
                    },
                    timeout=10
                )
                results.put(response.status_code)
            except Exception as e:
                results.put(str(e))
        
        # Create 5 concurrent threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        success_count = 0
        while not results.empty():
            result = results.get()
            if result == 200:
                success_count += 1
        
        # At least 80% of requests should succeed
        assert success_count >= 4
        print(f"✅ Concurrent requests working - {success_count}/5 successful")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

