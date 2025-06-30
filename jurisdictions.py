"""
Jurisdictions API Routes
Handles jurisdiction management and cloning
"""

from flask import Blueprint, request, jsonify
import logging

logger = logging.getLogger(__name__)

jurisdictions_bp = Blueprint('jurisdictions', __name__)

@jurisdictions_bp.route('/list', methods=['GET'])
def get_jurisdictions():
    """Get list of supported jurisdictions"""
    try:
        jurisdictions = [
            {
                'code': 'MT',
                'name': 'Malta',
                'languages': ['en', 'mt'],
                'currency': 'EUR',
                'tax_year': 'calendar',
                'features': ['income_tax', 'vat', 'corporate_tax', 'property_tax']
            },
            {
                'code': 'FR',
                'name': 'France',
                'languages': ['fr', 'en'],
                'currency': 'EUR',
                'tax_year': 'calendar',
                'features': ['income_tax', 'vat', 'corporate_tax', 'social_contributions']
            },
            {
                'code': 'DE',
                'name': 'Germany',
                'languages': ['de', 'en'],
                'currency': 'EUR',
                'tax_year': 'calendar',
                'features': ['income_tax', 'vat', 'corporate_tax', 'trade_tax']
            },
            {
                'code': 'IT',
                'name': 'Italy',
                'languages': ['it', 'en'],
                'currency': 'EUR',
                'tax_year': 'calendar',
                'features': ['income_tax', 'vat', 'corporate_tax']
            },
            {
                'code': 'ES',
                'name': 'Spain',
                'languages': ['es', 'en'],
                'currency': 'EUR',
                'tax_year': 'calendar',
                'features': ['income_tax', 'vat', 'corporate_tax']
            },
            {
                'code': 'NL',
                'name': 'Netherlands',
                'languages': ['nl', 'en'],
                'currency': 'EUR',
                'tax_year': 'calendar',
                'features': ['income_tax', 'vat', 'corporate_tax']
            },
            {
                'code': 'BE',
                'name': 'Belgium',
                'languages': ['fr', 'nl', 'de', 'en'],
                'currency': 'EUR',
                'tax_year': 'calendar',
                'features': ['income_tax', 'vat', 'corporate_tax']
            },
            {
                'code': 'LU',
                'name': 'Luxembourg',
                'languages': ['fr', 'de', 'en'],
                'currency': 'EUR',
                'tax_year': 'calendar',
                'features': ['income_tax', 'vat', 'corporate_tax']
            },
            {
                'code': 'IE',
                'name': 'Ireland',
                'languages': ['en', 'ga'],
                'currency': 'EUR',
                'tax_year': 'calendar',
                'features': ['income_tax', 'vat', 'corporate_tax']
            },
            {
                'code': 'CY',
                'name': 'Cyprus',
                'languages': ['en', 'el'],
                'currency': 'EUR',
                'tax_year': 'calendar',
                'features': ['income_tax', 'vat', 'corporate_tax']
            },
            {
                'code': 'CA',
                'name': 'Canada',
                'languages': ['en', 'fr'],
                'currency': 'CAD',
                'tax_year': 'calendar',
                'features': ['income_tax', 'gst_hst', 'corporate_tax']
            },
            {
                'code': 'AU',
                'name': 'Australia',
                'languages': ['en'],
                'currency': 'AUD',
                'tax_year': 'july_june',
                'features': ['income_tax', 'gst', 'corporate_tax']
            },
            {
                'code': 'NZ',
                'name': 'New Zealand',
                'languages': ['en'],
                'currency': 'NZD',
                'tax_year': 'april_march',
                'features': ['income_tax', 'gst', 'corporate_tax']
            },
            {
                'code': 'SG',
                'name': 'Singapore',
                'languages': ['en'],
                'currency': 'SGD',
                'tax_year': 'calendar',
                'features': ['income_tax', 'gst', 'corporate_tax']
            },
            {
                'code': 'HK',
                'name': 'Hong Kong',
                'languages': ['en', 'zh'],
                'currency': 'HKD',
                'tax_year': 'april_march',
                'features': ['salaries_tax', 'profits_tax', 'property_tax']
            }
        ]
        
        return jsonify({
            'success': True,
            'jurisdictions': jurisdictions
        })
        
    except Exception as e:
        logger.error(f"Failed to get jurisdictions: {e}")
        return jsonify({'error': 'Failed to retrieve jurisdictions'}), 500

