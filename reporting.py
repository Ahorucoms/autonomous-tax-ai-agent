"""
Reporting and Analytics API Routes
Advanced reporting capabilities for Malta Tax AI Agent
"""

from flask import Blueprint, request, jsonify
from ..services.reporting_service import ReportingService, ReportType, ReportFormat

reporting_bp = Blueprint('reporting', __name__)
reporting_service = ReportingService()

@reporting_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for reporting service"""
    return jsonify({
        'status': 'healthy',
        'service': 'reporting',
        'version': '1.0.0'
    })

@reporting_bp.route('/generate', methods=['POST'])
def generate_report():
    """Generate a new report"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['report_type', 'period_start', 'period_end']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Generate report
        result = reporting_service.generate_report(data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@reporting_bp.route('/<report_id>', methods=['GET'])
def get_report(report_id):
    """Get a specific report by ID"""
    try:
        result = reporting_service.get_report(report_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@reporting_bp.route('/', methods=['GET'])
def get_reports():
    """Get paginated list of reports"""
    try:
        # Get query parameters
        user_id = request.args.get('user_id')
        report_type = request.args.get('report_type')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        result = reporting_service.get_reports(
            user_id=user_id,
            report_type=report_type,
            page=page,
            per_page=per_page
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@reporting_bp.route('/templates', methods=['GET'])
def get_report_templates():
    """Get available report templates"""
    try:
        result = reporting_service.get_report_templates()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@reporting_bp.route('/dashboard-analytics', methods=['GET'])
def get_dashboard_analytics():
    """Get analytics data for dashboard"""
    try:
        result = reporting_service.get_dashboard_analytics()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@reporting_bp.route('/schedule', methods=['POST'])
def schedule_report():
    """Schedule automatic report generation"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['report_type', 'schedule_frequency', 'recipients']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Add user ID from headers if available
        data['user_id'] = request.headers.get('X-User-ID', 'system')
        
        result = reporting_service.schedule_report(data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@reporting_bp.route('/<report_id>/export', methods=['GET'])
def export_report(report_id):
    """Export report in specified format"""
    try:
        format = request.args.get('format', 'json')
        
        result = reporting_service.export_report(report_id, format)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@reporting_bp.route('/types', methods=['GET'])
def get_report_types():
    """Get available report types"""
    try:
        report_types = [
            {
                'value': ReportType.FILING_SUMMARY.value,
                'label': 'Filing Summary Report',
                'description': 'Comprehensive overview of filing activities and statistics'
            },
            {
                'value': ReportType.REVENUE_ANALYSIS.value,
                'label': 'Revenue Analysis Report',
                'description': 'Detailed analysis of tax revenue and financial metrics'
            },
            {
                'value': ReportType.COMPLIANCE_REPORT.value,
                'label': 'Compliance Report',
                'description': 'Compliance status and regulatory adherence analysis'
            },
            {
                'value': ReportType.USER_ACTIVITY.value,
                'label': 'User Activity Report',
                'description': 'User engagement and system usage analysis'
            },
            {
                'value': ReportType.PERFORMANCE_METRICS.value,
                'label': 'Performance Metrics Report',
                'description': 'System performance and technical metrics'
            },
            {
                'value': ReportType.TAX_BREAKDOWN.value,
                'label': 'Tax Breakdown Analysis',
                'description': 'Detailed breakdown of tax types and categories'
            },
            {
                'value': ReportType.AUDIT_REPORT.value,
                'label': 'Audit Report',
                'description': 'Audit trail and security analysis'
            },
            {
                'value': ReportType.CUSTOM_REPORT.value,
                'label': 'Custom Report',
                'description': 'User-defined custom report with flexible configuration'
            }
        ]
        
        return jsonify({
            'success': True,
            'report_types': report_types
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@reporting_bp.route('/formats', methods=['GET'])
def get_report_formats():
    """Get available report formats"""
    try:
        report_formats = [
            {
                'value': ReportFormat.JSON.value,
                'label': 'JSON',
                'description': 'JavaScript Object Notation format'
            },
            {
                'value': ReportFormat.PDF.value,
                'label': 'PDF',
                'description': 'Portable Document Format'
            },
            {
                'value': ReportFormat.EXCEL.value,
                'label': 'Excel',
                'description': 'Microsoft Excel spreadsheet format'
            },
            {
                'value': ReportFormat.CSV.value,
                'label': 'CSV',
                'description': 'Comma-Separated Values format'
            }
        ]
        
        return jsonify({
            'success': True,
            'report_formats': report_formats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

