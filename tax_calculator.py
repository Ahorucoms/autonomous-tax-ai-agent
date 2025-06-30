"""
Malta Tax Calculator Service
Implements tax calculations based on Malta's tax system
"""

class MaltaTaxCalculator:
    def __init__(self):
        # 2025 Individual Income Tax Rates (Single)
        self.individual_tax_bands_single = [
            {"from": 0, "to": 15000, "rate": 0.0, "deduct": 0},
            {"from": 15001, "to": 23000, "rate": 0.15, "deduct": 2250},
            {"from": 23001, "to": 60000, "rate": 0.25, "deduct": 4550},
            {"from": 60001, "to": float('inf'), "rate": 0.35, "deduct": 10550}
        ]
        
        # 2025 Individual Income Tax Rates (Married)
        self.individual_tax_bands_married = [
            {"from": 0, "to": 12000, "rate": 0.0, "deduct": 0},
            {"from": 12001, "to": 16000, "rate": 0.15, "deduct": 1800},
            {"from": 16001, "to": 60000, "rate": 0.25, "deduct": 3400},
            {"from": 60001, "to": float('inf'), "rate": 0.35, "deduct": 9400}
        ]
        
        # 2025 Individual Income Tax Rates (Parental)
        self.individual_tax_bands_parental = [
            {"from": 0, "to": 13000, "rate": 0.0, "deduct": 0},
            {"from": 13001, "to": 17500, "rate": 0.15, "deduct": 1950},
            {"from": 17501, "to": 60000, "rate": 0.25, "deduct": 3700},
            {"from": 60001, "to": float('inf'), "rate": 0.35, "deduct": 9700}
        ]
        
        # Corporate tax rate
        self.corporate_tax_rate = 0.35
        
        # VAT rates
        self.vat_rates = {
            "standard": 0.18,
            "reduced_12": 0.12,
            "reduced_7": 0.07,
            "reduced_5": 0.05,
            "zero": 0.0
        }
        
        # Social Security Contribution rates (Class 1 - Employees)
        self.social_security_rates = {
            "employee_rate": 0.10,
            "employer_rate": 0.10,
            "self_employed_rate": 0.15
        }

    def calculate_individual_income_tax(self, annual_income, marital_status="single"):
        """
        Calculate individual income tax based on Malta's progressive tax system
        
        Args:
            annual_income (float): Annual chargeable income in EUR
            marital_status (str): "single", "married", or "parental"
            
        Returns:
            dict: Tax calculation details
        """
        if marital_status == "married":
            tax_bands = self.individual_tax_bands_married
        elif marital_status == "parental":
            tax_bands = self.individual_tax_bands_parental
        else:
            tax_bands = self.individual_tax_bands_single
        
        # Find applicable tax band
        applicable_band = None
        for band in tax_bands:
            if band["from"] <= annual_income <= band["to"]:
                applicable_band = band
                break
        
        if not applicable_band:
            # Income exceeds highest band
            applicable_band = tax_bands[-1]
        
        # Calculate tax
        if applicable_band["rate"] == 0:
            tax_due = 0
        else:
            tax_due = (annual_income * applicable_band["rate"]) - applicable_band["deduct"]
        
        tax_due = max(0, tax_due)  # Ensure tax is not negative
        
        effective_rate = (tax_due / annual_income * 100) if annual_income > 0 else 0
        
        return {
            "annual_income": annual_income,
            "marital_status": marital_status,
            "tax_due": round(tax_due, 2),
            "effective_rate": round(effective_rate, 2),
            "marginal_rate": round(applicable_band["rate"] * 100, 2),
            "net_income": round(annual_income - tax_due, 2)
        }

    def calculate_corporate_tax(self, annual_profit):
        """
        Calculate corporate income tax (flat rate of 35%)
        
        Args:
            annual_profit (float): Annual taxable profit in EUR
            
        Returns:
            dict: Corporate tax calculation details
        """
        tax_due = annual_profit * self.corporate_tax_rate
        
        return {
            "annual_profit": annual_profit,
            "tax_rate": self.corporate_tax_rate * 100,
            "tax_due": round(tax_due, 2),
            "net_profit": round(annual_profit - tax_due, 2)
        }

    def calculate_vat(self, amount, vat_type="standard"):
        """
        Calculate VAT based on Malta's VAT rates
        
        Args:
            amount (float): Net amount in EUR
            vat_type (str): Type of VAT rate to apply
            
        Returns:
            dict: VAT calculation details
        """
        vat_rate = self.vat_rates.get(vat_type, self.vat_rates["standard"])
        vat_amount = amount * vat_rate
        gross_amount = amount + vat_amount
        
        return {
            "net_amount": amount,
            "vat_rate": vat_rate * 100,
            "vat_amount": round(vat_amount, 2),
            "gross_amount": round(gross_amount, 2),
            "vat_type": vat_type
        }

    def calculate_social_security_employee(self, weekly_wage, birth_year=1990):
        """
        Calculate Class 1 Social Security Contributions for employees
        
        Args:
            weekly_wage (float): Basic weekly wage in EUR
            birth_year (int): Birth year to determine contribution limits
            
        Returns:
            dict: Social security calculation details
        """
        # Determine category based on wage and age
        if weekly_wage <= 221.78:
            if weekly_wage >= 0.10:
                category = "B" if birth_year <= 1979 else "B"  # 18 and over
                employee_contribution = 22.18
                employer_contribution = 22.18
            else:
                category = "A"  # Under minimum
                employee_contribution = 6.62
                employer_contribution = 6.62
        else:
            # Category C or D
            if birth_year <= 1961:
                # Born up to 31st December 1961
                if weekly_wage <= 451.91:
                    category = "C"
                    employee_contribution = weekly_wage * 0.10
                    employer_contribution = weekly_wage * 0.10
                else:
                    category = "D"
                    employee_contribution = 45.19
                    employer_contribution = 45.19
            else:
                # Born from 1st January 1962 onwards
                if weekly_wage <= 544.28:
                    category = "C"
                    employee_contribution = weekly_wage * 0.10
                    employer_contribution = weekly_wage * 0.10
                else:
                    category = "D"
                    employee_contribution = 54.43
                    employer_contribution = 54.43
        
        total_contribution = employee_contribution + employer_contribution
        annual_employee = employee_contribution * 52
        annual_employer = employer_contribution * 52
        annual_total = total_contribution * 52
        
        return {
            "weekly_wage": weekly_wage,
            "category": category,
            "employee_weekly": round(employee_contribution, 2),
            "employer_weekly": round(employer_contribution, 2),
            "total_weekly": round(total_contribution, 2),
            "employee_annual": round(annual_employee, 2),
            "employer_annual": round(annual_employer, 2),
            "total_annual": round(annual_total, 2)
        }

    def calculate_social_security_self_employed(self, annual_income, birth_year=1990):
        """
        Calculate Class 2 Social Security Contributions for self-employed
        
        Args:
            annual_income (float): Annual net income in EUR
            birth_year (int): Birth year to determine contribution limits
            
        Returns:
            dict: Social security calculation details
        """
        if annual_income <= 910:
            return {
                "annual_income": annual_income,
                "contribution_rate": 0,
                "annual_contribution": 0,
                "category": "Below threshold"
            }
        
        contribution_rate = 0.15  # 15% for self-employed
        
        # Determine maximum based on birth year
        if birth_year <= 1961:
            max_weekly = 45.19
            max_annual = max_weekly * 52  # €2,349.88
        else:
            max_weekly = 54.43
            max_annual = max_weekly * 52  # €2,830.36
        
        calculated_contribution = annual_income * contribution_rate
        actual_contribution = min(calculated_contribution, max_annual)
        
        return {
            "annual_income": annual_income,
            "contribution_rate": contribution_rate * 100,
            "calculated_contribution": round(calculated_contribution, 2),
            "max_contribution": round(max_annual, 2),
            "actual_contribution": round(actual_contribution, 2),
            "weekly_equivalent": round(actual_contribution / 52, 2)
        }

    def calculate_stamp_duty_property(self, property_value, is_first_time_buyer=False, is_primary_residence=False):
        """
        Calculate stamp duty on property transfers
        
        Args:
            property_value (float): Property transfer value in EUR
            is_first_time_buyer (bool): Whether buyer is first-time buyer
            is_primary_residence (bool): Whether property is primary residence
            
        Returns:
            dict: Stamp duty calculation details
        """
        standard_rate = 0.05  # 5% standard rate
        reduced_rate = 0.035  # 3.5% reduced rate for primary residence
        
        if is_first_time_buyer and property_value <= 200000:
            # No stamp duty on first EUR 200,000 for first-time buyers
            stamp_duty = 0
            if property_value > 200000:
                stamp_duty = (property_value - 200000) * standard_rate
        elif is_primary_residence and property_value <= 150000:
            # 3.5% on first EUR 150,000 for primary residence
            stamp_duty = property_value * reduced_rate
        elif is_primary_residence and property_value > 150000:
            # 3.5% on first EUR 150,000, then 5% on remainder
            stamp_duty = (150000 * reduced_rate) + ((property_value - 150000) * standard_rate)
        else:
            # Standard 5% rate
            stamp_duty = property_value * standard_rate
        
        return {
            "property_value": property_value,
            "stamp_duty": round(stamp_duty, 2),
            "effective_rate": round((stamp_duty / property_value * 100), 2) if property_value > 0 else 0,
            "is_first_time_buyer": is_first_time_buyer,
            "is_primary_residence": is_primary_residence
        }

