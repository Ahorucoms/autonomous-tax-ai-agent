"""
Focused unit tests for Malta Tax Engine
Tests core tax calculation functionality
"""
import pytest
from decimal import Decimal
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from services.tax_engine import MaltaTaxEngine, MaritalStatus, ResidencyStatus, VATRate


class TestMaltaTaxEngineCore:
    """Core functionality tests for Malta Tax Engine"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.tax_engine = MaltaTaxEngine(tax_year=2025)
    
    def test_income_tax_calculation_basic(self):
        """Test basic income tax calculation"""
        result = self.tax_engine.calculate_income_tax(
            annual_income=Decimal('25000'),
            marital_status=MaritalStatus.SINGLE
        )
        
        # Verify result structure
        assert "annual_income" in result
        assert "net_tax" in result
        assert "tax_breakdown" in result
        assert "effective_rate" in result
        assert "marginal_rate" in result
        
        # Verify values are reasonable
        assert result["annual_income"] == 25000.0
        assert result["net_tax"] >= 0
        assert len(result["tax_breakdown"]) > 0
    
    def test_income_tax_married_vs_single(self):
        """Test income tax difference between married and single"""
        income = Decimal('40000')
        
        single_result = self.tax_engine.calculate_income_tax(
            annual_income=income,
            marital_status=MaritalStatus.SINGLE
        )
        
        married_result = self.tax_engine.calculate_income_tax(
            annual_income=income,
            marital_status=MaritalStatus.MARRIED
        )
        
        # Both should be valid calculations
        assert single_result["net_tax"] >= 0
        assert married_result["net_tax"] >= 0
        
        # Tax amounts should be different (married typically pays less)
        assert single_result["net_tax"] != married_result["net_tax"]
    
    def test_social_security_class1(self):
        """Test Class 1 (Employee) social security contributions"""
        result = self.tax_engine.calculate_social_security_class1(
            weekly_income=Decimal('500'),
            weeks=52
        )
        
        # Verify result structure
        assert "employee_contribution" in result
        assert "employer_contribution" in result
        assert "total_contribution" in result
        assert "contribution_rate" in result
        
        # Verify calculations
        employee_contrib = result["employee_contribution"]
        employer_contrib = result["employer_contribution"]
        total_contrib = result["total_contribution"]
        
        assert employee_contrib >= 0
        assert employer_contrib >= 0
        assert abs(total_contrib - (employee_contrib + employer_contrib)) < 0.01
    
    def test_social_security_class2(self):
        """Test Class 2 (Self-Employed) social security contributions"""
        result = self.tax_engine.calculate_social_security_class2(
            annual_income=Decimal('30000')
        )
        
        # Verify result structure
        assert "contribution_amount" in result
        assert "contribution_rate" in result
        assert "annual_income" in result
        
        # Verify values
        assert result["contribution_amount"] >= 0
        assert result["annual_income"] == 30000.0
    
    def test_vat_calculation_standard_rate(self):
        """Test VAT calculation with standard rate"""
        result = self.tax_engine.calculate_vat(
            net_amount=Decimal('1000'),
            vat_rate=VATRate.STANDARD
        )
        
        # Verify result structure
        assert "net_amount" in result
        assert "vat_amount" in result
        assert "gross_amount" in result
        assert "vat_rate" in result
        
        # Verify calculations (18% VAT)
        assert result["net_amount"] == 1000.0
        assert result["vat_amount"] == 180.0
        assert result["gross_amount"] == 1180.0
        assert result["vat_rate"] == 18.0
    
    def test_vat_calculation_multiple_rates(self):
        """Test VAT calculation with different rates"""
        base_amount = Decimal('1000')
        
        test_rates = [
            (VATRate.STANDARD, 180.0),    # 18%
            (VATRate.REDUCED_1, 120.0),   # 12%
            (VATRate.REDUCED_2, 70.0),    # 7%
            (VATRate.REDUCED_3, 50.0),    # 5%
            (VATRate.ZERO, 0.0)           # 0%
        ]
        
        for vat_rate, expected_vat in test_rates:
            result = self.tax_engine.calculate_vat(
                net_amount=base_amount,
                vat_rate=vat_rate
            )
            
            assert result["net_amount"] == 1000.0
            assert result["vat_amount"] == expected_vat
            assert result["gross_amount"] == 1000.0 + expected_vat
    
    def test_stamp_duty_calculation(self):
        """Test stamp duty calculation for property transfers"""
        result = self.tax_engine.calculate_stamp_duty(
            property_value=Decimal('250000'),
            is_first_time_buyer=False
        )
        
        # Verify result structure
        assert "property_value" in result
        assert "stamp_duty" in result
        assert "effective_rate" in result
        assert "is_first_time_buyer" in result
        
        # Verify values
        assert result["property_value"] == 250000.0
        assert result["stamp_duty"] > 0
        assert result["effective_rate"] > 0
    
    def test_stamp_duty_first_time_buyer_benefit(self):
        """Test stamp duty benefit for first-time buyers"""
        property_value = Decimal('200000')
        
        # Regular buyer
        regular_result = self.tax_engine.calculate_stamp_duty(
            property_value=property_value,
            is_first_time_buyer=False
        )
        
        # First-time buyer
        ftb_result = self.tax_engine.calculate_stamp_duty(
            property_value=property_value,
            is_first_time_buyer=True
        )
        
        # First-time buyer should pay less stamp duty
        assert ftb_result["stamp_duty"] < regular_result["stamp_duty"]
        assert ftb_result["effective_rate"] < regular_result["effective_rate"]
    
    def test_capital_gains_tax(self):
        """Test capital gains tax calculation"""
        result = self.tax_engine.calculate_capital_gains_tax(
            purchase_price=Decimal('100000'),
            sale_price=Decimal('150000'),
            holding_period_years=3,
            asset_type="property"
        )
        
        # Verify result structure
        assert "capital_gain" in result
        assert "tax_amount" in result
        assert "effective_rate" in result
        assert "holding_period_years" in result
        
        # Verify calculations
        assert result["capital_gain"] == 50000.0
        assert result["tax_amount"] >= 0
        assert result["holding_period_years"] == 3
    
    def test_comprehensive_tax_calculation(self):
        """Test comprehensive tax liability calculation"""
        result = self.tax_engine.calculate_comprehensive_tax_liability(
            annual_income=Decimal('50000'),
            marital_status=MaritalStatus.SINGLE,
            has_property=True,
            property_value=Decimal('200000'),
            business_income=Decimal('10000'),
            investment_income=Decimal('5000')
        )
        
        # Verify result structure
        assert "total_tax_liability" in result
        assert "breakdown" in result
        assert "summary" in result
        
        breakdown = result["breakdown"]
        assert "income_tax" in breakdown
        assert "social_security" in breakdown
        
        # Verify calculations
        assert result["total_tax_liability"] > 0
        assert breakdown["income_tax"] >= 0
        assert breakdown["social_security"] >= 0
    
    def test_edge_case_zero_income(self):
        """Test edge case: zero income"""
        result = self.tax_engine.calculate_income_tax(
            annual_income=Decimal('0'),
            marital_status=MaritalStatus.SINGLE
        )
        
        assert result["annual_income"] == 0.0
        assert result["net_tax"] == 0.0
        assert result["effective_rate"] == 0.0
    
    def test_edge_case_high_income(self):
        """Test edge case: very high income"""
        result = self.tax_engine.calculate_income_tax(
            annual_income=Decimal('500000'),
            marital_status=MaritalStatus.SINGLE
        )
        
        assert result["annual_income"] == 500000.0
        assert result["net_tax"] > 0
        assert result["effective_rate"] > 0
        
        # Should apply highest tax bracket
        assert result["marginal_rate"] > 30  # Expect high marginal rate
    
    def test_decimal_precision(self):
        """Test decimal precision in calculations"""
        result = self.tax_engine.calculate_vat(
            net_amount=Decimal('123.45'),
            vat_rate=VATRate.STANDARD
        )
        
        # VAT should be calculated with proper precision
        expected_vat = 123.45 * 0.18
        assert abs(result["vat_amount"] - expected_vat) < 0.01
        assert result["gross_amount"] == result["net_amount"] + result["vat_amount"]


class TestMaltaTaxEngineValidation:
    """Validation and error handling tests"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.tax_engine = MaltaTaxEngine()
    
    def test_negative_income_handling(self):
        """Test handling of negative income"""
        result = self.tax_engine.calculate_income_tax(
            annual_income=Decimal('-1000'),
            marital_status=MaritalStatus.SINGLE
        )
        
        # Should handle gracefully - taxable income should be 0
        assert result["taxable_income"] == 0.0
        assert result["net_tax"] == 0.0
    
    def test_large_numbers_handling(self):
        """Test handling of very large numbers"""
        result = self.tax_engine.calculate_income_tax(
            annual_income=Decimal('10000000'),  # 10 million
            marital_status=MaritalStatus.SINGLE
        )
        
        # Should handle large numbers without overflow
        assert result["annual_income"] == 10000000.0
        assert result["net_tax"] > 0
        assert result["effective_rate"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

