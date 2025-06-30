"""
Admin Management API Routes
Handle administrative functionality for user and system management
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import logging
from typing import Dict, Any

from ..services.admin_service import AdminService, UserRole, UserStatus, AuditAction

admin_bp = Blueprint('admin', __name__)

# Initialize admin service
admin_service = AdminService()

@admin_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'admin',
        'timestamp': datetime.utcnow().isoformat()
    })

@admin_bp.route('/login', methods=['POST'])
def admin_login():
    """Admin authentication"""
    try:
        data = request.get_json()
        
        required_fields = ['username', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        result = admin_service.authenticate_admin(data['username'], data['password'])
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 401
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error in admin login: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    """Get admin dashboard data"""
    try:
        result = admin_service.get_dashboard_data()
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error getting dashboard data: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/users', methods=['GET'])
def get_users():
    """Get paginated list of users"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        role = request.args.get('role')
        status = request.args.get('status')
        
        if page < 1:
            return jsonify({'error': 'Page must be >= 1'}), 400
        if per_page < 1 or per_page > 100:
            return jsonify({'error': 'Per page must be between 1 and 100'}), 400
        
        result = admin_service.get_users(page, per_page, role, status)
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error getting users: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/users', methods=['POST'])
def create_user():
    """Create new user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request data is required'}), 400
        
        # Get admin user ID from session (simplified for development)
        admin_user_id = request.headers.get('X-Admin-User-ID', 'admin_001')
        
        result = admin_service.create_user(data, admin_user_id)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error creating user: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    """Update existing user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request data is required'}), 400
        
        # Get admin user ID from session (simplified for development)
        admin_user_id = request.headers.get('X-Admin-User-ID', 'admin_001')
        
        result = admin_service.update_user(user_id, data, admin_user_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error updating user: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete user"""
    try:
        # Get admin user ID from session (simplified for development)
        admin_user_id = request.headers.get('X-Admin-User-ID', 'admin_001')
        
        result = admin_service.delete_user(user_id, admin_user_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 404
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error deleting user: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/audit-logs', methods=['GET'])
def get_audit_logs():
    """Get paginated audit logs"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        action = request.args.get('action')
        user_id = request.args.get('user_id')
        
        if page < 1:
            return jsonify({'error': 'Page must be >= 1'}), 400
        if per_page < 1 or per_page > 100:
            return jsonify({'error': 'Per page must be between 1 and 100'}), 400
        
        result = admin_service.get_audit_logs(page, per_page, action, user_id)
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error getting audit logs: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/system/config', methods=['GET'])
def get_system_config():
    """Get system configuration"""
    try:
        result = admin_service.get_system_config()
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error getting system config: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/system/config', methods=['PUT'])
def update_system_config():
    """Update system configuration"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Configuration data is required'}), 400
        
        # Get admin user ID from session (simplified for development)
        admin_user_id = request.headers.get('X-Admin-User-ID', 'admin_001')
        
        result = admin_service.update_system_config(data, admin_user_id)
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error updating system config: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/system/health', methods=['GET'])
def get_system_health():
    """Get system health status"""
    try:
        result = admin_service.get_system_health()
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error getting system health: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/system/performance', methods=['GET'])
def get_performance_metrics():
    """Get system performance metrics"""
    try:
        result = admin_service.get_performance_metrics()
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error getting performance metrics: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/users/roles', methods=['GET'])
def get_user_roles():
    """Get available user roles"""
    try:
        roles = [
            {
                'value': role.value,
                'name': role.name.replace('_', ' ').title(),
                'description': f'{role.value.replace("_", " ").title()} role'
            }
            for role in UserRole
        ]
        
        return jsonify({
            'success': True,
            'roles': roles
        })
        
    except Exception as e:
        logging.error(f"Error getting user roles: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/users/statuses', methods=['GET'])
def get_user_statuses():
    """Get available user statuses"""
    try:
        statuses = [
            {
                'value': status.value,
                'name': status.name.replace('_', ' ').title(),
                'description': f'{status.value.replace("_", " ").title()} status'
            }
            for status in UserStatus
        ]
        
        return jsonify({
            'success': True,
            'statuses': statuses
        })
        
    except Exception as e:
        logging.error(f"Error getting user statuses: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/audit/actions', methods=['GET'])
def get_audit_actions():
    """Get available audit actions"""
    try:
        actions = [
            {
                'value': action.value,
                'name': action.name.replace('_', ' ').title(),
                'description': f'{action.value.replace("_", " ").title()} action'
            }
            for action in AuditAction
        ]
        
        return jsonify({
            'success': True,
            'actions': actions
        })
        
    except Exception as e:
        logging.error(f"Error getting audit actions: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/users/<user_id>/suspend', methods=['POST'])
def suspend_user(user_id):
    """Suspend user account"""
    try:
        # Get admin user ID from session (simplified for development)
        admin_user_id = request.headers.get('X-Admin-User-ID', 'admin_001')
        
        result = admin_service.update_user(
            user_id, 
            {'status': UserStatus.SUSPENDED.value}, 
            admin_user_id
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'User suspended successfully',
                'user': result['user']
            })
        else:
            return jsonify(result), 400
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error suspending user: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/users/<user_id>/activate', methods=['POST'])
def activate_user(user_id):
    """Activate user account"""
    try:
        # Get admin user ID from session (simplified for development)
        admin_user_id = request.headers.get('X-Admin-User-ID', 'admin_001')
        
        result = admin_service.update_user(
            user_id, 
            {'status': UserStatus.ACTIVE.value}, 
            admin_user_id
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'User activated successfully',
                'user': result['user']
            })
        else:
            return jsonify(result), 400
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error activating user: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/statistics/summary', methods=['GET'])
def get_statistics_summary():
    """Get summary statistics for admin dashboard"""
    try:
        # Get dashboard data which includes statistics
        dashboard_result = admin_service.get_dashboard_data()
        
        if dashboard_result['success']:
            dashboard_data = dashboard_result['dashboard_data']
            
            summary = {
                'overview': dashboard_data['overview'],
                'user_statistics': dashboard_data['user_statistics'],
                'filing_statistics': dashboard_data['filing_statistics'],
                'performance_summary': {
                    'avg_response_time': dashboard_data['performance_metrics']['avg_response_time'],
                    'success_rate': dashboard_data['performance_metrics']['success_rate'],
                    'uptime_hours': dashboard_data['performance_metrics']['uptime_hours']
                }
            }
            
            return jsonify({
                'success': True,
                'statistics': summary
            })
        else:
            return jsonify({'error': 'Failed to get statistics'}), 500
        
    except Exception as e:
        logging.error(f"Error getting statistics summary: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

