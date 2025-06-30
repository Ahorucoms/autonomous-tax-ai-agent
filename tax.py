"""
Tax calculation API routes for Malta Tax Agent
"""

from flask import Blueprint, request, jsonify
from flask_cors import CORS
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.services.tax_calculator import MaltaTaxCalculator

tax_bp = Blueprint('tax', __name__)
CORS(tax_bp)  # Enable CORS for all routes in this blueprint

calculator = MaltaTaxCalculator()

@tax_bp.route('/calculate/income-tax', methods=['POST'])
def calculate_income_tax():
    """Calculate individual income tax"""
    try:
        data = request.get_json()
        annual_income = float(data.get('annual_income', 0))
        marital_status = data.get('marital_status', 'single')
        
        if annual_income < 0:
            return jsonify({"error": "Annual income cannot be negative"}), 400
        
        result = calculator.calculate_individual_income_tax(annual_income, marital_status)
        return jsonify(result)
    
    except (ValueError, TypeError) as e:
        return jsonify({"error": "Invalid input data"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tax_bp.route('/calculate/corporate-tax', methods=['POST'])
def calculate_corporate_tax():
    """Calculate corporate income tax"""
    try:
        data = request.get_json()
        annual_profit = float(data.get('annual_profit', 0))
        
        if annual_profit < 0:
            return jsonify({"error": "Annual profit cannot be negative"}), 400
        
        result = calculator.calculate_corporate_tax(annual_profit)
        return jsonify(result)
    
    except (ValueError, TypeError) as e:
        return jsonify({"error": "Invalid input data"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tax_bp.route('/calculate/vat', methods=['POST'])
def calculate_vat():
    """Calculate VAT"""
    try:
        data = request.get_json()
        amount = float(data.get('amount', 0))
        vat_type = data.get('vat_type', 'standard')
        
        if amount < 0:
            return jsonify({"error": "Amount cannot be negative"}), 400
        
        valid_vat_types = ['standard', 'reduced_12', 'reduced_7', 'reduced_5', 'zero']
        if vat_type not in valid_vat_types:
            return jsonify({"error": f"Invalid VAT type. Must be one of: {valid_vat_types}"}), 400
        
        result = calculator.calculate_vat(amount, vat_type)
        return jsonify(result)
    
    except (ValueError, TypeError) as e:
        return jsonify({"error": "Invalid input data"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tax_bp.route('/calculate/social-security/employee', methods=['POST'])
def calculate_social_security_employee():
    """Calculate Class 1 Social Security Contributions for employees"""
    try:
        data = request.get_json()
        weekly_wage = float(data.get('weekly_wage', 0))
        birth_year = int(data.get('birth_year', 1990))
        
        if weekly_wage < 0:
            return jsonify({"error": "Weekly wage cannot be negative"}), 400
        
        if birth_year < 1900 or birth_year > 2024:
            return jsonify({"error": "Invalid birth year"}), 400
        
        result = calculator.calculate_social_security_employee(weekly_wage, birth_year)
        return jsonify(result)
    
    except (ValueError, TypeError) as e:
        return jsonify({"error": "Invalid input data"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tax_bp.route('/calculate/social-security/self-employed', methods=['POST'])
def calculate_social_security_self_employed():
    """Calculate Class 2 Social Security Contributions for self-employed"""
    try:
        data = request.get_json()
        annual_income = float(data.get('annual_income', 0))
        birth_year = int(data.get('birth_year', 1990))
        
        if annual_income < 0:
            return jsonify({"error": "Annual income cannot be negative"}), 400
        
        if birth_year < 1900 or birth_year > 2024:
            return jsonify({"error": "Invalid birth year"}), 400
        
        result = calculator.calculate_social_security_self_employed(annual_income, birth_year)
        return jsonify(result)
    
    except (ValueError, TypeError) as e:
        return jsonify({"error": "Invalid input data"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tax_bp.route('/calculate/stamp-duty', methods=['POST'])
def calculate_stamp_duty():
    """Calculate stamp duty on property transfers"""
    try:
        data = request.get_json()
        property_value = float(data.get('property_value', 0))
        is_first_time_buyer = bool(data.get('is_first_time_buyer', False))
        is_primary_residence = bool(data.get('is_primary_residence', False))
        
        if property_value < 0:
            return jsonify({"error": "Property value cannot be negative"}), 400
        
        result = calculator.calculate_stamp_duty_property(property_value, is_first_time_buyer, is_primary_residence)
        return jsonify(result)
    
    except (ValueError, TypeError) as e:
        return jsonify({"error": "Invalid input data"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tax_bp.route('/tax-info/rates', methods=['GET'])
def get_tax_rates():
    """Get current tax rates and information"""
    try:
        tax_info = {
            "individual_tax_rates": {
                "single": calculator.individual_tax_bands_single,
                "married": calculator.individual_tax_bands_married,
                "parental": calculator.individual_tax_bands_parental
            },
            "corporate_tax_rate": calculator.corporate_tax_rate * 100,
            "vat_rates": {k: v * 100 for k, v in calculator.vat_rates.items()},
            "social_security_rates": {k: v * 100 for k, v in calculator.social_security_rates.items()},
            "stamp_duty_rates": {
                "standard": 5.0,
                "reduced_primary_residence": 3.5,
                "first_time_buyer_exemption": "First EUR 200,000 exempt"
            }
        }
        return jsonify(tax_info)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tax_bp.route('/tax-info/deadlines', methods=['GET'])
def get_tax_deadlines():
    """Get important tax deadlines"""
    try:
        deadlines = {
            "individual_income_tax": {
                "return_deadline": "30 June (31 July for electronic submissions)",
                "provisional_tax_payments": ["30 April", "31 August", "21 December"]
            },
            "corporate_income_tax": {
                "return_deadline": "31 March (for companies with financial year ending Jan-Jun)",
                "provisional_tax_payments": ["30 April", "31 August", "21 December"]
            },
            "vat": {
                "invoicing_deadline": "15th day of month following chargeable event",
                "return_frequency": "Monthly or quarterly depending on turnover"
            },
            "social_security": {
                "self_employed_payments": ["30 April", "31 August", "21 December"]
            }
        }
        return jsonify(deadlines)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tax_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "Malta Tax Agent API"})

