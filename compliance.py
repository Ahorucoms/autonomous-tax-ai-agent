"""
Compliance and Validation API Routes
Handle Malta tax compliance checking, deadline tracking, and penalty calculations
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from decimal import Decimal
import logging
from typing import Dict, Any

from ..services.compliance_engine import MaltaComplianceEngine, PenaltyType, AlertSeverity

compliance_bp = Blueprint('compliance', __name__)

# Initialize compliance engine
compliance_engine = MaltaComplianceEngine()

@compliance_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'compliance',
        'timestamp': datetime.utcnow().isoformat()
    })

@compliance_bp.route('/check', methods=['POST'])
def check_compliance():
    """Check compliance status for a user"""
    try:
        data = request.get_json()
        
        if 'user_id' not in data:
            return jsonify({'error': 'User ID is required'}), 400
        
        if 'financial_data' not in data:
            return jsonify({'error': 'Financial data is required'}), 400
        
        user_id = data['user_id']
        financial_data = data['financial_data']
        
        compliance_record = compliance_engine.check_compliance(user_id, financial_data)
        
        return jsonify({
            'success': True,
            'compliance': compliance_record
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error checking compliance: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@compliance_bp.route('/dashboard/<user_id>', methods=['GET'])
def get_compliance_dashboard(user_id):
    """Get compliance dashboard for a user"""
    try:
        dashboard = compliance_engine.get_compliance_dashboard(user_id)
        
        return jsonify({
            'success': True,
            'dashboard': dashboard
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error getting compliance dashboard: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@compliance_bp.route('/penalties/calculate', methods=['POST'])
def calculate_penalties():
    """Calculate penalties for tax violations"""
    try:
        data = request.get_json()
        
        required_fields = ['violation_type', 'tax_type', 'days_late']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        violation_type = data['violation_type']
        tax_type = data['tax_type']
        days_late = int(data['days_late'])
        tax_amount = None
        
        if 'tax_amount' in data:
            tax_amount = Decimal(str(data['tax_amount']))
        
        if days_late < 0:
            return jsonify({'error': 'Days late must be non-negative'}), 400
        
        # Validate violation type
        try:
            PenaltyType(violation_type)
        except ValueError:
            return jsonify({'error': 'Invalid violation type'}), 400
        
        penalty_info = compliance_engine.calculate_penalties(
            violation_type, tax_type, days_late, tax_amount
        )
        
        return jsonify({
            'success': True,
            'penalties': penalty_info
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error calculating penalties: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@compliance_bp.route('/alerts/create', methods=['POST'])
def create_alert():
    """Create a compliance alert"""
    try:
        data = request.get_json()
        
        required_fields = ['user_id', 'alert_type', 'severity', 'message']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        user_id = data['user_id']
        alert_type = data['alert_type']
        message = data['message']
        alert_data = data.get('data', {})
        
        try:
            severity = AlertSeverity(data['severity'])
        except ValueError:
            return jsonify({'error': 'Invalid severity level'}), 400
        
        alert_id = compliance_engine.create_alert(
            user_id, alert_type, severity, message, alert_data
        )
        
        return jsonify({
            'success': True,
            'alert_id': alert_id,
            'message': 'Alert created successfully'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error creating alert: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@compliance_bp.route('/alerts/<user_id>', methods=['GET'])
def get_user_alerts(user_id):
    """Get alerts for a user"""
    try:
        # Filter alerts by user and status
        resolved = request.args.get('resolved', 'false').lower() == 'true'
        
        user_alerts = [
            alert for alert in compliance_engine.alerts.values()
            if alert['user_id'] == user_id and alert['resolved'] == resolved
        ]
        
        # Sort by creation date (newest first)
        user_alerts = sorted(
            user_alerts, 
            key=lambda a: a['created_at'], 
            reverse=True
        )
        
        return jsonify({
            'success': True,
            'alerts': user_alerts,
            'count': len(user_alerts)
        })
        
    except Exception as e:
        logging.error(f"Error getting user alerts: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@compliance_bp.route('/alerts/<alert_id>/acknowledge', methods=['PUT'])
def acknowledge_alert(alert_id):
    """Acknowledge an alert"""
    try:
        alert = compliance_engine.alerts.get(alert_id)
        if not alert:
            return jsonify({'error': 'Alert not found'}), 404
        
        alert['acknowledged'] = True
        alert['acknowledged_at'] = datetime.utcnow().isoformat()
        
        return jsonify({
            'success': True,
            'message': 'Alert acknowledged successfully'
        })
        
    except Exception as e:
        logging.error(f"Error acknowledging alert: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@compliance_bp.route('/alerts/<alert_id>/resolve', methods=['PUT'])
def resolve_alert(alert_id):
    """Resolve an alert"""
    try:
        alert = compliance_engine.alerts.get(alert_id)
        if not alert:
            return jsonify({'error': 'Alert not found'}), 404
        
        data = request.get_json() or {}
        resolution_notes = data.get('resolution_notes', '')
        
        alert['resolved'] = True
        alert['resolved_at'] = datetime.utcnow().isoformat()
        alert['resolution_notes'] = resolution_notes
        
        return jsonify({
            'success': True,
            'message': 'Alert resolved successfully'
        })
        
    except Exception as e:
        logging.error(f"Error resolving alert: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@compliance_bp.route('/deadlines/<user_id>', methods=['GET'])
def get_upcoming_deadlines(user_id):
    """Get upcoming deadlines for a user"""
    try:
        # Get the latest compliance record for the user
        user_compliance_records = [
            record for record in compliance_engine.compliance_records.values()
            if record['user_id'] == user_id
        ]
        
        if not user_compliance_records:
            return jsonify({
                'success': True,
                'deadlines': [],
                'message': 'No compliance data found. Run compliance check first.'
            })
        
        latest_compliance = max(
            user_compliance_records, 
            key=lambda r: r['checked_at']
        )
        
        deadlines = latest_compliance.get('upcoming_deadlines', [])
        
        return jsonify({
            'success': True,
            'deadlines': deadlines,
            'count': len(deadlines)
        })
        
    except Exception as e:
        logging.error(f"Error getting upcoming deadlines: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@compliance_bp.route('/regulatory-updates', methods=['GET'])
def get_regulatory_updates():
    """Get recent regulatory changes and updates"""
    try:
        updates = compliance_engine.get_regulatory_updates()
        
        return jsonify({
            'success': True,
            'updates': updates,
            'count': len(updates)
        })
        
    except Exception as e:
        logging.error(f"Error getting regulatory updates: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@compliance_bp.route('/audit-logs/<user_id>', methods=['GET'])
def get_audit_logs(user_id):
    """Get audit logs for a user"""
    try:
        limit = request.args.get('limit', 50, type=int)
        event_type = request.args.get('event_type')
        
        # Filter audit logs by user
        user_logs = [
            log for log in compliance_engine.audit_logs.values()
            if log['user_id'] == user_id
        ]
        
        # Filter by event type if specified
        if event_type:
            user_logs = [log for log in user_logs if log['event_type'] == event_type]
        
        # Sort by timestamp (newest first) and limit
        user_logs = sorted(
            user_logs, 
            key=lambda l: l['timestamp'], 
            reverse=True
        )[:limit]
        
        return jsonify({
            'success': True,
            'audit_logs': user_logs,
            'count': len(user_logs)
        })
        
    except Exception as e:
        logging.error(f"Error getting audit logs: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@compliance_bp.route('/statistics', methods=['GET'])
def get_compliance_statistics():
    """Get compliance statistics (admin endpoint)"""
    try:
        all_compliance_records = list(compliance_engine.compliance_records.values())
        all_alerts = list(compliance_engine.alerts.values())
        
        # Calculate statistics
        stats = {
            'total_compliance_checks': len(all_compliance_records),
            'compliance_status_breakdown': {},
            'alert_severity_breakdown': {},
            'recent_checks': 0,
            'active_alerts': 0
        }
        
        # Count by compliance status
        for status in ['compliant', 'warning', 'non_compliant', 'overdue']:
            count = len([r for r in all_compliance_records if r['overall_status'] == status])
            stats['compliance_status_breakdown'][status] = count
        
        # Count by alert severity
        for severity in ['info', 'warning', 'critical']:
            count = len([a for a in all_alerts if a['severity'] == severity])
            stats['alert_severity_breakdown'][severity] = count
        
        # Count recent checks (last 7 days)
        from datetime import timedelta
        week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
        stats['recent_checks'] = len([
            r for r in all_compliance_records 
            if r['checked_at'] > week_ago
        ])
        
        # Count active alerts
        stats['active_alerts'] = len([a for a in all_alerts if not a['resolved']])
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        logging.error(f"Error getting compliance statistics: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@compliance_bp.route('/rules', methods=['GET'])
def get_compliance_rules():
    """Get all compliance rules"""
    try:
        rules = compliance_engine.compliance_rules
        
        return jsonify({
            'success': True,
            'rules': rules,
            'count': len(rules)
        })
        
    except Exception as e:
        logging.error(f"Error getting compliance rules: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

