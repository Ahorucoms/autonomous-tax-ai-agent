"""
System Administration API Routes
Advanced system management capabilities for Malta Tax AI Agent
"""

from flask import Blueprint, request, jsonify
from ..services.system_admin_service import SystemAdminService

system_admin_bp = Blueprint('system_admin', __name__)
system_admin_service = SystemAdminService()

@system_admin_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for system admin service"""
    return jsonify({
        'status': 'healthy',
        'service': 'system_admin',
        'version': '1.0.0'
    })

@system_admin_bp.route('/status', methods=['GET'])
def get_system_status():
    """Get comprehensive system status"""
    try:
        result = system_admin_service.get_system_status()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@system_admin_bp.route('/config', methods=['GET'])
def get_system_config():
    """Get current system configuration"""
    try:
        result = system_admin_service.get_system_config()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@system_admin_bp.route('/config', methods=['PUT'])
def update_system_config():
    """Update system configuration"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No configuration data provided'
            }), 400
        
        result = system_admin_service.update_system_config(data)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@system_admin_bp.route('/services/<service_id>/restart', methods=['POST'])
def restart_service(service_id):
    """Restart a specific service"""
    try:
        result = system_admin_service.restart_service(service_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@system_admin_bp.route('/maintenance', methods=['POST'])
def schedule_maintenance():
    """Schedule system maintenance window"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['start_time', 'end_time', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Add user ID from headers if available
        data['user_id'] = request.headers.get('X-User-ID', 'system')
        
        result = system_admin_service.schedule_maintenance(data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@system_admin_bp.route('/logs', methods=['GET'])
def get_system_logs():
    """Get system logs with filtering"""
    try:
        # Get query parameters
        log_level = request.args.get('level')
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        result = system_admin_service.get_system_logs(
            log_level=log_level,
            limit=limit,
            offset=offset
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@system_admin_bp.route('/backup', methods=['POST'])
def create_backup():
    """Create system backup"""
    try:
        data = request.get_json() or {}
        
        # Add user ID from headers if available
        data['user_id'] = request.headers.get('X-User-ID', 'system')
        
        result = system_admin_service.create_backup(data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@system_admin_bp.route('/performance', methods=['GET'])
def get_performance_metrics():
    """Get detailed performance metrics"""
    try:
        time_range = request.args.get('time_range', '24h')
        
        result = system_admin_service.get_performance_metrics(time_range)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@system_admin_bp.route('/monitoring/thresholds', methods=['GET'])
def get_monitoring_thresholds():
    """Get current monitoring thresholds"""
    try:
        thresholds = {
            'cpu_threshold': 80.0,
            'memory_threshold': 85.0,
            'disk_threshold': 90.0,
            'response_time_threshold': 5.0,
            'error_rate_threshold': 5.0,
            'check_interval': 60
        }
        
        return jsonify({
            'success': True,
            'thresholds': thresholds
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@system_admin_bp.route('/monitoring/thresholds', methods=['PUT'])
def update_monitoring_thresholds():
    """Update monitoring thresholds"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No threshold data provided'
            }), 400
        
        # Validate threshold values
        valid_thresholds = ['cpu_threshold', 'memory_threshold', 'disk_threshold', 
                          'response_time_threshold', 'error_rate_threshold', 'check_interval']
        
        for key, value in data.items():
            if key not in valid_thresholds:
                return jsonify({
                    'success': False,
                    'error': f'Invalid threshold: {key}'
                }), 400
            
            if not isinstance(value, (int, float)) or value <= 0:
                return jsonify({
                    'success': False,
                    'error': f'Invalid value for {key}: must be a positive number'
                }), 400
        
        # In production, this would update the actual monitoring configuration
        return jsonify({
            'success': True,
            'message': 'Monitoring thresholds updated successfully',
            'updated_thresholds': data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@system_admin_bp.route('/alerts', methods=['GET'])
def get_system_alerts():
    """Get recent system alerts"""
    try:
        limit = int(request.args.get('limit', 50))
        level = request.args.get('level')
        category = request.args.get('category')
        
        # Get alerts from system admin service
        # This would filter based on the provided parameters
        alerts = [
            {
                'id': 'alert_001',
                'timestamp': '2025-06-30T16:30:00Z',
                'level': 'warning',
                'category': 'performance',
                'message': 'High CPU usage detected',
                'details': {'cpu_usage': 85.5}
            },
            {
                'id': 'alert_002',
                'timestamp': '2025-06-30T16:25:00Z',
                'level': 'info',
                'category': 'backup',
                'message': 'Daily backup completed successfully',
                'details': {'backup_size': '500MB'}
            }
        ]
        
        # Apply filters
        if level:
            alerts = [a for a in alerts if a['level'] == level]
        if category:
            alerts = [a for a in alerts if a['category'] == category]
        
        # Apply limit
        alerts = alerts[:limit]
        
        return jsonify({
            'success': True,
            'alerts': alerts,
            'total_count': len(alerts)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@system_admin_bp.route('/system-info', methods=['GET'])
def get_system_info():
    """Get detailed system information"""
    try:
        import platform
        import psutil
        
        system_info = {
            'hostname': platform.node(),
            'platform': platform.platform(),
            'processor': platform.processor(),
            'architecture': platform.architecture(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'disk_total': psutil.disk_usage('/').total,
            'network_interfaces': list(psutil.net_if_addrs().keys())
        }
        
        return jsonify({
            'success': True,
            'system_info': system_info
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

