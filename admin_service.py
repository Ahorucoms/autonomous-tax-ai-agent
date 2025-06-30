"""
Admin Service for Malta Tax AI Agent
Comprehensive administrative functionality for user and system management
"""

import os
import json
import logging
import hashlib
import secrets
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any, Optional
import uuid
from enum import Enum

class UserRole(Enum):
    ADMIN = "admin"
    TAX_PROFESSIONAL = "tax_professional"
    USER = "user"
    VIEWER = "viewer"

class UserStatus(Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"
    INACTIVE = "inactive"

class AuditAction(Enum):
    LOGIN = "login"
    LOGOUT = "logout"
    CREATE_USER = "create_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    SUSPEND_USER = "suspend_user"
    FILING_SUBMITTED = "filing_submitted"
    PAYMENT_PROCESSED = "payment_processed"
    SYSTEM_CONFIG_CHANGED = "system_config_changed"
    BATCH_PROCESSED = "batch_processed"

class AdminService:
    """Administrative service for Malta Tax AI Agent"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Storage for admin data
        self.admin_users = {}
        self.system_users = {}
        self.audit_logs = []
        self.system_config = {}
        self.performance_metrics = {}
        self.system_health = {}
        
        # Initialize default admin user and system config
        self._initialize_default_admin()
        self._initialize_system_config()
        self._initialize_performance_tracking()
    
    def _initialize_default_admin(self):
        """Initialize default admin user"""
        admin_id = "admin_001"
        admin_user = {
            'user_id': admin_id,
            'username': 'admin',
            'email': 'admin@maltatax.ai',
            'password_hash': self._hash_password('admin123'),  # Default password
            'role': UserRole.ADMIN.value,
            'status': UserStatus.ACTIVE.value,
            'created_at': datetime.utcnow().isoformat(),
            'last_login': None,
            'permissions': [
                'user_management',
                'system_config',
                'audit_logs',
                'batch_processing',
                'reporting',
                'system_monitoring'
            ]
        }
        self.admin_users[admin_id] = admin_user
        
        # Create some sample users for testing
        self._create_sample_users()
    
    def _create_sample_users(self):
        """Create sample users for testing"""
        sample_users = [
            {
                'username': 'john_doe',
                'email': 'john.doe@example.com',
                'role': UserRole.USER.value,
                'status': UserStatus.ACTIVE.value,
                'full_name': 'John Doe',
                'tax_number': 'MT12345678'
            },
            {
                'username': 'tax_pro_1',
                'email': 'professional@taxfirm.com',
                'role': UserRole.TAX_PROFESSIONAL.value,
                'status': UserStatus.ACTIVE.value,
                'full_name': 'Maria Borg',
                'tax_number': 'MT87654321'
            },
            {
                'username': 'viewer_user',
                'email': 'viewer@company.com',
                'role': UserRole.VIEWER.value,
                'status': UserStatus.ACTIVE.value,
                'full_name': 'David Camilleri',
                'tax_number': 'MT11223344'
            }
        ]
        
        for user_data in sample_users:
            user_id = str(uuid.uuid4())
            user = {
                'user_id': user_id,
                'username': user_data['username'],
                'email': user_data['email'],
                'password_hash': self._hash_password('password123'),
                'role': user_data['role'],
                'status': user_data['status'],
                'full_name': user_data['full_name'],
                'tax_number': user_data['tax_number'],
                'created_at': datetime.utcnow().isoformat(),
                'last_login': None,
                'login_count': 0,
                'filings_count': 0,
                'total_tax_paid': 0.0
            }
            self.system_users[user_id] = user
    
    def _initialize_system_config(self):
        """Initialize system configuration"""
        self.system_config = {
            'tax_rates': {
                'income_tax_brackets': [
                    {'min': 0, 'max': 9100, 'rate': 0.0},
                    {'min': 9101, 'max': 14500, 'rate': 15.0},
                    {'min': 14501, 'max': 19500, 'rate': 25.0},
                    {'min': 19501, 'max': 60000, 'rate': 25.0},
                    {'min': 60001, 'max': float('inf'), 'rate': 35.0}
                ],
                'vat_rates': {
                    'standard': 18.0,
                    'reduced_1': 12.0,
                    'reduced_2': 7.0,
                    'reduced_3': 5.0,
                    'zero': 0.0
                },
                'social_security_rates': {
                    'class1_employee': 10.0,
                    'class1_employer': 10.0,
                    'class2_self_employed': 15.0
                }
            },
            'filing_deadlines': {
                'income_tax_individual': 'June 30',
                'income_tax_corporate': '9 months after year end',
                'vat_return': '15th of following month/quarter',
                'social_security': '15th of following month'
            },
            'system_settings': {
                'max_file_size_mb': 50,
                'session_timeout_minutes': 30,
                'max_batch_size': 1000,
                'backup_frequency_hours': 24,
                'audit_retention_days': 365
            },
            'notification_settings': {
                'email_enabled': True,
                'sms_enabled': False,
                'deadline_reminder_days': [30, 14, 7, 1],
                'admin_alerts_enabled': True
            }
        }
    
    def _initialize_performance_tracking(self):
        """Initialize performance metrics tracking"""
        self.performance_metrics = {
            'api_response_times': [],
            'filing_processing_times': [],
            'payment_processing_times': [],
            'document_processing_times': [],
            'system_uptime': datetime.utcnow().isoformat(),
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'active_users': 0,
            'total_filings': 0,
            'total_payments': 0
        }
        
        self.system_health = {
            'status': 'healthy',
            'last_check': datetime.utcnow().isoformat(),
            'services': {
                'database': 'operational',
                'api': 'operational',
                'filing_system': 'operational',
                'payment_system': 'operational',
                'document_processing': 'operational'
            },
            'alerts': []
        }
    
    def _hash_password(self, password: str) -> str:
        """Hash password for secure storage"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}:{password_hash.hex()}"
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            salt, hash_value = password_hash.split(':')
            password_hash_check = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return password_hash_check.hex() == hash_value
        except Exception:
            return False
    
    def authenticate_admin(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate admin user"""
        try:
            # Find admin user
            admin_user = None
            for user in self.admin_users.values():
                if user['username'] == username:
                    admin_user = user
                    break
            
            if not admin_user:
                return {
                    'success': False,
                    'error': 'Invalid credentials'
                }
            
            # Verify password
            if not self._verify_password(password, admin_user['password_hash']):
                return {
                    'success': False,
                    'error': 'Invalid credentials'
                }
            
            # Check if user is active
            if admin_user['status'] != UserStatus.ACTIVE.value:
                return {
                    'success': False,
                    'error': 'Account is not active'
                }
            
            # Update last login
            admin_user['last_login'] = datetime.utcnow().isoformat()
            
            # Log authentication
            self._log_audit_action(
                user_id=admin_user['user_id'],
                action=AuditAction.LOGIN,
                details={'username': username}
            )
            
            # Generate session token (simplified)
            session_token = secrets.token_urlsafe(32)
            
            return {
                'success': True,
                'user': {
                    'user_id': admin_user['user_id'],
                    'username': admin_user['username'],
                    'email': admin_user['email'],
                    'role': admin_user['role'],
                    'permissions': admin_user['permissions']
                },
                'session_token': session_token,
                'expires_at': (datetime.utcnow() + timedelta(hours=8)).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error authenticating admin: {str(e)}")
            raise ValueError(f"Authentication failed: {str(e)}")
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get admin dashboard data"""
        try:
            # Calculate statistics
            total_users = len(self.system_users)
            active_users = len([u for u in self.system_users.values() if u['status'] == UserStatus.ACTIVE.value])
            total_filings = sum(u.get('filings_count', 0) for u in self.system_users.values())
            total_revenue = sum(u.get('total_tax_paid', 0) for u in self.system_users.values())
            
            # Recent activity (last 7 days)
            recent_logs = [log for log in self.audit_logs[-50:]]  # Last 50 activities
            
            # System health summary
            health_status = self.system_health['status']
            service_issues = [service for service, status in self.system_health['services'].items() if status != 'operational']
            
            dashboard_data = {
                'overview': {
                    'total_users': total_users,
                    'active_users': active_users,
                    'total_filings': total_filings,
                    'total_revenue': total_revenue,
                    'system_health': health_status,
                    'service_issues': len(service_issues)
                },
                'recent_activity': recent_logs,
                'system_health': self.system_health,
                'performance_metrics': {
                    'avg_response_time': sum(self.performance_metrics['api_response_times'][-100:]) / max(len(self.performance_metrics['api_response_times'][-100:]), 1),
                    'success_rate': (self.performance_metrics['successful_requests'] / max(self.performance_metrics['total_requests'], 1)) * 100,
                    'uptime_hours': (datetime.utcnow() - datetime.fromisoformat(self.performance_metrics['system_uptime'])).total_seconds() / 3600
                },
                'user_statistics': {
                    'by_role': self._get_user_role_breakdown(),
                    'by_status': self._get_user_status_breakdown(),
                    'registration_trend': self._get_registration_trend()
                },
                'filing_statistics': {
                    'by_type': self._get_filing_type_breakdown(),
                    'by_status': self._get_filing_status_breakdown(),
                    'monthly_trend': self._get_monthly_filing_trend()
                }
            }
            
            return {
                'success': True,
                'dashboard_data': dashboard_data
            }
            
        except Exception as e:
            self.logger.error(f"Error getting dashboard data: {str(e)}")
            raise ValueError(f"Dashboard data retrieval failed: {str(e)}")
    
    def _get_user_role_breakdown(self) -> Dict[str, int]:
        """Get user breakdown by role"""
        breakdown = {}
        for user in self.system_users.values():
            role = user['role']
            breakdown[role] = breakdown.get(role, 0) + 1
        return breakdown
    
    def _get_user_status_breakdown(self) -> Dict[str, int]:
        """Get user breakdown by status"""
        breakdown = {}
        for user in self.system_users.values():
            status = user['status']
            breakdown[status] = breakdown.get(status, 0) + 1
        return breakdown
    
    def _get_registration_trend(self) -> List[Dict[str, Any]]:
        """Get user registration trend (simplified)"""
        # Simplified trend data
        return [
            {'month': 'Jan 2025', 'registrations': 45},
            {'month': 'Feb 2025', 'registrations': 52},
            {'month': 'Mar 2025', 'registrations': 38},
            {'month': 'Apr 2025', 'registrations': 61},
            {'month': 'May 2025', 'registrations': 47},
            {'month': 'Jun 2025', 'registrations': 33}
        ]
    
    def _get_filing_type_breakdown(self) -> Dict[str, int]:
        """Get filing breakdown by type (simplified)"""
        return {
            'income_tax_individual': 156,
            'vat_return': 89,
            'social_security_class1': 134,
            'social_security_class2': 67,
            'income_tax_corporate': 23
        }
    
    def _get_filing_status_breakdown(self) -> Dict[str, int]:
        """Get filing breakdown by status (simplified)"""
        return {
            'submitted': 234,
            'processed': 189,
            'acknowledged': 156,
            'rejected': 12,
            'pending': 45
        }
    
    def _get_monthly_filing_trend(self) -> List[Dict[str, Any]]:
        """Get monthly filing trend (simplified)"""
        return [
            {'month': 'Jan 2025', 'filings': 89},
            {'month': 'Feb 2025', 'filings': 76},
            {'month': 'Mar 2025', 'filings': 134},
            {'month': 'Apr 2025', 'filings': 98},
            {'month': 'May 2025', 'filings': 112},
            {'month': 'Jun 2025', 'filings': 156}
        ]
    
    def get_users(self, page: int = 1, per_page: int = 20, role: str = None, status: str = None) -> Dict[str, Any]:
        """Get paginated list of users"""
        try:
            users = list(self.system_users.values())
            
            # Apply filters
            if role:
                users = [u for u in users if u['role'] == role]
            if status:
                users = [u for u in users if u['status'] == status]
            
            # Sort by creation date (newest first)
            users = sorted(users, key=lambda u: u['created_at'], reverse=True)
            
            # Pagination
            total_users = len(users)
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            paginated_users = users[start_idx:end_idx]
            
            # Remove sensitive data
            safe_users = []
            for user in paginated_users:
                safe_user = user.copy()
                safe_user.pop('password_hash', None)
                safe_users.append(safe_user)
            
            return {
                'success': True,
                'users': safe_users,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total_users,
                    'pages': (total_users + per_page - 1) // per_page
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting users: {str(e)}")
            raise ValueError(f"User retrieval failed: {str(e)}")
    
    def create_user(self, user_data: Dict[str, Any], admin_user_id: str) -> Dict[str, Any]:
        """Create new user"""
        try:
            # Validate required fields
            required_fields = ['username', 'email', 'password', 'role']
            for field in required_fields:
                if field not in user_data:
                    return {
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }
            
            # Check if username or email already exists
            for user in self.system_users.values():
                if user['username'] == user_data['username']:
                    return {
                        'success': False,
                        'error': 'Username already exists'
                    }
                if user['email'] == user_data['email']:
                    return {
                        'success': False,
                        'error': 'Email already exists'
                    }
            
            # Validate role
            try:
                UserRole(user_data['role'])
            except ValueError:
                return {
                    'success': False,
                    'error': 'Invalid role'
                }
            
            # Create user
            user_id = str(uuid.uuid4())
            new_user = {
                'user_id': user_id,
                'username': user_data['username'],
                'email': user_data['email'],
                'password_hash': self._hash_password(user_data['password']),
                'role': user_data['role'],
                'status': UserStatus.ACTIVE.value,
                'full_name': user_data.get('full_name', ''),
                'tax_number': user_data.get('tax_number', ''),
                'created_at': datetime.utcnow().isoformat(),
                'created_by': admin_user_id,
                'last_login': None,
                'login_count': 0,
                'filings_count': 0,
                'total_tax_paid': 0.0
            }
            
            self.system_users[user_id] = new_user
            
            # Log action
            self._log_audit_action(
                user_id=admin_user_id,
                action=AuditAction.CREATE_USER,
                details={
                    'created_user_id': user_id,
                    'username': user_data['username'],
                    'role': user_data['role']
                }
            )
            
            # Return user without password hash
            safe_user = new_user.copy()
            safe_user.pop('password_hash')
            
            return {
                'success': True,
                'user': safe_user
            }
            
        except Exception as e:
            self.logger.error(f"Error creating user: {str(e)}")
            raise ValueError(f"User creation failed: {str(e)}")
    
    def update_user(self, user_id: str, user_data: Dict[str, Any], admin_user_id: str) -> Dict[str, Any]:
        """Update existing user"""
        try:
            if user_id not in self.system_users:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            user = self.system_users[user_id]
            
            # Update allowed fields
            updatable_fields = ['email', 'role', 'status', 'full_name', 'tax_number']
            updated_fields = []
            
            for field in updatable_fields:
                if field in user_data:
                    old_value = user.get(field)
                    new_value = user_data[field]
                    
                    if field == 'role':
                        try:
                            UserRole(new_value)
                        except ValueError:
                            return {
                                'success': False,
                                'error': 'Invalid role'
                            }
                    
                    if field == 'status':
                        try:
                            UserStatus(new_value)
                        except ValueError:
                            return {
                                'success': False,
                                'error': 'Invalid status'
                            }
                    
                    user[field] = new_value
                    updated_fields.append(f"{field}: {old_value} -> {new_value}")
            
            # Update password if provided
            if 'password' in user_data:
                user['password_hash'] = self._hash_password(user_data['password'])
                updated_fields.append("password: updated")
            
            user['updated_at'] = datetime.utcnow().isoformat()
            user['updated_by'] = admin_user_id
            
            # Log action
            self._log_audit_action(
                user_id=admin_user_id,
                action=AuditAction.UPDATE_USER,
                details={
                    'updated_user_id': user_id,
                    'username': user['username'],
                    'changes': updated_fields
                }
            )
            
            # Return user without password hash
            safe_user = user.copy()
            safe_user.pop('password_hash')
            
            return {
                'success': True,
                'user': safe_user
            }
            
        except Exception as e:
            self.logger.error(f"Error updating user: {str(e)}")
            raise ValueError(f"User update failed: {str(e)}")
    
    def delete_user(self, user_id: str, admin_user_id: str) -> Dict[str, Any]:
        """Delete user (soft delete by setting status to inactive)"""
        try:
            if user_id not in self.system_users:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            user = self.system_users[user_id]
            user['status'] = UserStatus.INACTIVE.value
            user['deleted_at'] = datetime.utcnow().isoformat()
            user['deleted_by'] = admin_user_id
            
            # Log action
            self._log_audit_action(
                user_id=admin_user_id,
                action=AuditAction.DELETE_USER,
                details={
                    'deleted_user_id': user_id,
                    'username': user['username']
                }
            )
            
            return {
                'success': True,
                'message': 'User deleted successfully'
            }
            
        except Exception as e:
            self.logger.error(f"Error deleting user: {str(e)}")
            raise ValueError(f"User deletion failed: {str(e)}")
    
    def get_audit_logs(self, page: int = 1, per_page: int = 50, action: str = None, user_id: str = None) -> Dict[str, Any]:
        """Get paginated audit logs"""
        try:
            logs = self.audit_logs.copy()
            
            # Apply filters
            if action:
                logs = [log for log in logs if log['action'] == action]
            if user_id:
                logs = [log for log in logs if log['user_id'] == user_id]
            
            # Sort by timestamp (newest first)
            logs = sorted(logs, key=lambda log: log['timestamp'], reverse=True)
            
            # Pagination
            total_logs = len(logs)
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            paginated_logs = logs[start_idx:end_idx]
            
            return {
                'success': True,
                'audit_logs': paginated_logs,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total_logs,
                    'pages': (total_logs + per_page - 1) // per_page
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting audit logs: {str(e)}")
            raise ValueError(f"Audit log retrieval failed: {str(e)}")
    
    def _log_audit_action(self, user_id: str, action: AuditAction, details: Dict[str, Any] = None):
        """Log audit action"""
        try:
            audit_log = {
                'log_id': str(uuid.uuid4()),
                'user_id': user_id,
                'action': action.value,
                'timestamp': datetime.utcnow().isoformat(),
                'details': details or {},
                'ip_address': '127.0.0.1',  # Simplified for development
                'user_agent': 'Malta Tax AI Agent'
            }
            
            self.audit_logs.append(audit_log)
            
            # Keep only last 1000 logs in memory
            if len(self.audit_logs) > 1000:
                self.audit_logs = self.audit_logs[-1000:]
                
        except Exception as e:
            self.logger.error(f"Error logging audit action: {str(e)}")
    
    def get_system_config(self) -> Dict[str, Any]:
        """Get system configuration"""
        return {
            'success': True,
            'config': self.system_config
        }
    
    def update_system_config(self, config_data: Dict[str, Any], admin_user_id: str) -> Dict[str, Any]:
        """Update system configuration"""
        try:
            # Update configuration
            for key, value in config_data.items():
                if key in self.system_config:
                    self.system_config[key] = value
            
            # Log action
            self._log_audit_action(
                user_id=admin_user_id,
                action=AuditAction.SYSTEM_CONFIG_CHANGED,
                details={'updated_keys': list(config_data.keys())}
            )
            
            return {
                'success': True,
                'config': self.system_config
            }
            
        except Exception as e:
            self.logger.error(f"Error updating system config: {str(e)}")
            raise ValueError(f"System config update failed: {str(e)}")
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get system health status"""
        # Update health check timestamp
        self.system_health['last_check'] = datetime.utcnow().isoformat()
        
        return {
            'success': True,
            'health': self.system_health
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        return {
            'success': True,
            'metrics': self.performance_metrics
        }