@jurisdictions_bp.route('/<jurisdiction_code>', methods=['GET'])
def get_jurisdiction_details(jurisdiction_code):
    """Get detailed information about a specific jurisdiction"""
    try:
        # Sample jurisdiction details
        jurisdiction_details = {
            'MT': {
                'code': 'MT',
                'name': 'Malta',
                'full_name': 'Republic of Malta',
                'languages': ['en', 'mt'],
                'currency': 'EUR',
                'tax_year': 'calendar',
                'tax_authority': 'Malta Tax Authority',
                'tax_rates': {
                    'income_tax': [
                        {'min': 0, 'max': 9100, 'rate': 0},
                        {'min': 9101, 'max': 14500, 'rate': 15},
                        {'min': 14501, 'max': 19500, 'rate': 25},
                        {'min': 19501, 'max': 60000, 'rate': 25},
                        {'min': 60001, 'max': None, 'rate': 35}
                    ],
                    'vat_rates': [18, 7, 5, 0],
                    'corporate_tax': 35
                },
                'deadlines': {
                    'income_tax': '2024-06-30',
                    'vat_return': 'Quarterly',
                    'corporate_tax': '2024-09-30'
                }
            },
            'FR': {
                'code': 'FR',
                'name': 'France',
                'full_name': 'French Republic',
                'languages': ['fr', 'en'],
                'currency': 'EUR',
                'tax_year': 'calendar',
                'tax_authority': 'Direction Générale des Finances Publiques',
                'tax_rates': {
                    'income_tax': [
                        {'min': 0, 'max': 10777, 'rate': 0},
                        {'min': 10778, 'max': 27478, 'rate': 11},
                        {'min': 27479, 'max': 78570, 'rate': 30},
                        {'min': 78571, 'max': 168994, 'rate': 41},
                        {'min': 168995, 'max': None, 'rate': 45}
                    ],
                    'vat_rates': [20, 10, 5.5, 2.1],
                    'corporate_tax': 25
                }
            }
        }
        
        details = jurisdiction_details.get(jurisdiction_code.upper())
        if not details:
            return jsonify({'error': 'Jurisdiction not found'}), 404
        
        return jsonify({
            'success': True,
            'jurisdiction': details
        })
        
    except Exception as e:
        logger.error(f"Failed to get jurisdiction details for {jurisdiction_code}: {e}")
        return jsonify({'error': 'Failed to retrieve jurisdiction details'}), 500

@jurisdictions_bp.route('/clone', methods=['POST'])
def clone_jurisdiction():
    """Clone configuration from one jurisdiction to another"""
    try:
        data = request.get_json()
        source_jurisdiction = data.get('source_jurisdiction')
        target_jurisdiction = data.get('target_jurisdiction')
        components = data.get('components', [])
        
        if not source_jurisdiction or not target_jurisdiction:
            return jsonify({'error': 'Source and target jurisdictions are required'}), 400
        
        # Simulate cloning process
        cloning_result = {
            'clone_id': f'clone_{source_jurisdiction}_to_{target_jurisdiction}',
            'source_jurisdiction': source_jurisdiction,
            'target_jurisdiction': target_jurisdiction,
            'components_cloned': components,
            'status': 'completed',
            'created_at': '2024-01-15T10:30:00Z',
            'adaptations': [
                'Tax rates adapted to local regulations',
                'Language translations updated',
                'Currency conversions applied',
                'Local compliance rules integrated'
            ]
        }
        
        return jsonify({
            'success': True,
            'clone_result': cloning_result
        })
        
    except Exception as e:
        logger.error(f"Failed to clone jurisdiction: {e}")
        return jsonify({'error': 'Failed to clone jurisdiction'}), 500

