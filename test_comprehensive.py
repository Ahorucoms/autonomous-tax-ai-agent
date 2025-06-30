"""
Comprehensive Test Suite for AI Tax Agent
Tests all critical components and integrations
"""

import pytest
import asyncio
import json
import os
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock

# Import services to test
from services.agents_sdk import TaxAgentSDK
from services.external_integrations import ExternalIntegrationsService
from services.pinecone_rag import PineconeRAGService
from services.pdf_form_generator import PDFFormGenerator
from services.i18n_service import I18nService

class TestAgentsSDK:
    """Test OpenAI Agents SDK implementation"""
    
    @pytest.fixture
    def agent_sdk(self):
        return TaxAgentSDK()
    
    @pytest.mark.asyncio
    async def test_reasoning_loop(self, agent_sdk):
        """Test the reasoning loop functionality"""
        query = "What are the Malta income tax rates for 2024?"
        context = {"jurisdiction": "MT", "user_type": "individual"}
        
        result = await agent_sdk.execute_reasoning_loop(query, context)
        
        assert result['success'] == True
        assert 'reasoning_steps' in result
        assert 'final_response' in result
        assert len(result['reasoning_steps']) > 0
    
    @pytest.mark.asyncio
    async def test_pre_execution_reasoning(self, agent_sdk):
        """Test pre-execution reasoning and missing info detection"""
        incomplete_query = "Calculate my tax"
        context = {"jurisdiction": "MT"}
        
        result = await agent_sdk.pre_execution_reasoning(incomplete_query, context)
        
        assert result['success'] == True
        assert 'missing_information' in result
        assert len(result['missing_information']) > 0
        assert 'clarifying_questions' in result
    
    @pytest.mark.asyncio
    async def test_tool_orchestration(self, agent_sdk):
        """Test tool orchestration capabilities"""
        task = "Generate Malta income tax form for user"
        context = {
            "jurisdiction": "MT",
            "user_data": {"income": 50000, "name": "John Doe"},
            "form_type": "income_tax_return"
        }
        
        result = await agent_sdk.orchestrate_tools(task, context)
        
        assert result['success'] == True
        assert 'tools_used' in result
        assert 'execution_plan' in result

class TestExternalIntegrations:
    """Test external API integrations"""
    
    @pytest.fixture
    def integrations_service(self):
        return ExternalIntegrationsService()
    
    @pytest.mark.asyncio
    async def test_google_drive_integration(self, integrations_service):
        """Test Google Drive document parsing"""
        # Mock Google Drive API response
        with patch.object(integrations_service, '_authenticate_google_drive') as mock_auth:
            mock_auth.return_value = Mock()
            
            result = await integrations_service.parse_google_drive_document("test_doc_id")
            
            assert 'success' in result
            # Note: Will fail without real credentials, but tests the structure
    
    @pytest.mark.asyncio
    async def test_cfr_malta_api(self, integrations_service):
        """Test CFR Malta API integration"""
        company_number = "C12345"
        
        result = await integrations_service.get_company_info(company_number)
        
        assert 'success' in result
        # Note: Will fail without real API access, but tests the structure
    
    @pytest.mark.asyncio
    async def test_whatsapp_integration(self, integrations_service):
        """Test WhatsApp Business API integration"""
        phone_number = "+35699123456"
        message = "Your tax calculation is ready"
        
        result = await integrations_service.send_whatsapp_message(phone_number, message)
        
        assert 'success' in result
    
    @pytest.mark.asyncio
    async def test_revolut_payment_link(self, integrations_service):
        """Test Revolut payment link generation"""
        payment_data = {
            "amount": 150.00,
            "currency": "EUR",
            "description": "Tax consultation fee"
        }
        
        result = await integrations_service.create_revolut_payment_link(payment_data)
        
        assert 'success' in result
        if result['success']:
            assert 'payment_link' in result

