"""
Malta Tax System Integration API Routes
Handle electronic filing, payment processing, and status tracking
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from decimal import Decimal
import logging
from typing import Dict, Any

from ..services.malta_tax_integration import MaltaTaxIntegration, FilingStatus, PaymentStatus

malta_integration_bp = Blueprint('malta_integration', __name__)

# Initialize Malta tax integration service
malta_integration = MaltaTaxIntegration()

@malta_integration_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'malta_integration',
        'timestamp': datetime.utcnow().isoformat()
    })

@malta_integration_bp.route('/submit-filing', methods=['POST'])
def submit_filing():
    """Submit electronic filing to CFR"""
    try:
        data = request.get_json()
        
        required_fields = ['user_id', 'filing_type', 'tax_year']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        result = malta_integration.submit_electronic_filing(data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error submitting filing: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@malta_integration_bp.route('/process-payment', methods=['POST'])
def process_payment():
    """Process tax payment"""
    try:
        data = request.get_json()
        
        required_fields = ['filing_id', 'amount', 'payment_method']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate amount
        try:
            amount = Decimal(str(data['amount']))
            if amount <= 0:
                return jsonify({'error': 'Amount must be greater than zero'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid amount format'}), 400
        
        result = malta_integration.process_payment(data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error processing payment: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@malta_integration_bp.route('/filing-status/<filing_id>', methods=['GET'])
def get_filing_status(filing_id):
    """Get filing status"""
    try:
        result = malta_integration.track_filing_status(filing_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 404
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error getting filing status: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@malta_integration_bp.route('/refund-status/<refund_reference>', methods=['GET'])
def get_refund_status(refund_reference):
    """Get refund status"""
    try:
        result = malta_integration.track_refund_status(refund_reference)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 404
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error getting refund status: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@malta_integration_bp.route('/cfr-api-status', methods=['GET'])
def get_cfr_api_status():
    """Get CFR API system status"""
    try:
        result = malta_integration.get_cfr_api_status()
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error getting CFR API status: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@malta_integration_bp.route('/filing-types', methods=['GET'])
def get_filing_types():
    """Get supported filing types"""
    try:
        result = malta_integration.get_supported_filing_types()
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error getting filing types: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@malta_integration_bp.route('/payment-methods', methods=['GET'])
def get_payment_methods():
    """Get supported payment methods"""
    try:
        result = malta_integration.get_payment_methods()
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error getting payment methods: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@malta_integration_bp.route('/statistics', methods=['GET'])
def get_filing_statistics():
    """Get filing statistics"""
    try:
        user_id = request.args.get('user_id')
        result = malta_integration.get_filing_statistics(user_id)
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error getting filing statistics: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@malta_integration_bp.route('/user-filings/<user_id>', methods=['GET'])
def get_user_filings(user_id):
    """Get all filings for a user"""
    try:
        # Filter filings by user
        user_filings = [
            filing for filing in malta_integration.filing_records.values()
            if filing['user_id'] == user_id
        ]
        
        # Sort by submission date (newest first)
        user_filings = sorted(
            user_filings,
            key=lambda f: f['submitted_at'],
            reverse=True
        )
        
        return jsonify({
            'success': True,
            'filings': user_filings,
            'count': len(user_filings)
        })
        
    except Exception as e:
        logging.error(f"Error getting user filings: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@malta_integration_bp.route('/user-payments/<user_id>', methods=['GET'])
def get_user_payments(user_id):
    """Get all payments for a user"""
    try:
        # Filter payments by user
        user_payments = [
            payment for payment in malta_integration.payment_records.values()
            if payment['user_id'] == user_id
        ]
        
        # Sort by initiation date (newest first)
        user_payments = sorted(
            user_payments,
            key=lambda p: p['initiated_at'],
            reverse=True
        )
        
        return jsonify({
            'success': True,
            'payments': user_payments,
            'count': len(user_payments)
        })
        
    except Exception as e:
        logging.error(f"Error getting user payments: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@malta_integration_bp.route('/acknowledgments/<filing_id>', methods=['GET'])
def get_filing_acknowledgments(filing_id):
    """Get acknowledgments for a filing"""
    try:
        # Find acknowledgments for the filing
        filing_acknowledgments = [
            ack for ack in malta_integration.acknowledgments.values()
            if ack['filing_id'] == filing_id
        ]
        
        return jsonify({
            'success': True,
            'acknowledgments': filing_acknowledgments,
            'count': len(filing_acknowledgments)
        })
        
    except Exception as e:
        logging.error(f"Error getting acknowledgments: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@malta_integration_bp.route('/validate-filing', methods=['POST'])
def validate_filing_data():
    """Validate filing data before submission"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Filing data is required'}), 400
        
        validation_result = malta_integration._validate_filing_data(data)
        
        return jsonify({
            'success': True,
            'validation_result': validation_result
        })
        
    except Exception as e:
        logging.error(f"Error validating filing data: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@malta_integration_bp.route('/payment-fees', methods=['POST'])
def calculate_payment_fees():
    """Calculate payment processing fees"""
    try:
        data = request.get_json()
        
        required_fields = ['amount', 'payment_method']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        try:
            amount = Decimal(str(data['amount']))
            if amount <= 0:
                return jsonify({'error': 'Amount must be greater than zero'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid amount format'}), 400
        
        payment_method = data['payment_method']
        
        if payment_method not in malta_integration.payment_methods:
            return jsonify({'error': 'Unsupported payment method'}), 400
        
        method_info = malta_integration.payment_methods[payment_method]
        fee_percentage = method_info['fees']
        processing_fee = amount * Decimal(str(fee_percentage / 100)) if fee_percentage > 0 else Decimal('0')
        total_amount = amount + processing_fee
        
        return jsonify({
            'success': True,
            'fee_calculation': {
                'amount': float(amount),
                'fee_percentage': fee_percentage,
                'processing_fee': float(processing_fee),
                'total_amount': float(total_amount),
                'payment_method': payment_method,
                'processing_time': method_info['processing_time']
            }
        })
        
    except Exception as e:
        logging.error(f"Error calculating payment fees: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@malta_integration_bp.route('/filing-deadlines', methods=['GET'])
def get_filing_deadlines():
    """Get filing deadlines for all supported types"""
    try:
        deadlines = {}
        
        for filing_type, info in malta_integration.supported_filings.items():
            deadlines[filing_type] = {
                'form_code': info['form_code'],
                'description': info['description'],
                'deadline': info['deadline'],
                'electronic_filing': info['electronic_filing'],
                'payment_required': info['payment_required']
            }
        
        return jsonify({
            'success': True,
            'deadlines': deadlines
        })
        
    except Exception as e:
        logging.error(f"Error getting filing deadlines: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@malta_integration_bp.route('/system-status', methods=['GET'])
def get_system_status():
    """Get overall system status"""
    try:
        # Get CFR API status
        cfr_status = malta_integration.get_cfr_api_status()
        
        # Get system statistics
        stats = malta_integration.get_filing_statistics()
        
        system_status = {
            'overall_status': 'operational',
            'last_checked': datetime.utcnow().isoformat(),
            'cfr_api': cfr_status.get('api_status', {}),
            'system_statistics': stats.get('statistics', {}),
            'services': {
                'electronic_filing': 'operational',
                'payment_processing': 'operational',
                'status_tracking': 'operational',
                'document_processing': 'operational',
                'compliance_checking': 'operational'
            }
        }
        
        return jsonify({
            'success': True,
            'system_status': system_status
        })
        
    except Exception as e:
        logging.error(f"Error getting system status: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

