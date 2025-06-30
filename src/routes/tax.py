"""
Tax calculation routes for Flask application
"""
from flask import Blueprint, request, jsonify
from datetime import datetime

tax_bp = Blueprint('tax', __name__)

def calculate_malta_income_tax(annual_income, marital_status='single'):
    """Calculate Malta income tax based on 2024 rates"""
    
    # Malta 2024 tax brackets
    if marital_status in ['married', 'parental']:
        # Married/Parental rates
        brackets = [
            (12700, 0.0),      # First €12,700 - 0%
            (21200, 0.15),     # €12,701 to €21,200 - 15%
            (28700, 0.25),     # €21,201 to €28,700 - 25%
            (60000, 0.25),     # €28,701 to €60,000 - 25%
            (float('inf'), 0.35)  # Over €60,000 - 35%
        ]
    else:
        # Single rates
        brackets = [
            (9100, 0.0),       # First €9,100 - 0%
            (14500, 0.15),     # €9,101 to €14,500 - 15%
            (19500, 0.25),     # €14,501 to €19,500 - 25%
            (60000, 0.25),     # €19,501 to €60,000 - 25%
            (float('inf'), 0.35)  # Over €60,000 - 35%
        ]
    
    tax_due = 0
    remaining_income = annual_income
    breakdown = []
    
    for i, (bracket_limit, rate) in enumerate(brackets):
        if remaining_income <= 0:
            break
            
        if i == 0:
            taxable_in_bracket = min(remaining_income, bracket_limit)
            bracket_start = 0
        else:
            prev_limit = brackets[i-1][0]
            taxable_in_bracket = min(remaining_income, bracket_limit - prev_limit)
            bracket_start = prev_limit
        
        if taxable_in_bracket > 0:
            tax_in_bracket = taxable_in_bracket * rate
            tax_due += tax_in_bracket
            
            breakdown.append({
                'bracket': f"€{bracket_start:,.0f} - €{min(bracket_limit, annual_income):,.0f}",
                'rate': f"{rate*100:.0f}%",
                'taxable_amount': taxable_in_bracket,
                'tax_amount': tax_in_bracket
            })
            
        remaining_income -= taxable_in_bracket
    
    effective_rate = (tax_due / annual_income * 100) if annual_income > 0 else 0
    
    return {
        'annual_income': annual_income,
        'marital_status': marital_status,
        'tax_due': round(tax_due, 2),
        'effective_rate': round(effective_rate, 2),
        'breakdown': breakdown,
        'calculation_date': datetime.now().isoformat()
    }

@tax_bp.route('/calculate/income-tax', methods=['POST'])
def calculate_income_tax():
    """Calculate individual income tax"""
    try:
        data = request.get_json()
        annual_income = data.get('annual_income')
        marital_status = data.get('marital_status', 'single')
        
        if not annual_income or annual_income <= 0:
            return jsonify({'error': 'Valid annual income is required'}), 400
        
        result = calculate_malta_income_tax(annual_income, marital_status)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tax_bp.route('/calculate/corporate-tax', methods=['POST'])
