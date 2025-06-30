"""
Malta Tax Calculation Engine
Comprehensive tax calculations for Malta tax system including:
- Income Tax (Progressive rates)
- Social Security Contributions (Class 1 & 2)
- VAT (Multiple rates)
- Stamp Duty
- Capital Gains Tax
- Withholding Tax
"""

from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, date
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
import logging

class TaxYear(Enum):
    YEAR_2024 = 2024
    YEAR_2025 = 2025

class MaritalStatus(Enum):
    SINGLE = "single"
    MARRIED = "married"
    WIDOWED = "widowed"
    SEPARATED = "separated"

class ResidencyStatus(Enum):
    RESIDENT = "resident"
    NON_RESIDENT = "non_resident"
    ORDINARILY_RESIDENT = "ordinarily_resident"

class VATRate(Enum):
    STANDARD = Decimal('0.18')  # 18%
    REDUCED_1 = Decimal('0.12')  # 12%
    REDUCED_2 = Decimal('0.07')  # 7%
    REDUCED_3 = Decimal('0.05')  # 5%
    ZERO = Decimal('0.00')      # 0%

class MaltaTaxEngine:
    """Comprehensive Malta tax calculation engine"""
    
    def __init__(self, tax_year: int = 2025):
        self.tax_year = tax_year
        self.logger = logging.getLogger(__name__)
        
        # Tax rates and thresholds for 2025
        self.income_tax_rates = {
            2025: {
                'single': [
                    (Decimal('0'), Decimal('9100'), Decimal('0.00')),      # 0% up to €9,100
                    (Decimal('9100'), Decimal('14500'), Decimal('0.15')),   # 15% from €9,100 to €14,500
                    (Decimal('14500'), Decimal('19500'), Decimal('0.25')),  # 25% from €14,500 to €19,500
                    (Decimal('19500'), Decimal('60000'), Decimal('0.25')),  # 25% from €19,500 to €60,000
                    (Decimal('60000'), None, Decimal('0.35'))               # 35% above €60,000
                ],
                'married': [
                    (Decimal('0'), Decimal('12700'), Decimal('0.00')),      # 0% up to €12,700
                    (Decimal('12700'), Decimal('21200'), Decimal('0.15')),  # 15% from €12,700 to €21,200
                    (Decimal('21200'), Decimal('28700'), Decimal('0.25')),  # 25% from €21,200 to €28,700
                    (Decimal('28700'), Decimal('60000'), Decimal('0.25')),  # 25% from €28,700 to €60,000
                    (Decimal('60000'), None, Decimal('0.35'))               # 35% above €60,000
                ]
            }
        }
        
        # Social Security Contribution rates for 2025
        self.social_security_rates = {
            2025: {
                'class_1': {
                    'employee_rate': Decimal('0.10'),     # 10%
                    'employer_rate': Decimal('0.10'),     # 10%
                    'weekly_minimum': Decimal('24.31'),   # Minimum weekly wage
                    'weekly_maximum': Decimal('894.23'),  # Maximum weekly wage
                    'annual_minimum': Decimal('1264.12'), # Annual minimum
                    'annual_maximum': Decimal('46499.96') # Annual maximum
                },
                'class_2': {
                    'rate': Decimal('0.15'),              # 15%
                    'minimum_annual': Decimal('3600'),    # Minimum annual income
                    'maximum_annual': Decimal('46499.96') # Maximum annual income
                }
            }
        }
        
        # VAT rates
        self.vat_rates = {
            'standard': VATRate.STANDARD.value,
            'reduced_1': VATRate.REDUCED_1.value,
            'reduced_2': VATRate.REDUCED_2.value,
            'reduced_3': VATRate.REDUCED_3.value,
            'zero': VATRate.ZERO.value
        }
        
        # Stamp duty rates for property transactions
        self.stamp_duty_rates = {
            2025: {
                'first_time_buyer': [
                    (Decimal('0'), Decimal('175000'), Decimal('0.00')),     # 0% up to €175,000
                    (Decimal('175000'), Decimal('300000'), Decimal('0.02')), # 2% from €175,000 to €300,000
                    (Decimal('300000'), None, Decimal('0.05'))              # 5% above €300,000
                ],
                'regular_buyer': [
                    (Decimal('0'), Decimal('150000'), Decimal('0.02')),     # 2% up to €150,000
                    (Decimal('150000'), Decimal('300000'), Decimal('0.05')), # 5% from €150,000 to €300,000
                    (Decimal('300000'), None, Decimal('0.08'))              # 8% above €300,000
                ]
            }
        }
    
    def calculate_income_tax(self, 
                           annual_income: Decimal, 
                           marital_status: MaritalStatus = MaritalStatus.SINGLE,
                           residency_status: ResidencyStatus = ResidencyStatus.RESIDENT,
                           allowable_deductions: Decimal = Decimal('0'),
                           tax_credits: Decimal = Decimal('0')) -> Dict[str, Any]:
        """
        Calculate Malta income tax
        
        Args:
            annual_income: Gross annual income in EUR
            marital_status: Marital status for tax calculation
            residency_status: Tax residency status
            allowable_deductions: Total allowable deductions
            tax_credits: Available tax credits
            
        Returns:
            Dictionary with detailed tax calculation breakdown
        """
        try:
            # Convert to Decimal for precision
            annual_income = Decimal(str(annual_income))
            allowable_deductions = Decimal(str(allowable_deductions))
            tax_credits = Decimal(str(tax_credits))
            
            # Calculate taxable income
            taxable_income = annual_income - allowable_deductions
            if taxable_income < 0:
                taxable_income = Decimal('0')
            
            # Get tax brackets for marital status
            status_key = 'married' if marital_status == MaritalStatus.MARRIED else 'single'
            tax_brackets = self.income_tax_rates[self.tax_year][status_key]
            
            # Calculate tax using progressive rates
            total_tax = Decimal('0')
            tax_breakdown = []
            
            for i, (lower_limit, upper_limit, rate) in enumerate(tax_brackets):
                if taxable_income <= lower_limit:
                    break
                
                # Calculate taxable amount in this bracket
                if upper_limit is None:
                    taxable_in_bracket = taxable_income - lower_limit
                else:
                    taxable_in_bracket = min(taxable_income, upper_limit) - lower_limit
                
                if taxable_in_bracket <= 0:
                    continue
                
                # Calculate tax for this bracket
                tax_in_bracket = taxable_in_bracket * rate
                total_tax += tax_in_bracket
                
                tax_breakdown.append({
                    'bracket': i + 1,
                    'lower_limit': float(lower_limit),
                    'upper_limit': float(upper_limit) if upper_limit else None,
                    'rate': float(rate * 100),  # Convert to percentage
                    'taxable_amount': float(taxable_in_bracket),
                    'tax_amount': float(tax_in_bracket)
                })
            
            # Apply tax credits
            tax_after_credits = max(total_tax - tax_credits, Decimal('0'))
            
            # Calculate effective and marginal tax rates
            effective_rate = (tax_after_credits / annual_income * 100) if annual_income > 0 else Decimal('0')
            
            # Find marginal rate (rate of the highest bracket used)
            marginal_rate = Decimal('0')
            for lower_limit, upper_limit, rate in reversed(tax_brackets):
                if taxable_income > lower_limit:
                    marginal_rate = rate * 100
                    break
            
            return {
                'annual_income': float(annual_income),
                'allowable_deductions': float(allowable_deductions),
                'taxable_income': float(taxable_income),
                'gross_tax': float(total_tax),
                'tax_credits': float(tax_credits),
                'net_tax': float(tax_after_credits),
                'effective_rate': float(effective_rate.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'marginal_rate': float(marginal_rate),
                'marital_status': marital_status.value,
                'residency_status': residency_status.value,
                'tax_year': self.tax_year,
                'tax_breakdown': tax_breakdown,
                'calculation_date': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating income tax: {str(e)}")
            raise ValueError(f"Income tax calculation failed: {str(e)}")
    
    def calculate_social_security_class1(self, 
                                       weekly_wage: Decimal,
                                       weeks_worked: int = 52) -> Dict[str, Any]:
        """
        Calculate Class 1 Social Security Contributions (Employees)
        
        Args:
            weekly_wage: Weekly wage in EUR
            weeks_worked: Number of weeks worked in the year
            
        Returns:
            Dictionary with social security calculation breakdown
        """
        try:
            weekly_wage = Decimal(str(weekly_wage))
            rates = self.social_security_rates[self.tax_year]['class_1']
            
            # Apply weekly limits
            contributory_wage = max(
                min(weekly_wage, rates['weekly_maximum']),
                rates['weekly_minimum']
            )
            
            # Calculate contributions
            employee_contribution = contributory_wage * rates['employee_rate']
            employer_contribution = contributory_wage * rates['employer_rate']
            
            # Annual calculations
            annual_contributory_wage = contributory_wage * weeks_worked
            annual_employee_contribution = employee_contribution * weeks_worked
            annual_employer_contribution = employer_contribution * weeks_worked
            
            return {
                'weekly_wage': float(weekly_wage),
                'contributory_wage': float(contributory_wage),
                'weeks_worked': weeks_worked,
                'employee_rate': float(rates['employee_rate'] * 100),
                'employer_rate': float(rates['employer_rate'] * 100),
                'weekly_employee_contribution': float(employee_contribution),
                'weekly_employer_contribution': float(employer_contribution),
                'annual_contributory_wage': float(annual_contributory_wage),
                'annual_employee_contribution': float(annual_employee_contribution),
                'annual_employer_contribution': float(annual_employer_contribution),
                'total_annual_contribution': float(annual_employee_contribution + annual_employer_contribution),
                'weekly_minimum': float(rates['weekly_minimum']),
                'weekly_maximum': float(rates['weekly_maximum']),
                'tax_year': self.tax_year,
                'calculation_date': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating Class 1 social security: {str(e)}")
            raise ValueError(f"Class 1 social security calculation failed: {str(e)}")
    
    def calculate_social_security_class2(self, annual_income: Decimal) -> Dict[str, Any]:
        """
        Calculate Class 2 Social Security Contributions (Self-Employed)
        
        Args:
            annual_income: Annual income in EUR
            
        Returns:
            Dictionary with social security calculation breakdown
        """
        try:
            annual_income = Decimal(str(annual_income))
            rates = self.social_security_rates[self.tax_year]['class_2']
            
            # Apply annual limits
            contributory_income = max(
                min(annual_income, rates['maximum_annual']),
                rates['minimum_annual']
            )
            
            # Calculate contribution
            annual_contribution = contributory_income * rates['rate']
            
            return {
                'annual_income': float(annual_income),
                'contributory_income': float(contributory_income),
                'contribution_rate': float(rates['rate'] * 100),
                'annual_contribution': float(annual_contribution),
                'minimum_annual': float(rates['minimum_annual']),
                'maximum_annual': float(rates['maximum_annual']),
                'tax_year': self.tax_year,
                'calculation_date': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating Class 2 social security: {str(e)}")
            raise ValueError(f"Class 2 social security calculation failed: {str(e)}")
    
    def calculate_vat(self, 
                     net_amount: Decimal, 
                     vat_rate_type: str = 'standard',
                     include_vat: bool = False) -> Dict[str, Any]:
        """
        Calculate VAT (Value Added Tax)
        
        Args:
            net_amount: Net amount (excluding VAT) or gross amount (including VAT)
            vat_rate_type: Type of VAT rate to apply
            include_vat: Whether the amount includes VAT (True) or excludes VAT (False)
            
        Returns:
            Dictionary with VAT calculation breakdown
        """
        try:
            net_amount = Decimal(str(net_amount))
            
            if vat_rate_type not in self.vat_rates:
                raise ValueError(f"Invalid VAT rate type: {vat_rate_type}")
            
            vat_rate = self.vat_rates[vat_rate_type]
            
            if include_vat:
                # Amount includes VAT - calculate net amount and VAT
                gross_amount = net_amount
                net_amount = gross_amount / (1 + vat_rate)
                vat_amount = gross_amount - net_amount
            else:
                # Amount excludes VAT - calculate VAT and gross amount
                vat_amount = net_amount * vat_rate
                gross_amount = net_amount + vat_amount
            
            return {
                'net_amount': float(net_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'vat_rate_type': vat_rate_type,
                'vat_rate': float(vat_rate * 100),
                'vat_amount': float(vat_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'gross_amount': float(gross_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'includes_vat': include_vat,
                'calculation_date': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating VAT: {str(e)}")
            raise ValueError(f"VAT calculation failed: {str(e)}")
    
    def calculate_stamp_duty(self, 
                           property_value: Decimal,
                           is_first_time_buyer: bool = False) -> Dict[str, Any]:
        """
        Calculate stamp duty for property transactions
        
        Args:
            property_value: Value of the property in EUR
            is_first_time_buyer: Whether the buyer is a first-time buyer
            
        Returns:
            Dictionary with stamp duty calculation breakdown
        """
        try:
            property_value = Decimal(str(property_value))
            
            # Select appropriate rate structure
            buyer_type = 'first_time_buyer' if is_first_time_buyer else 'regular_buyer'
            rate_structure = self.stamp_duty_rates[self.tax_year][buyer_type]
            
            total_duty = Decimal('0')
            duty_breakdown = []
            
            for i, (lower_limit, upper_limit, rate) in enumerate(rate_structure):
                if property_value <= lower_limit:
                    break
                
                # Calculate taxable amount in this bracket
                if upper_limit is None:
                    taxable_in_bracket = property_value - lower_limit
                else:
                    taxable_in_bracket = min(property_value, upper_limit) - lower_limit
                
                if taxable_in_bracket <= 0:
                    continue
                
                # Calculate duty for this bracket
                duty_in_bracket = taxable_in_bracket * rate
                total_duty += duty_in_bracket
                
                duty_breakdown.append({
                    'bracket': i + 1,
                    'lower_limit': float(lower_limit),
                    'upper_limit': float(upper_limit) if upper_limit else None,
                    'rate': float(rate * 100),
                    'taxable_amount': float(taxable_in_bracket),
                    'duty_amount': float(duty_in_bracket)
                })
            
            # Calculate effective rate
            effective_rate = (total_duty / property_value * 100) if property_value > 0 else Decimal('0')
            
            return {
                'property_value': float(property_value),
                'is_first_time_buyer': is_first_time_buyer,
                'buyer_type': buyer_type,
                'total_stamp_duty': float(total_duty.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'effective_rate': float(effective_rate.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'duty_breakdown': duty_breakdown,
                'tax_year': self.tax_year,
                'calculation_date': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating stamp duty: {str(e)}")
            raise ValueError(f"Stamp duty calculation failed: {str(e)}")
    
    def calculate_capital_gains_tax(self, 
                                  purchase_price: Decimal,
                                  sale_price: Decimal,
                                  purchase_date: date,
                                  sale_date: date,
                                  improvement_costs: Decimal = Decimal('0'),
                                  selling_costs: Decimal = Decimal('0')) -> Dict[str, Any]:
        """
        Calculate capital gains tax on asset disposal
        
        Args:
            purchase_price: Original purchase price
            sale_price: Sale price
            purchase_date: Date of purchase
            sale_date: Date of sale
            improvement_costs: Costs of improvements made to the asset
            selling_costs: Costs associated with the sale
            
        Returns:
            Dictionary with capital gains tax calculation
        """
        try:
            purchase_price = Decimal(str(purchase_price))
            sale_price = Decimal(str(sale_price))
            improvement_costs = Decimal(str(improvement_costs))
            selling_costs = Decimal(str(selling_costs))
            
            # Calculate holding period
            holding_period = (sale_date - purchase_date).days
            holding_years = holding_period / 365.25
            
            # Calculate adjusted cost base
            adjusted_cost_base = purchase_price + improvement_costs + selling_costs
            
            # Calculate capital gain/loss
            capital_gain = sale_price - adjusted_cost_base
            
            # Determine tax rate based on holding period
            # Malta: No capital gains tax on assets held for more than 3 years (for residents)
            if holding_years >= 3:
                tax_rate = Decimal('0.00')  # 0% for long-term holdings
                exemption_reason = "Long-term holding (>3 years)"
            else:
                tax_rate = Decimal('0.35')  # 35% for short-term holdings
                exemption_reason = None
            
            # Calculate tax
            if capital_gain > 0:
                capital_gains_tax = capital_gain * tax_rate
            else:
                capital_gains_tax = Decimal('0')  # No tax on losses
            
            return {
                'purchase_price': float(purchase_price),
                'sale_price': float(sale_price),
                'improvement_costs': float(improvement_costs),
                'selling_costs': float(selling_costs),
                'adjusted_cost_base': float(adjusted_cost_base),
                'capital_gain': float(capital_gain),
                'holding_period_days': holding_period,
                'holding_period_years': round(holding_years, 2),
                'tax_rate': float(tax_rate * 100),
                'capital_gains_tax': float(capital_gains_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'exemption_reason': exemption_reason,
                'purchase_date': purchase_date.isoformat(),
                'sale_date': sale_date.isoformat(),
                'calculation_date': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating capital gains tax: {str(e)}")
            raise ValueError(f"Capital gains tax calculation failed: {str(e)}")
    
    def calculate_comprehensive_tax_liability(self,
                                            annual_income: Decimal,
                                            marital_status: MaritalStatus = MaritalStatus.SINGLE,
                                            employment_type: str = 'employee',  # 'employee' or 'self_employed'
                                            weekly_wage: Optional[Decimal] = None,
                                            allowable_deductions: Decimal = Decimal('0'),
                                            tax_credits: Decimal = Decimal('0')) -> Dict[str, Any]:
        """
        Calculate comprehensive tax liability including income tax and social security
        
        Args:
            annual_income: Annual income in EUR
            marital_status: Marital status
            employment_type: Type of employment (employee or self_employed)
            weekly_wage: Weekly wage (for employees)
            allowable_deductions: Total allowable deductions
            tax_credits: Available tax credits
            
        Returns:
            Dictionary with comprehensive tax calculation
        """
        try:
            # Calculate income tax
            income_tax_result = self.calculate_income_tax(
                annual_income=annual_income,
                marital_status=marital_status,
                allowable_deductions=allowable_deductions,
                tax_credits=tax_credits
            )
            
            # Calculate social security contributions
            if employment_type == 'employee':
                if weekly_wage is None:
                    weekly_wage = annual_income / 52
                social_security_result = self.calculate_social_security_class1(weekly_wage)
                social_security_contribution = social_security_result['annual_employee_contribution']
            else:  # self_employed
                social_security_result = self.calculate_social_security_class2(annual_income)
                social_security_contribution = social_security_result['annual_contribution']
            
            # Calculate total tax liability
            total_tax_liability = income_tax_result['net_tax'] + social_security_contribution
            
            # Calculate net income after all taxes
            net_income = float(annual_income) - total_tax_liability
            
            # Calculate overall effective tax rate
            overall_effective_rate = (total_tax_liability / float(annual_income) * 100) if annual_income > 0 else 0
            
            return {
                'annual_income': float(annual_income),
                'employment_type': employment_type,
                'income_tax': income_tax_result,
                'social_security': social_security_result,
                'total_income_tax': income_tax_result['net_tax'],
                'total_social_security': social_security_contribution,
                'total_tax_liability': total_tax_liability,
                'net_income': net_income,
                'overall_effective_rate': round(overall_effective_rate, 2),
                'tax_year': self.tax_year,
                'calculation_date': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating comprehensive tax liability: {str(e)}")
            raise ValueError(f"Comprehensive tax calculation failed: {str(e)}")

# Utility functions for common tax calculations
def get_current_tax_rates(tax_year: int = 2025) -> Dict[str, Any]:
    """Get current tax rates for Malta"""
    engine = MaltaTaxEngine(tax_year)
    return {
        'tax_year': tax_year,
        'income_tax_rates': engine.income_tax_rates[tax_year],
        'social_security_rates': engine.social_security_rates[tax_year],
        'vat_rates': engine.vat_rates,
        'stamp_duty_rates': engine.stamp_duty_rates[tax_year]
    }

def validate_tax_calculation_inputs(data: Dict[str, Any]) -> List[str]:
    """Validate inputs for tax calculations"""
    errors = []
    
    # Check required fields
    if 'annual_income' not in data:
        errors.append("Annual income is required")
    elif not isinstance(data['annual_income'], (int, float, Decimal)) or data['annual_income'] < 0:
        errors.append("Annual income must be a positive number")
    
    # Validate marital status
    if 'marital_status' in data:
        valid_statuses = [status.value for status in MaritalStatus]
        if data['marital_status'] not in valid_statuses:
            errors.append(f"Invalid marital status. Must be one of: {valid_statuses}")
    
    # Validate employment type
    if 'employment_type' in data:
        if data['employment_type'] not in ['employee', 'self_employed']:
            errors.append("Employment type must be 'employee' or 'self_employed'")
    
    return errors

