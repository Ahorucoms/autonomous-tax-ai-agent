"""
System Administration Service for Malta Tax AI Agent
Advanced system management and configuration capabilities
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import uuid
from enum import Enum
import psutil
import platform

class SystemStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    MAINTENANCE = "maintenance"

class ServiceStatus(Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    STARTING = "starting"
    STOPPING = "stopping"

class LogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class SystemAdminService:
    """System administration service for Malta Tax AI Agent"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # System configuration
        self.system_config = {}
        self.service_registry = {}
        self.maintenance_windows = {}
        self.system_alerts = []
        self.backup_schedules = {}
        
        # Initialize system monitoring
        self._initialize_system_monitoring()
        self._initialize_service_registry()
        self._initialize_default_config()
    
    def _initialize_system_monitoring(self):
        """Initialize system monitoring capabilities"""
        self.monitoring_config = {
            'cpu_threshold': 80.0,
            'memory_threshold': 85.0,
            'disk_threshold': 90.0,
            'response_time_threshold': 5.0,
            'error_rate_threshold': 5.0,
            'check_interval': 60  # seconds
        }
        
        self.system_metrics = {
            'last_check': datetime.utcnow().isoformat(),
            'cpu_usage': 0.0,
            'memory_usage': 0.0,
            'disk_usage': 0.0,
            'network_io': {'bytes_sent': 0, 'bytes_recv': 0},
            'process_count': 0,
            'uptime': 0.0
        }
    
    def _initialize_service_registry(self):
        """Initialize service registry with core services"""
        self.service_registry = {
            'api_server': {
                'name': 'API Server',
                'status': ServiceStatus.RUNNING.value,
                'port': 5004,
                'health_endpoint': '/api/health',
                'last_check': datetime.utcnow().isoformat(),
                'uptime': 0.0,
                'restart_count': 0
            },
            'database': {
                'name': 'Database',
                'status': ServiceStatus.RUNNING.value,
                'port': None,
                'health_endpoint': None,
                'last_check': datetime.utcnow().isoformat(),
                'uptime': 0.0,
                'restart_count': 0
            },
            'document_processor': {
                'name': 'Document Processor',
                'status': ServiceStatus.RUNNING.value,
                'port': None,
                'health_endpoint': '/api/document-processing/health',
                'last_check': datetime.utcnow().isoformat(),
                'uptime': 0.0,
                'restart_count': 0
            },
            'filing_system': {
                'name': 'Filing System',
                'status': ServiceStatus.RUNNING.value,
                'port': None,
                'health_endpoint': '/api/malta-integration/health',
                'last_check': datetime.utcnow().isoformat(),
                'uptime': 0.0,
                'restart_count': 0
            },
            'batch_processor': {
                'name': 'Batch Processor',
                'status': ServiceStatus.RUNNING.value,
                'port': None,
                'health_endpoint': '/api/batch/health',
                'last_check': datetime.utcnow().isoformat(),
                'uptime': 0.0,
                'restart_count': 0
            }
        }
    
    def _initialize_default_config(self):
        """Initialize default system configuration"""
        self.system_config = {
            'system_name': 'Malta Tax AI Agent',
            'version': '1.0.0',
            'environment': 'production',
            'timezone': 'Europe/Malta',
            'max_file_size': 50 * 1024 * 1024,  # 50MB
            'session_timeout': 3600,  # 1 hour
            'rate_limiting': {
                'enabled': True,
                'requests_per_minute': 100,
                'burst_limit': 200
            },
            'security': {
                'password_policy': {
                    'min_length': 8,
                    'require_uppercase': True,
                    'require_lowercase': True,
                    'require_numbers': True,
                    'require_special_chars': True
                },
                'session_security': {
                    'secure_cookies': True,
                    'csrf_protection': True,
                    'xss_protection': True
                }
            },
            'backup': {
                'enabled': True,
                'frequency': 'daily',
                'retention_days': 30,
                'backup_location': '/backups'
            },
            'logging': {
                'level': LogLevel.INFO.value,
                'max_file_size': 100 * 1024 * 1024,  # 100MB
                'backup_count': 5,
                'log_rotation': True
            },
            'performance': {
                'cache_enabled': True,
                'cache_ttl': 3600,
                'compression_enabled': True,
                'cdn_enabled': False
            }
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        try:
            # Update system metrics
            self._update_system_metrics()
            
            # Check service health
            service_health = self._check_service_health()
            
            # Determine overall system status
            overall_status = self._determine_system_status()
            
            # Get recent alerts
            recent_alerts = self._get_recent_alerts()
            
            return {
                'success': True,
                'system_status': {
                    'overall_status': overall_status,
                    'last_check': datetime.utcnow().isoformat(),
                    'system_info': {
                        'hostname': platform.node(),
                        'platform': platform.platform(),
                        'python_version': platform.python_version(),
                        'architecture': platform.architecture()[0]
                    },
                    'system_metrics': self.system_metrics,
                    'service_health': service_health,
                    'recent_alerts': recent_alerts,
                    'maintenance_mode': self._is_maintenance_mode(),
                    'uptime': self._get_system_uptime()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system status: {str(e)}")
            raise ValueError(f"System status check failed: {str(e)}")
    
    def _update_system_metrics(self):
        """Update system performance metrics"""
        try:
            # CPU usage
            self.system_metrics['cpu_usage'] = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.system_metrics['memory_usage'] = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.system_metrics['disk_usage'] = (disk.used / disk.total) * 100
            
            # Network I/O
            network = psutil.net_io_counters()
            self.system_metrics['network_io'] = {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv
            }
            
            # Process count
            self.system_metrics['process_count'] = len(psutil.pids())
            
            # System uptime
            boot_time = psutil.boot_time()
            uptime_seconds = datetime.utcnow().timestamp() - boot_time
            self.system_metrics['uptime'] = uptime_seconds / 3600  # Convert to hours
            
            self.system_metrics['last_check'] = datetime.utcnow().isoformat()
            
        except Exception as e:
            self.logger.error(f"Error updating system metrics: {str(e)}")
    
    def _check_service_health(self) -> Dict[str, Any]:
        """Check health of all registered services"""
        service_health = {}
        
        for service_id, service_info in self.service_registry.items():
            try:
                # Simulate service health check
                # In production, this would make actual health check requests
                service_health[service_id] = {
                    'name': service_info['name'],
                    'status': service_info['status'],
                    'last_check': datetime.utcnow().isoformat(),
                    'response_time': 0.1 + (hash(service_id) % 100) / 1000,  # Simulated response time
                    'uptime': service_info['uptime'],
                    'restart_count': service_info['restart_count']
                }
                
            except Exception as e:
                service_health[service_id] = {
                    'name': service_info['name'],
                    'status': ServiceStatus.ERROR.value,
                    'last_check': datetime.utcnow().isoformat(),
                    'error': str(e)
                }
        
        return service_health
    
    def _determine_system_status(self) -> str:
        """Determine overall system status based on metrics and service health"""
        # Check if in maintenance mode
        if self._is_maintenance_mode():
            return SystemStatus.MAINTENANCE.value
        
        # Check critical thresholds
        if (self.system_metrics['cpu_usage'] > 95 or 
            self.system_metrics['memory_usage'] > 95 or 
            self.system_metrics['disk_usage'] > 95):
            return SystemStatus.CRITICAL.value
        
        # Check warning thresholds
        if (self.system_metrics['cpu_usage'] > self.monitoring_config['cpu_threshold'] or 
            self.system_metrics['memory_usage'] > self.monitoring_config['memory_threshold'] or 
            self.system_metrics['disk_usage'] > self.monitoring_config['disk_threshold']):
            return SystemStatus.WARNING.value
        
        # Check service health
        for service_id, service_info in self.service_registry.items():
            if service_info['status'] == ServiceStatus.ERROR.value:
                return SystemStatus.CRITICAL.value
            elif service_info['status'] == ServiceStatus.STOPPED.value:
                return SystemStatus.WARNING.value
        
        return SystemStatus.HEALTHY.value
    
    def _get_recent_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent system alerts"""
        # Sort alerts by timestamp (newest first) and return limited number
        sorted_alerts = sorted(self.system_alerts, key=lambda x: x['timestamp'], reverse=True)
        return sorted_alerts[:limit]
    
    def _is_maintenance_mode(self) -> bool:
        """Check if system is in maintenance mode"""
        now = datetime.utcnow()
        
        for window_id, window in self.maintenance_windows.items():
            start_time = datetime.fromisoformat(window['start_time'].replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(window['end_time'].replace('Z', '+00:00'))
            
            if start_time <= now <= end_time and window['status'] == 'active':
                return True
        
        return False
    
    def _get_system_uptime(self) -> Dict[str, Any]:
        """Get system uptime information"""
        try:
            boot_time = psutil.boot_time()
            uptime_seconds = datetime.utcnow().timestamp() - boot_time
            
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            
            return {
                'total_seconds': uptime_seconds,
                'days': days,
                'hours': hours,
                'minutes': minutes,
                'formatted': f"{days}d {hours}h {minutes}m"
            }
            
        except Exception:
            return {
                'total_seconds': 0,
                'days': 0,
                'hours': 0,
                'minutes': 0,
                'formatted': "Unknown"
            }
    
    def get_system_config(self) -> Dict[str, Any]:
        """Get current system configuration"""
        try:
            return {
                'success': True,
                'config': self.system_config
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system config: {str(e)}")
            raise ValueError(f"System config retrieval failed: {str(e)}")
    
    def update_system_config(self, config_updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update system configuration"""
        try:
            # Validate configuration updates
            validation_result = self._validate_config_updates(config_updates)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['error']
                }
            
            # Apply configuration updates
            self._apply_config_updates(config_updates)
            
            # Log configuration change
            self._log_config_change(config_updates)
            
            return {
                'success': True,
                'message': 'Configuration updated successfully',
                'updated_config': self.system_config
            }
            
        except Exception as e:
            self.logger.error(f"Error updating system config: {str(e)}")
            raise ValueError(f"System config update failed: {str(e)}")
    
    def _validate_config_updates(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration updates"""
        try:
            # Basic validation rules
            if 'max_file_size' in updates:
                if not isinstance(updates['max_file_size'], int) or updates['max_file_size'] <= 0:
                    return {'valid': False, 'error': 'max_file_size must be a positive integer'}
            
            if 'session_timeout' in updates:
                if not isinstance(updates['session_timeout'], int) or updates['session_timeout'] <= 0:
                    return {'valid': False, 'error': 'session_timeout must be a positive integer'}
            
            # Validate rate limiting settings
            if 'rate_limiting' in updates:
                rate_config = updates['rate_limiting']
                if 'requests_per_minute' in rate_config:
                    if not isinstance(rate_config['requests_per_minute'], int) or rate_config['requests_per_minute'] <= 0:
                        return {'valid': False, 'error': 'requests_per_minute must be a positive integer'}
            
            return {'valid': True}
            
        except Exception as e:
            return {'valid': False, 'error': f'Validation error: {str(e)}'}
    
    def _apply_config_updates(self, updates: Dict[str, Any]):
        """Apply configuration updates to system config"""
        def update_nested_dict(target, source):
            for key, value in source.items():
                if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                    update_nested_dict(target[key], value)
                else:
                    target[key] = value
        
        update_nested_dict(self.system_config, updates)
    
    def _log_config_change(self, updates: Dict[str, Any]):
        """Log configuration changes for audit trail"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'action': 'config_update',
            'changes': updates,
            'user': 'system_admin'  # In production, this would be the actual user
        }
        
        # Add to system alerts
        alert = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.utcnow().isoformat(),
            'level': 'info',
            'category': 'configuration',
            'message': 'System configuration updated',
            'details': updates
        }
        self.system_alerts.append(alert)
    
    def restart_service(self, service_id: str) -> Dict[str, Any]:
        """Restart a specific service"""
        try:
            if service_id not in self.service_registry:
                return {
                    'success': False,
                    'error': 'Service not found'
                }
            
            service = self.service_registry[service_id]
            
            # Simulate service restart
            service['status'] = ServiceStatus.STOPPING.value
            service['restart_count'] += 1
            
            # In production, this would actually restart the service
            # For simulation, we'll mark it as running again
            service['status'] = ServiceStatus.RUNNING.value
            service['last_check'] = datetime.utcnow().isoformat()
            
            # Log service restart
            alert = {
                'id': str(uuid.uuid4()),
                'timestamp': datetime.utcnow().isoformat(),
                'level': 'warning',
                'category': 'service',
                'message': f'Service {service["name"]} restarted',
                'details': {'service_id': service_id, 'restart_count': service['restart_count']}
            }
            self.system_alerts.append(alert)
            
            return {
                'success': True,
                'message': f'Service {service["name"]} restarted successfully',
                'service_status': service
            }
            
        except Exception as e:
            self.logger.error(f"Error restarting service: {str(e)}")
            raise ValueError(f"Service restart failed: {str(e)}")
    
    def schedule_maintenance(self, maintenance_config: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule system maintenance window"""
        try:
            # Validate maintenance configuration
            required_fields = ['start_time', 'end_time', 'description']
            for field in required_fields:
                if field not in maintenance_config:
                    return {
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }
            
            # Generate maintenance window ID
            window_id = str(uuid.uuid4())
            
            # Create maintenance window
            maintenance_window = {
                'window_id': window_id,
                'start_time': maintenance_config['start_time'],
                'end_time': maintenance_config['end_time'],
                'description': maintenance_config['description'],
                'created_at': datetime.utcnow().isoformat(),
                'created_by': maintenance_config.get('user_id', 'system'),
                'status': 'scheduled',
                'affected_services': maintenance_config.get('affected_services', []),
                'notification_sent': False
            }
            
            # Store maintenance window
            self.maintenance_windows[window_id] = maintenance_window
            
            # Create alert for scheduled maintenance
            alert = {
                'id': str(uuid.uuid4()),
                'timestamp': datetime.utcnow().isoformat(),
                'level': 'info',
                'category': 'maintenance',
                'message': 'Maintenance window scheduled',
                'details': maintenance_window
            }
            self.system_alerts.append(alert)
            
            return {
                'success': True,
                'window_id': window_id,
                'maintenance_window': maintenance_window
            }
            
        except Exception as e:
            self.logger.error(f"Error scheduling maintenance: {str(e)}")
            raise ValueError(f"Maintenance scheduling failed: {str(e)}")
    
    def get_system_logs(self, log_level: str = None, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Get system logs with filtering"""
        try:
            # In production, this would read from actual log files
            # For simulation, we'll generate sample log entries
            sample_logs = self._generate_sample_logs(limit, offset, log_level)
            
            return {
                'success': True,
                'logs': sample_logs,
                'total_count': 1000,  # Simulated total
                'pagination': {
                    'limit': limit,
                    'offset': offset,
                    'has_more': offset + limit < 1000
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system logs: {str(e)}")
            raise ValueError(f"System logs retrieval failed: {str(e)}")
    
    def _generate_sample_logs(self, limit: int, offset: int, log_level: str = None) -> List[Dict[str, Any]]:
        """Generate sample log entries for demonstration"""
        log_levels = ['debug', 'info', 'warning', 'error', 'critical']
        log_sources = ['api_server', 'database', 'document_processor', 'filing_system', 'batch_processor']
        
        logs = []
        base_time = datetime.utcnow() - timedelta(hours=24)
        
        for i in range(limit):
            log_time = base_time + timedelta(minutes=i * 2)
            level = log_levels[i % len(log_levels)]
            source = log_sources[i % len(log_sources)]
            
            # Skip if log level filter is applied and doesn't match
            if log_level and level != log_level:
                continue
            
            log_entry = {
                'timestamp': log_time.isoformat(),
                'level': level,
                'source': source,
                'message': f'Sample log message {i + offset + 1}',
                'details': {
                    'request_id': str(uuid.uuid4()),
                    'user_id': f'user_{(i % 10) + 1}',
                    'ip_address': f'192.168.1.{(i % 254) + 1}'
                }
            }
            logs.append(log_entry)
        
        return logs
    
    def create_backup(self, backup_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create system backup"""
        try:
            # Generate backup ID
            backup_id = str(uuid.uuid4())
            
            # Create backup record
            backup = {
                'backup_id': backup_id,
                'created_at': datetime.utcnow().isoformat(),
                'backup_type': backup_config.get('backup_type', 'full'),
                'description': backup_config.get('description', 'Manual backup'),
                'status': 'in_progress',
                'size_bytes': 0,
                'file_path': f'/backups/backup_{backup_id}.tar.gz',
                'created_by': backup_config.get('user_id', 'system')
            }
            
            # Simulate backup process
            # In production, this would create actual backup files
            backup['status'] = 'completed'
            backup['size_bytes'] = 1024 * 1024 * 500  # 500MB simulated size
            backup['completed_at'] = datetime.utcnow().isoformat()
            
            # Create alert for backup completion
            alert = {
                'id': str(uuid.uuid4()),
                'timestamp': datetime.utcnow().isoformat(),
                'level': 'info',
                'category': 'backup',
                'message': 'System backup completed',
                'details': backup
            }
            self.system_alerts.append(alert)
            
            return {
                'success': True,
                'backup_id': backup_id,
                'backup': backup
            }
            
        except Exception as e:
            self.logger.error(f"Error creating backup: {str(e)}")
            raise ValueError(f"Backup creation failed: {str(e)}")
    
    def get_performance_metrics(self, time_range: str = '24h') -> Dict[str, Any]:
        """Get detailed performance metrics"""
        try:
            # Generate performance metrics for the specified time range
            metrics = self._generate_performance_metrics(time_range)
            
            return {
                'success': True,
                'time_range': time_range,
                'metrics': metrics,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting performance metrics: {str(e)}")
            raise ValueError(f"Performance metrics retrieval failed: {str(e)}")
    
    def _generate_performance_metrics(self, time_range: str) -> Dict[str, Any]:
        """Generate performance metrics for specified time range"""
        # Determine time range in hours
        if time_range == '1h':
            hours = 1
        elif time_range == '24h':
            hours = 24
        elif time_range == '7d':
            hours = 24 * 7
        elif time_range == '30d':
            hours = 24 * 30
        else:
            hours = 24  # Default to 24 hours
        
        # Generate sample metrics
        base_time = datetime.utcnow() - timedelta(hours=hours)
        data_points = min(hours, 100)  # Limit data points for performance
        interval = hours / data_points
        
        cpu_data = []
        memory_data = []
        response_time_data = []
        request_count_data = []
        
        for i in range(data_points):
            timestamp = base_time + timedelta(hours=i * interval)
            
            cpu_data.append({
                'timestamp': timestamp.isoformat(),
                'value': 30 + (i % 20) + (i % 3 * 5)  # Simulated CPU usage
            })
            
            memory_data.append({
                'timestamp': timestamp.isoformat(),
                'value': 45 + (i % 15) + (i % 4 * 3)  # Simulated memory usage
            })
            
            response_time_data.append({
                'timestamp': timestamp.isoformat(),
                'value': 0.5 + (i % 10) * 0.1  # Simulated response time
            })
            
            request_count_data.append({
                'timestamp': timestamp.isoformat(),
                'value': 100 + (i % 50) + (i % 5 * 20)  # Simulated request count
            })
        
        return {
            'cpu_usage': cpu_data,
            'memory_usage': memory_data,
            'response_times': response_time_data,
            'request_counts': request_count_data,
            'summary': {
                'avg_cpu': sum(d['value'] for d in cpu_data) / len(cpu_data),
                'avg_memory': sum(d['value'] for d in memory_data) / len(memory_data),
                'avg_response_time': sum(d['value'] for d in response_time_data) / len(response_time_data),
                'total_requests': sum(d['value'] for d in request_count_data)
            }
        }