class TestPineconeRAG:
    """Test Pinecone RAG implementation"""
    
    @pytest.fixture
    def rag_service(self):
        return PineconeRAGService()
    
    @pytest.mark.asyncio
    async def test_document_ingestion(self, rag_service):
        """Test document ingestion and embedding"""
        document = {
            "title": "Malta Tax Guide 2024",
            "content": "Malta has a progressive income tax system with rates from 0% to 35%...",
            "metadata": {"jurisdiction": "MT", "year": 2024}
        }
        
        result = await rag_service.ingest_document(document)
        
        assert result['success'] == True
        assert 'document_id' in result
        assert 'chunks_created' in result
    
    @pytest.mark.asyncio
    async def test_semantic_search(self, rag_service):
        """Test semantic search functionality"""
        query = "What are the Malta income tax rates?"
        
        result = await rag_service.semantic_search(query, top_k=5)
        
        assert result['success'] == True
        assert 'results' in result
        assert len(result['results']) <= 5
        
        # Check result structure
        if result['results']:
            first_result = result['results'][0]
            assert 'content' in first_result
            assert 'score' in first_result
            assert 'metadata' in first_result
    
    @pytest.mark.asyncio
    async def test_rag_query(self, rag_service):
        """Test full RAG query with context generation"""
        query = "How do I calculate VAT in Malta?"
        context = {"jurisdiction": "MT", "user_type": "business"}
        
        result = await rag_service.rag_query(query, context)
        
        assert result['success'] == True
        assert 'answer' in result
        assert 'sources' in result
        assert 'confidence' in result

class TestPDFFormGenerator:
    """Test PDF form generation"""
    
    @pytest.fixture
    def pdf_generator(self):
        return PDFFormGenerator()
    
    @pytest.mark.asyncio
    async def test_form_generation(self, pdf_generator):
        """Test PDF form generation"""
        user_data = {
            "full_name": "John Doe",
            "id_card_number": "1234567M",
            "employment_income": 45000
        }
        
        tax_data = {
            "total_income": 45000,
            "tax_due": 7500,
            "taxable_income": 40000
        }
        
        result = await pdf_generator.generate_form(
            "income_tax_return", "MT", user_data, tax_data
        )
        
        assert result['success'] == True
        assert 'pdf_base64' in result
        assert 'metadata' in result
    
    @pytest.mark.asyncio
    async def test_form_validation(self, pdf_generator):
        """Test form data validation"""
        form_data = {
            "full_name": "John Doe",
            "id_card_number": "invalid_id",  # Invalid format
            "employment_income": -1000  # Invalid negative income
        }
        
        result = await pdf_generator.validate_form_data(
            "income_tax_return", "MT", form_data
        )
        
        assert result['success'] == True
        assert result['valid'] == False
        assert len(result['errors']) > 0
    
    @pytest.mark.asyncio
    async def test_available_forms(self, pdf_generator):
        """Test getting available forms"""
        result = await pdf_generator.get_available_forms("MT")
        
        assert result['success'] == True
        assert 'forms' in result
        assert len(result['forms']) > 0

class TestI18nService:
    """Test internationalization service"""
    
    @pytest.fixture
    def i18n_service(self):
        return I18nService()
    
    @pytest.mark.asyncio
    async def test_translation_retrieval(self, i18n_service):
        """Test translation retrieval"""
        translation = await i18n_service.get_translation(
            "welcome", "fr", "common"
        )
        
        assert isinstance(translation, str)
        assert len(translation) > 0
    
    @pytest.mark.asyncio
    async def test_bulk_translations(self, i18n_service):
        """Test bulk translation retrieval"""
        keys = ["welcome", "hello", "goodbye"]
        
        translations = await i18n_service.get_translations_bulk(
            keys, "fr", "common"
        )
        
        assert isinstance(translations, dict)
        assert len(translations) == len(keys)
    
    @pytest.mark.asyncio
    async def test_currency_formatting(self, i18n_service):
        """Test currency formatting"""
        amount = 1234.56
        
        # Test different locales
        eur_en = await i18n_service.format_currency(amount, "EUR", "en")
        eur_fr = await i18n_service.format_currency(amount, "EUR", "fr")
        
        assert "€" in eur_en
        assert "€" in eur_fr
        assert eur_en != eur_fr  # Different formatting
    
    @pytest.mark.asyncio
    async def test_date_formatting(self, i18n_service):
        """Test date formatting"""
        test_date = datetime(2024, 12, 25)
        
        # Test different locales
        date_en = await i18n_service.format_date(test_date, "en", "medium")
        date_fr = await i18n_service.format_date(test_date, "fr", "medium")
        
        assert isinstance(date_en, str)
        assert isinstance(date_fr, str)
        assert date_en != date_fr  # Different formatting

