"""
Enhanced Tax Calculation API Routes
Comprehensive Malta tax calculations including:
- Income Tax
- Social Security Contributions
- VAT
- Stamp Duty
- Capital Gains Tax
- Comprehensive Tax Liability
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, date
from decimal import Decimal
import logging
from typing import Dict, Any

from ..services.tax_engine import (
    MaltaTaxEngine, 
    MaritalStatus, 
    ResidencyStatus,
    get_current_tax_rates,
    validate_tax_calculation_inputs
)

tax_calculations_bp = Blueprint('tax_calculations', __name__)

# Initialize tax engine
tax_engine = MaltaTaxEngine()

@tax_calculations_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'tax_calculations',
        'timestamp': datetime.utcnow().isoformat()
    })

@tax_calculations_bp.route('/rates', methods=['GET'])
def get_tax_rates():
    """Get current Malta tax rates"""
    try:
        tax_year = request.args.get('tax_year', 2025, type=int)
        rates = get_current_tax_rates(tax_year)
        
        return jsonify({
            'success': True,
            'rates': rates
        })
        
    except Exception as e:
        logging.error(f"Error getting tax rates: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@tax_calculations_bp.route('/income-tax', methods=['POST'])
def calculate_income_tax():
    """Calculate Malta income tax"""
    try:
        data = request.get_json()
        
        # Validate inputs
        errors = validate_tax_calculation_inputs(data)
        if errors:
            return jsonify({'error': 'Validation failed', 'details': errors}), 400
        
        # Extract parameters
        annual_income = Decimal(str(data['annual_income']))
        marital_status = MaritalStatus(data.get('marital_status', 'single'))
        residency_status = ResidencyStatus(data.get('residency_status', 'resident'))
        allowable_deductions = Decimal(str(data.get('allowable_deductions', 0)))
        tax_credits = Decimal(str(data.get('tax_credits', 0)))
        
        # Calculate income tax
        result = tax_engine.calculate_income_tax(
            annual_income=annual_income,
            marital_status=marital_status,
            residency_status=residency_status,
            allowable_deductions=allowable_deductions,
            tax_credits=tax_credits
        )
        
        return jsonify({
            'success': True,
            'calculation': result
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error calculating income tax: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@tax_calculations_bp.route('/social-security/class1', methods=['POST'])
def calculate_social_security_class1():
    """Calculate Class 1 Social Security Contributions (Employees)"""
    try:
        data = request.get_json()
        
        if 'weekly_wage' not in data:
            return jsonify({'error': 'Weekly wage is required'}), 400
        
        weekly_wage = Decimal(str(data['weekly_wage']))
        weeks_worked = data.get('weeks_worked', 52)
        
        if weekly_wage < 0:
            return jsonify({'error': 'Weekly wage must be positive'}), 400
        
        if not isinstance(weeks_worked, int) or weeks_worked < 1 or weeks_worked > 52:
            return jsonify({'error': 'Weeks worked must be between 1 and 52'}), 400
        
        # Calculate Class 1 contributions
        result = tax_engine.calculate_social_security_class1(
            weekly_wage=weekly_wage,
            weeks_worked=weeks_worked
        )
        
        return jsonify({
            'success': True,
            'calculation': result
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error calculating Class 1 social security: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@tax_calculations_bp.route('/social-security/class2', methods=['POST'])
def calculate_social_security_class2():
    """Calculate Class 2 Social Security Contributions (Self-Employed)"""
    try:
        data = request.get_json()
        
        if 'annual_income' not in data:
            return jsonify({'error': 'Annual income is required'}), 400
        
        annual_income = Decimal(str(data['annual_income']))
        
        if annual_income < 0:
            return jsonify({'error': 'Annual income must be positive'}), 400
        
        # Calculate Class 2 contributions
        result = tax_engine.calculate_social_security_class2(annual_income=annual_income)
        
        return jsonify({
            'success': True,
            'calculation': result
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error calculating Class 2 social security: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@tax_calculations_bp.route('/vat', methods=['POST'])
def calculate_vat():
    """Calculate VAT (Value Added Tax)"""
    try:
        data = request.get_json()
        
        if 'amount' not in data:
            return jsonify({'error': 'Amount is required'}), 400
        
        amount = Decimal(str(data['amount']))
        vat_rate_type = data.get('vat_rate_type', 'standard')
        include_vat = data.get('include_vat', False)
        
        if amount < 0:
            return jsonify({'error': 'Amount must be positive'}), 400
        
        # Calculate VAT
        result = tax_engine.calculate_vat(
            net_amount=amount,
            vat_rate_type=vat_rate_type,
            include_vat=include_vat
        )
        
        return jsonify({
            'success': True,
            'calculation': result
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error calculating VAT: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@tax_calculations_bp.route('/stamp-duty', methods=['POST'])
def calculate_stamp_duty():
    """Calculate stamp duty for property transactions"""
    try:
        data = request.get_json()
        
        if 'property_value' not in data:
            return jsonify({'error': 'Property value is required'}), 400
        
        property_value = Decimal(str(data['property_value']))
        is_first_time_buyer = data.get('is_first_time_buyer', False)
        
        if property_value <= 0:
            return jsonify({'error': 'Property value must be positive'}), 400
        
        # Calculate stamp duty
        result = tax_engine.calculate_stamp_duty(
            property_value=property_value,
            is_first_time_buyer=is_first_time_buyer
        )
        
        return jsonify({
            'success': True,
            'calculation': result
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error calculating stamp duty: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@tax_calculations_bp.route('/capital-gains', methods=['POST'])
def calculate_capital_gains():
    """Calculate capital gains tax"""
    try:
        data = request.get_json()
        
        required_fields = ['purchase_price', 'sale_price', 'purchase_date', 'sale_date']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        purchase_price = Decimal(str(data['purchase_price']))
        sale_price = Decimal(str(data['sale_price']))
        improvement_costs = Decimal(str(data.get('improvement_costs', 0)))
        selling_costs = Decimal(str(data.get('selling_costs', 0)))
        
        # Parse dates
        try:
            purchase_date = datetime.strptime(data['purchase_date'], '%Y-%m-%d').date()
            sale_date = datetime.strptime(data['sale_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        if purchase_price < 0 or sale_price < 0:
            return jsonify({'error': 'Prices must be positive'}), 400
        
        if sale_date <= purchase_date:
            return jsonify({'error': 'Sale date must be after purchase date'}), 400
        
        # Calculate capital gains tax
        result = tax_engine.calculate_capital_gains_tax(
            purchase_price=purchase_price,
            sale_price=sale_price,
            purchase_date=purchase_date,
            sale_date=sale_date,
            improvement_costs=improvement_costs,
            selling_costs=selling_costs
        )
        
        return jsonify({
            'success': True,
            'calculation': result
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error calculating capital gains: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@tax_calculations_bp.route('/comprehensive', methods=['POST'])
def calculate_comprehensive_tax():
    """Calculate comprehensive tax liability"""
    try:
        data = request.get_json()
        
        # Validate inputs
        errors = validate_tax_calculation_inputs(data)
        if errors:
            return jsonify({'error': 'Validation failed', 'details': errors}), 400
        
        # Extract parameters
        annual_income = Decimal(str(data['annual_income']))
        marital_status = MaritalStatus(data.get('marital_status', 'single'))
        employment_type = data.get('employment_type', 'employee')
        weekly_wage = Decimal(str(data['weekly_wage'])) if 'weekly_wage' in data else None
        allowable_deductions = Decimal(str(data.get('allowable_deductions', 0)))
        tax_credits = Decimal(str(data.get('tax_credits', 0)))
        
        # Calculate comprehensive tax liability
        result = tax_engine.calculate_comprehensive_tax_liability(
            annual_income=annual_income,
            marital_status=marital_status,
            employment_type=employment_type,
            weekly_wage=weekly_wage,
            allowable_deductions=allowable_deductions,
            tax_credits=tax_credits
        )
        
        return jsonify({
            'success': True,
            'calculation': result
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error calculating comprehensive tax: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@tax_calculations_bp.route('/estimate', methods=['POST'])
def estimate_tax_liability():
    """Estimate tax liability with minimal inputs"""
    try:
        data = request.get_json()
        
        if 'annual_income' not in data:
            return jsonify({'error': 'Annual income is required'}), 400
        
        annual_income = Decimal(str(data['annual_income']))
        marital_status = MaritalStatus(data.get('marital_status', 'single'))
        employment_type = data.get('employment_type', 'employee')
        
        if annual_income <= 0:
            return jsonify({'error': 'Annual income must be positive'}), 400
        
        # Calculate basic estimate
        result = tax_engine.calculate_comprehensive_tax_liability(
            annual_income=annual_income,
            marital_status=marital_status,
            employment_type=employment_type
        )
        
        # Simplify result for estimate
        estimate = {
            'annual_income': result['annual_income'],
            'estimated_income_tax': result['total_income_tax'],
            'estimated_social_security': result['total_social_security'],
            'estimated_total_tax': result['total_tax_liability'],
            'estimated_net_income': result['net_income'],
            'effective_tax_rate': result['overall_effective_rate'],
            'employment_type': employment_type,
            'marital_status': marital_status.value,
            'calculation_date': datetime.utcnow().isoformat(),
            'note': 'This is an estimate. Actual tax may vary based on deductions, credits, and other factors.'
        }
        
        return jsonify({
            'success': True,
            'estimate': estimate
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error estimating tax liability: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@tax_calculations_bp.route('/vat-rates', methods=['GET'])
def get_vat_rates():
    """Get available VAT rates"""
    try:
        vat_rates = {
            'standard': {'rate': 18, 'description': 'Standard rate for most goods and services'},
            'reduced_1': {'rate': 12, 'description': 'Reduced rate for certain goods'},
            'reduced_2': {'rate': 7, 'description': 'Reduced rate for accommodation and restaurants'},
            'reduced_3': {'rate': 5, 'description': 'Reduced rate for specific items'},
            'zero': {'rate': 0, 'description': 'Zero rate for exports and certain supplies'}
        }
        
        return jsonify({
            'success': True,
            'vat_rates': vat_rates
        })
        
    except Exception as e:
        logging.error(f"Error getting VAT rates: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@tax_calculations_bp.route('/tax-brackets', methods=['GET'])
def get_tax_brackets():
    """Get income tax brackets"""
    try:
        tax_year = request.args.get('tax_year', 2025, type=int)
        marital_status = request.args.get('marital_status', 'single')
        
        if marital_status not in ['single', 'married']:
            return jsonify({'error': 'Invalid marital status'}), 400
        
        engine = MaltaTaxEngine(tax_year)
        brackets = engine.income_tax_rates[tax_year][marital_status]
        
        formatted_brackets = []
        for i, (lower, upper, rate) in enumerate(brackets):
            formatted_brackets.append({
                'bracket': i + 1,
                'lower_limit': float(lower),
                'upper_limit': float(upper) if upper else None,
                'rate': float(rate * 100)
            })
        
        return jsonify({
            'success': True,
            'tax_year': tax_year,
            'marital_status': marital_status,
            'tax_brackets': formatted_brackets
        })
        
    except Exception as e:
        logging.error(f"Error getting tax brackets: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

