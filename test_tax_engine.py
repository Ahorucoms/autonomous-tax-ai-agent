"""
Comprehensive unit tests for Malta Tax Calculation Engine
"""
import pytest
from decimal import Decimal
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from services.tax_engine import MaltaTaxEngine, MaritalStatus, ResidencyStatus, VATRate
from decimal import Decimal


class TestMaltaTaxEngine:
    """Test suite for Malta Tax Engine calculations"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.tax_engine = MaltaTaxEngine()
    
    def test_income_tax_calculation_basic(self):
        """Test basic income tax calculation"""
        # Test case: €25,000 annual income, single
        result = self.tax_engine.calculate_income_tax(
            annual_income=Decimal('25000'),
            marital_status=MaritalStatus.SINGLE
        )
        
        assert "annual_income" in result
        assert "net_tax" in result
        assert "tax_breakdown" in result
        assert result["net_tax"] >= 0
        
        # Verify tax brackets are applied correctly
        breakdown = result["tax_breakdown"]
        assert len(breakdown) > 0
        assert all("rate" in bracket for bracket in breakdown)
        assert all("tax_amount" in bracket for bracket in breakdown)
    
    def test_income_tax_calculation_married(self):
        """Test income tax calculation for married status"""
        result = self.tax_engine.calculate_income_tax(
            annual_income=Decimal('50000'),
            marital_status=MaritalStatus.MARRIED
        )
        
        assert "annual_income" in result
        assert result["net_tax"] >= 0
        
        # Married status should have different tax calculation
        single_result = self.tax_engine.calculate_income_tax(
            annual_income=Decimal('50000'),
            marital_status=MaritalStatus.SINGLE
        )
        
        # Tax amounts should be different for married vs single
        assert result["net_tax"] != single_result["net_tax"]
    
    def test_income_tax_progressive_brackets(self):
        """Test progressive tax bracket application"""
        # Test multiple income levels to verify progressive taxation
        test_cases = [
            {"income": 10000, "expected_min": 0, "expected_max": 2000},
            {"income": 30000, "expected_min": 2000, "expected_max": 8000},
            {"income": 60000, "expected_min": 8000, "expected_max": 20000},
        ]
        
        for case in test_cases:
            result = self.tax_engine.calculate_income_tax(
                annual_income=case["income"],
                marital_status="single"
            )
            
            assert result["success"] is True
            tax_amount = result["total_tax"]
            assert case["expected_min"] <= tax_amount <= case["expected_max"]
    
    def test_social_security_class1(self):
        """Test Class 1 (Employee) social security contributions"""
        result = self.tax_engine.calculate_social_security_class1(
            weekly_income=500,
            weeks=52
        )
        
        assert result["success"] is True
        assert "employee_contribution" in result
        assert "employer_contribution" in result
        assert "total_contribution" in result
        
        # Verify contribution rates
        employee_contrib = result["employee_contribution"]
        employer_contrib = result["employer_contribution"]
        assert employee_contrib > 0
        assert employer_contrib > 0
        assert result["total_contribution"] == employee_contrib + employer_contrib
    
    def test_social_security_class2(self):
        """Test Class 2 (Self-Employed) social security contributions"""
        result = self.tax_engine.calculate_social_security_class2(
            annual_income=30000
        )
        
        assert result["success"] is True
        assert "contribution_amount" in result
        assert "contribution_rate" in result
        assert result["contribution_amount"] > 0
    
    def test_vat_calculation_standard_rate(self):
        """Test VAT calculation with standard rate"""
        result = self.tax_engine.calculate_vat(
            amount=1000,
            vat_rate=18
        )
        
        assert result["success"] is True
        assert result["vat_amount"] == 180
        assert result["total_amount"] == 1180
        assert result["net_amount"] == 1000
    
    def test_vat_calculation_multiple_rates(self):
        """Test VAT calculation with different rates"""
        test_rates = [18, 12, 7, 5, 0]
        base_amount = 1000
        
        for rate in test_rates:
            result = self.tax_engine.calculate_vat(
                amount=base_amount,
                vat_rate=rate
            )
            
            assert result["success"] is True
            expected_vat = base_amount * rate / 100
            assert result["vat_amount"] == expected_vat
            assert result["total_amount"] == base_amount + expected_vat
    
    def test_stamp_duty_calculation(self):
        """Test stamp duty calculation for property transfers"""
        result = self.tax_engine.calculate_stamp_duty(
            property_value=250000,
            is_first_time_buyer=False
        )
        
        assert result["success"] is True
        assert "stamp_duty" in result
        assert "effective_rate" in result
        assert result["stamp_duty"] > 0
    
    def test_stamp_duty_first_time_buyer_exemption(self):
        """Test stamp duty exemption for first-time buyers"""
        # First-time buyer
        result_ftb = self.tax_engine.calculate_stamp_duty(
            property_value=200000,
            is_first_time_buyer=True
        )
        
        # Regular buyer
        result_regular = self.tax_engine.calculate_stamp_duty(
            property_value=200000,
            is_first_time_buyer=False
        )
        
        assert result_ftb["success"] is True
        assert result_regular["success"] is True
        
        # First-time buyer should pay less stamp duty
        assert result_ftb["stamp_duty"] < result_regular["stamp_duty"]
    
    def test_capital_gains_tax(self):
        """Test capital gains tax calculation"""
        result = self.tax_engine.calculate_capital_gains_tax(
            purchase_price=100000,
            sale_price=150000,
            holding_period_years=3
        )
        
        assert result["success"] is True
        assert "capital_gain" in result
        assert "tax_amount" in result
        assert result["capital_gain"] == 50000
        assert result["tax_amount"] > 0
    
    def test_capital_gains_long_term_exemption(self):
        """Test capital gains tax exemption for long-term holdings"""
        # Short-term holding (taxable)
        result_short = self.tax_engine.calculate_capital_gains_tax(
            purchase_price=100000,
            sale_price=150000,
            holding_period_years=2
        )
        
        # Long-term holding (potentially exempt)
        result_long = self.tax_engine.calculate_capital_gains_tax(
            purchase_price=100000,
            sale_price=150000,
            holding_period_years=10
        )
        
        assert result_short["success"] is True
        assert result_long["success"] is True
        
        # Long-term holdings should have lower or zero tax
        assert result_long["tax_amount"] <= result_short["tax_amount"]
    
    def test_comprehensive_tax_calculation(self):
        """Test comprehensive tax liability calculation"""
        result = self.tax_engine.calculate_comprehensive_tax(
            annual_income=50000,
            marital_status="single",
            has_property=True,
            property_value=200000,
            business_income=10000,
            investment_income=5000
        )
        
        assert result["success"] is True
        assert "total_tax_liability" in result
        assert "breakdown" in result
        
        breakdown = result["breakdown"]
        assert "income_tax" in breakdown
        assert "social_security" in breakdown
        assert breakdown["income_tax"] > 0
        assert breakdown["social_security"] > 0
    
    def test_edge_cases_zero_income(self):
        """Test edge case: zero income"""
        result = self.tax_engine.calculate_income_tax(
            annual_income=0,
            marital_status="single"
        )
        
        assert result["success"] is True
        assert result["total_tax"] == 0
    
    def test_edge_cases_negative_values(self):
        """Test edge case: negative values"""
        result = self.tax_engine.calculate_income_tax(
            annual_income=-1000,
            marital_status="single"
        )
        
        # Should handle negative income gracefully
        assert result["success"] is False or result["total_tax"] == 0
    
    def test_edge_cases_very_high_income(self):
        """Test edge case: very high income"""
        result = self.tax_engine.calculate_income_tax(
            annual_income=1000000,
            marital_status="single"
        )
        
        assert result["success"] is True
        assert result["total_tax"] > 0
        
        # Should apply highest tax bracket
        assert result["total_tax"] > 300000  # Expect significant tax
    
    def test_decimal_precision(self):
        """Test decimal precision in calculations"""
        result = self.tax_engine.calculate_vat(
            amount=123.45,
            vat_rate=18
        )
        
        assert result["success"] is True
        # VAT should be calculated with proper precision
        expected_vat = 123.45 * 0.18
        assert abs(result["vat_amount"] - expected_vat) < 0.01
    
    def test_invalid_parameters(self):
        """Test handling of invalid parameters"""
        # Invalid marital status
        result = self.tax_engine.calculate_income_tax(
            annual_income=50000,
            marital_status="invalid_status"
        )
        
        # Should handle gracefully
        assert result["success"] is False or "error" in result
        
        # Invalid VAT rate
        result = self.tax_engine.calculate_vat(
            amount=1000,
            vat_rate=150  # Invalid rate
        )
        
        # Should handle gracefully
        assert result["success"] is False or "error" in result


class TestTaxEngineIntegration:
    """Integration tests for tax engine components"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.tax_engine = TaxEngine()
    
    def test_full_tax_scenario_individual(self):
        """Test complete tax scenario for individual taxpayer"""
        # Simulate a complete individual tax calculation
        annual_income = 45000
        property_value = 180000
        
        # Calculate all applicable taxes
        income_tax = self.tax_engine.calculate_income_tax(
            annual_income=annual_income,
            marital_status="single"
        )
        
        social_security = self.tax_engine.calculate_social_security_class1(
            weekly_income=annual_income / 52,
            weeks=52
        )
        
        stamp_duty = self.tax_engine.calculate_stamp_duty(
            property_value=property_value,
            is_first_time_buyer=True
        )
        
        # Verify all calculations succeeded
        assert income_tax["success"] is True
        assert social_security["success"] is True
        assert stamp_duty["success"] is True
        
        # Calculate total tax burden
        total_tax = (
            income_tax["total_tax"] +
            social_security["employee_contribution"] +
            stamp_duty["stamp_duty"]
        )
        
        assert total_tax > 0
        assert total_tax < annual_income  # Sanity check
    
    def test_full_tax_scenario_business(self):
        """Test complete tax scenario for business taxpayer"""
        business_income = 75000
        vat_transactions = 50000
        
        # Calculate business taxes
        income_tax = self.tax_engine.calculate_income_tax(
            annual_income=business_income,
            marital_status="single"
        )
        
        social_security = self.tax_engine.calculate_social_security_class2(
            annual_income=business_income
        )
        
        vat = self.tax_engine.calculate_vat(
            amount=vat_transactions,
            vat_rate=18
        )
        
        # Verify all calculations succeeded
        assert income_tax["success"] is True
        assert social_security["success"] is True
        assert vat["success"] is True
        
        # Calculate total tax burden
        total_tax = (
            income_tax["total_tax"] +
            social_security["contribution_amount"] +
            vat["vat_amount"]
        )
        
        assert total_tax > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