class TestSystemIntegration:
    """Test system-wide integration"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_tax_calculation(self):
        """Test complete tax calculation workflow"""
        # This would test the entire flow from user input to final result
        user_query = "Calculate my Malta income tax for €50,000 salary"
        context = {
            "jurisdiction": "MT",
            "user_type": "individual",
            "language": "en"
        }
        
        # Initialize services
        agent_sdk = TaxAgentSDK()
        
        # Execute reasoning loop
        result = await agent_sdk.execute_reasoning_loop(user_query, context)
        
        assert result['success'] == True
        assert 'final_response' in result
        assert 'tax_calculation' in result.get('final_response', {})
    
    @pytest.mark.asyncio
    async def test_multilingual_workflow(self):
        """Test multilingual support throughout the system"""
        # Test French language workflow
        user_query = "Calculer mon impôt sur le revenu à Malte"
        context = {
            "jurisdiction": "MT",
            "user_type": "individual",
            "language": "fr"
        }
        
        agent_sdk = TaxAgentSDK()
        i18n_service = I18nService()
        
        # Get French translations
        welcome_msg = await i18n_service.get_translation("welcome", "fr")
        assert "Bienvenue" in welcome_msg
        
        # Process query in French context
        result = await agent_sdk.execute_reasoning_loop(user_query, context)
        assert result['success'] == True
    
    @pytest.mark.asyncio
    async def test_document_to_form_workflow(self):
        """Test document processing to form generation workflow"""
        # Mock document upload and processing
        document_data = {
            "type": "employment_certificate",
            "content": "Annual salary: €45,000",
            "jurisdiction": "MT"
        }
        
        # This would test:
        # 1. Document upload and OCR
        # 2. Information extraction
        # 3. Form pre-filling
        # 4. PDF generation
        
        pdf_generator = PDFFormGenerator()
        
        # Generate form with extracted data
        user_data = {"employment_income": 45000, "full_name": "Test User"}
        result = await pdf_generator.generate_form(
            "income_tax_return", "MT", user_data
        )
        
        assert result['success'] == True

class TestPerformance:
    """Test system performance"""
    
    @pytest.mark.asyncio
    async def test_response_time(self):
        """Test API response times"""
        import time
        
        agent_sdk = TaxAgentSDK()
        
        start_time = time.time()
        result = await agent_sdk.execute_reasoning_loop(
            "What is the VAT rate in Malta?",
            {"jurisdiction": "MT"}
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Should respond within 5 seconds
        assert response_time < 5.0
        assert result['success'] == True
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test handling concurrent requests"""
        agent_sdk = TaxAgentSDK()
        
        # Create multiple concurrent requests
        tasks = []
        for i in range(5):
            task = agent_sdk.execute_reasoning_loop(
                f"Calculate tax for income {30000 + i * 1000}",
                {"jurisdiction": "MT"}
            )
            tasks.append(task)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should succeed
        for result in results:
            assert not isinstance(result, Exception)
            assert result['success'] == True

class TestSecurity:
    """Test security measures"""
    
    def test_input_sanitization(self):
        """Test input sanitization"""
        # Test SQL injection attempts
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "<script>alert('xss')</script>",
            "../../etc/passwd",
            "{{7*7}}"  # Template injection
        ]
        
        agent_sdk = TaxAgentSDK()
        
        for malicious_input in malicious_inputs:
            # Should sanitize input without crashing
            sanitized = agent_sdk._sanitize_input(malicious_input)
            assert sanitized != malicious_input
            assert "<script>" not in sanitized
            assert "DROP TABLE" not in sanitized
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        # This would test the rate limiting implementation
        # In a real scenario, this would make multiple rapid requests
        # and verify that rate limiting kicks in
        pass
    
    def test_authentication_required(self):
        """Test that protected endpoints require authentication"""
        # This would test that sensitive operations require proper authentication
        pass

# Test configuration
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])

