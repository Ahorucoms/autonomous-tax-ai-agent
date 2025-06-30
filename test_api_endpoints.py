"""
Comprehensive integration tests for Malta Tax AI API endpoints
"""
import pytest
import requests
import json
import time
from decimal import Decimal


class TestTaxCalculationAPI:
    """Integration tests for tax calculation API endpoints"""
    
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
    
    def test_health_endpoint(self):
        """Test API health check endpoint"""
        response = requests.get(f"{self.BASE_URL}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
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
        
        assert data["success"] is True
        assert "total_tax" in data
        assert "tax_breakdown" in data
        assert data["total_tax"] > 0
        
        # Verify response structure
        breakdown = data["tax_breakdown"]
        assert isinstance(breakdown, list)
        assert len(breakdown) > 0
        
        for bracket in breakdown:
            assert "rate" in bracket
            assert "amount" in bracket
            assert "range" in bracket
    
    def test_social_security_class1_api(self):
        """Test Class 1 social security calculation API"""
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
        
        assert data["success"] is True
        assert "employee_contribution" in data
        assert "employer_contribution" in data
        assert "total_contribution" in data
        
        # Verify calculations
        employee = data["employee_contribution"]
        employer = data["employer_contribution"]
        total = data["total_contribution"]
        
        assert employee > 0
        assert employer > 0
        assert abs(total - (employee + employer)) < 0.01
    
    def test_social_security_class2_api(self):
        """Test Class 2 social security calculation API"""
        payload = {
            "annual_income": 35000
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/tax/social-security/class2",
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "contribution_amount" in data
        assert "contribution_rate" in data
        assert data["contribution_amount"] > 0
    
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
        
        assert data["success"] is True
        assert data["vat_amount"] == 180
        assert data["total_amount"] == 1180
        assert data["net_amount"] == 1000
    
    def test_stamp_duty_calculation_api(self):
        """Test stamp duty calculation API endpoint"""
        payload = {
            "property_value": 250000,
            "is_first_time_buyer": False
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/tax/stamp-duty",
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "stamp_duty" in data
        assert "effective_rate" in data
        assert data["stamp_duty"] > 0
    
    def test_capital_gains_tax_api(self):
        """Test capital gains tax calculation API endpoint"""
        payload = {
            "purchase_price": 100000,
            "sale_price": 150000,
            "holding_period_years": 3
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/tax/capital-gains",
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "capital_gain" in data
        assert "tax_amount" in data
        assert data["capital_gain"] == 50000
    
    def test_comprehensive_tax_calculation_api(self):
        """Test comprehensive tax calculation API endpoint"""
        payload = {
            "annual_income": 50000,
            "marital_status": "single",
            "has_property": True,
            "property_value": 200000,
            "business_income": 10000,
            "investment_income": 5000
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/tax/comprehensive",
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "total_tax_liability" in data
        assert "breakdown" in data
        
        breakdown = data["breakdown"]
        assert "income_tax" in breakdown
        assert "social_security" in breakdown
        assert breakdown["income_tax"] > 0
    
    def test_tax_rates_api(self):
        """Test tax rates information API endpoint"""
        response = requests.get(f"{self.BASE_URL}/api/tax/rates")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "income_tax_brackets" in data
        assert "social_security_rates" in data
        assert "vat_rates" in data
        
        # Verify structure
        brackets = data["income_tax_brackets"]
        assert isinstance(brackets, list)
        assert len(brackets) > 0
        
        for bracket in brackets:
            assert "min_income" in bracket
            assert "rate" in bracket
    
    def test_api_error_handling(self):
        """Test API error handling for invalid requests"""
        # Test missing required fields
        response = requests.post(
            f"{self.BASE_URL}/api/tax/income-tax",
            json={}
        )
        
        assert response.status_code == 400
        
        # Test invalid data types
        response = requests.post(
            f"{self.BASE_URL}/api/tax/income-tax",
            json={
                "annual_income": "invalid",
                "marital_status": "single"
            }
        )
        
        assert response.status_code == 400
        
        # Test invalid marital status
        response = requests.post(
            f"{self.BASE_URL}/api/tax/income-tax",
            json={
                "annual_income": 50000,
                "marital_status": "invalid_status"
            }
        )
        
        assert response.status_code == 400


class TestFormGenerationAPI:
    """Integration tests for form generation API endpoints"""
    
    BASE_URL = "http://localhost:5004"
    
    def test_form_templates_api(self):
        """Test form templates listing API"""
        response = requests.get(f"{self.BASE_URL}/api/forms/templates")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "templates" in data
        templates = data["templates"]
        assert len(templates) > 0
        
        # Verify template structure
        for template in templates:
            assert "id" in template
            assert "name" in template
            assert "fields" in template
    
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
        
        response = requests.post(
            f"{self.BASE_URL}/api/forms/create",
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "form_id" in data
        assert "status" in data
        assert data["status"] == "draft"
    
    def test_form_validation_api(self):
        """Test form validation API endpoint"""
        # First create a form
        create_payload = {
            "template_id": "fs3",
            "data": {
                "taxpayer_name": "John Doe",
                "id_number": "123456M",
                "annual_income": 45000,
                "tax_year": 2025
            }
        }
        
        create_response = requests.post(
            f"{self.BASE_URL}/api/forms/create",
            json=create_payload
        )
        
        assert create_response.status_code == 200
        form_id = create_response.json()["form_id"]
        
        # Validate the form
        response = requests.post(f"{self.BASE_URL}/api/forms/{form_id}/validate")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "is_valid" in data
        assert "errors" in data
        assert "warnings" in data


class TestComplianceAPI:
    """Integration tests for compliance API endpoints"""
    
    BASE_URL = "http://localhost:5004"
    
    def test_compliance_check_api(self):
        """Test compliance check API endpoint"""
        payload = {
            "user_id": "test_user_123",
            "annual_income": 45000,
            "filing_status": "individual",
            "last_filing_date": "2024-06-30"
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/compliance/check",
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "compliance_score" in data
        assert "status" in data
        assert "issues" in data
        assert "recommendations" in data
        
        # Verify score is valid
        score = data["compliance_score"]
        assert 0 <= score <= 100
    
    def test_deadline_tracking_api(self):
        """Test deadline tracking API endpoint"""
        response = requests.get(f"{self.BASE_URL}/api/compliance/deadlines")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "upcoming_deadlines" in data
        deadlines = data["upcoming_deadlines"]
        
        # Verify deadline structure
        for deadline in deadlines:
            assert "type" in deadline
            assert "date" in deadline
            assert "description" in deadline
            assert "severity" in deadline
    
    def test_penalty_calculation_api(self):
        """Test penalty calculation API endpoint"""
        payload = {
            "tax_type": "income_tax",
            "original_amount": 5000,
            "due_date": "2025-06-30",
            "payment_date": "2025-07-15"
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/compliance/penalty",
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "penalty_amount" in data
        assert "penalty_rate" in data
        assert "days_late" in data
        assert data["penalty_amount"] > 0
        assert data["days_late"] == 15


class TestDocumentProcessingAPI:
    """Integration tests for document processing API endpoints"""
    
    BASE_URL = "http://localhost:5004"
    
    def test_document_classification_api(self):
        """Test document classification API endpoint"""
        # Simulate document upload
        payload = {
            "document_type": "tax_certificate",
            "content": "This is a sample FS3 tax certificate document",
            "filename": "fs3_certificate.pdf"
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/document-processing/classify",
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "classification" in data
        assert "confidence" in data
        assert "extracted_data" in data
        
        # Verify confidence score
        confidence = data["confidence"]
        assert 0 <= confidence <= 1
    
    def test_data_extraction_api(self):
        """Test data extraction API endpoint"""
        payload = {
            "document_id": "test_doc_123",
            "document_type": "fs3",
            "content": "Taxpayer: John Doe, ID: 123456M, Income: €45,000"
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/document-processing/extract",
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "extracted_fields" in data
        assert "confidence_scores" in data
        
        extracted = data["extracted_fields"]
        assert len(extracted) > 0


class TestPerformanceAndLoad:
    """Performance and load testing for API endpoints"""
    
    BASE_URL = "http://localhost:5004"
    
    def test_api_response_times(self):
        """Test API response times under normal load"""
        endpoints = [
            ("/health", "GET", None),
            ("/api/tax/rates", "GET", None),
            ("/api/tax/income-tax", "POST", {
                "annual_income": 45000,
                "marital_status": "single"
            }),
            ("/api/tax/vat", "POST", {
                "amount": 1000,
                "vat_rate": 18
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
            assert response_time < 2.0  # Response should be under 2 seconds
    
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
                    }
                )
                results.put(response.status_code)
            except Exception as e:
                results.put(str(e))
        
        # Create 10 concurrent threads
        threads = []
        for _ in range(10):
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
        assert success_count >= 8


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