def calculate_corporate_tax():
    """Calculate corporate income tax"""
    try:
        data = request.get_json()
        annual_profit = data.get('annual_profit')
        
        if not annual_profit or annual_profit <= 0:
            return jsonify({'error': 'Valid annual profit is required'}), 400
        
        # Malta corporate tax rate is 35%
        corporate_rate = 0.35
        tax_due = annual_profit * corporate_rate
        
        result = {
            'annual_profit': annual_profit,
            'tax_rate': f"{corporate_rate*100:.0f}%",
            'tax_due': round(tax_due, 2),
            'net_profit_after_tax': round(annual_profit - tax_due, 2),
            'calculation_date': datetime.now().isoformat()
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tax_bp.route('/calculate/vat', methods=['POST'])
def calculate_vat():
    """Calculate VAT"""
    try:
        data = request.get_json()
        amount = data.get('amount')
        vat_type = data.get('vat_type', 'standard')
        
        if not amount or amount <= 0:
            return jsonify({'error': 'Valid amount is required'}), 400
        
        # Malta VAT rates
        vat_rates = {
            'standard': 0.18,      # 18%
            'reduced_12': 0.12,    # 12%
            'reduced_7': 0.07,     # 7%
            'reduced_5': 0.05,     # 5%
            'zero': 0.0            # 0%
        }
        
        if vat_type not in vat_rates:
            return jsonify({'error': 'Invalid VAT type'}), 400
        
        vat_rate = vat_rates[vat_type]
        vat_amount = amount * vat_rate
        total_amount = amount + vat_amount
        
        result = {
            'net_amount': amount,
            'vat_type': vat_type,
            'vat_rate': f"{vat_rate*100:.0f}%",
            'vat_amount': round(vat_amount, 2),
            'total_amount': round(total_amount, 2),
            'calculation_date': datetime.now().isoformat()
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tax_bp.route('/calculate/social-security/employee', methods=['POST'])
def calculate_employee_social_security():
    """Calculate Class 1 (Employee) social security contributions"""
    try:
        data = request.get_json()
        weekly_wage = data.get('weekly_wage')
        birth_year = data.get('birth_year', 1990)
        
        if not weekly_wage or weekly_wage <= 0:
            return jsonify({'error': 'Valid weekly wage is required'}), 400
        
        # Calculate age
        current_year = datetime.now().year
        age = current_year - birth_year
        
        # Class 1 contribution rates (2024)
        if age < 18:
            employee_rate = 0.00
            employer_rate = 0.00
        elif age > 61:
            employee_rate = 0.00  # Reduced for pensioners
            employer_rate = 0.10
        else:
            employee_rate = 0.10  # 10%
            employer_rate = 0.10  # 10%
        
        annual_wage = weekly_wage * 52
        employee_contribution = annual_wage * employee_rate
        employer_contribution = annual_wage * employer_rate
        total_contribution = employee_contribution + employer_contribution
        
        result = {
            'weekly_wage': weekly_wage,
            'annual_wage': annual_wage,
            'age': age,
            'employee_rate': f"{employee_rate*100:.0f}%",
            'employer_rate': f"{employer_rate*100:.0f}%",
            'employee_contribution': round(employee_contribution, 2),
            'employer_contribution': round(employer_contribution, 2),
            'total_contribution': round(total_contribution, 2),
            'calculation_date': datetime.now().isoformat()
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tax_bp.route('/calculate/social-security/self-employed', methods=['POST'])
def calculate_self_employed_social_security():
    """Calculate Class 2 (Self-Employed) social security contributions"""
    try:
        data = request.get_json()
        annual_income = data.get('annual_income')
        birth_year = data.get('birth_year', 1990)
        
        if not annual_income or annual_income <= 0:
            return jsonify({'error': 'Valid annual income is required'}), 400
        
        # Calculate age
        current_year = datetime.now().year
        age = current_year - birth_year
        
        # Class 2 contribution rates (2024)
        if age < 18 or age > 65:
            contribution_rate = 0.00
        else:
            contribution_rate = 0.15  # 15%
        
        contribution = annual_income * contribution_rate
        
        result = {
            'annual_income': annual_income,
            'age': age,
            'contribution_rate': f"{contribution_rate*100:.0f}%",
            'contribution': round(contribution, 2),
            'calculation_date': datetime.now().isoformat()
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tax_bp.route('/calculate/stamp-duty', methods=['POST'])
def calculate_stamp_duty():
    """Calculate stamp duty on property transfers"""
    try:
        data = request.get_json()
        property_value = data.get('property_value')
        is_first_time_buyer = data.get('is_first_time_buyer', False)
        is_primary_residence = data.get('is_primary_residence', False)
        
        if not property_value or property_value <= 0:
            return jsonify({'error': 'Valid property value is required'}), 400
        
        # Malta stamp duty rates (2024)
        if is_first_time_buyer and is_primary_residence and property_value <= 175000:
            # First-time buyer exemption up to €175,000
            stamp_duty_rate = 0.0
        elif property_value <= 175000:
            stamp_duty_rate = 0.02  # 2%
        elif property_value <= 300000:
            stamp_duty_rate = 0.05  # 5%
        else:
            stamp_duty_rate = 0.08  # 8%
        
        stamp_duty = property_value * stamp_duty_rate
        
        result = {
            'property_value': property_value,
            'is_first_time_buyer': is_first_time_buyer,
            'is_primary_residence': is_primary_residence,
            'stamp_duty_rate': f"{stamp_duty_rate*100:.1f}%",
            'stamp_duty': round(stamp_duty, 2),
            'total_cost': round(property_value + stamp_duty, 2),
            'calculation_date': datetime.now().isoformat()
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tax_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Malta Tax Calculator API',
        'timestamp': datetime.now().isoformat()
    }) 