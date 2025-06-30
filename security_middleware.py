"""
Security middleware for Malta Tax AI Backend
Implements security hardening measures and protection against common vulnerabilities
"""

from flask import Flask, request, jsonify, g
from functools import wraps
import re
import time
import hashlib
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import ipaddress


class SecurityMiddleware:
    """Security middleware for Flask application"""
    
    def __init__(self, app: Flask = None):
        self.app = app
        self.rate_limit_storage = {}
        self.blocked_ips = set()
        self.security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize security middleware with Flask app"""
        self.app = app
        
        # Register security handlers
        app.before_request(self.before_request_security)
        app.after_request(self.after_request_security)
        
        # Register error handlers
        app.errorhandler(400)(self.handle_bad_request)
        app.errorhandler(403)(self.handle_forbidden)
        app.errorhandler(429)(self.handle_rate_limit)
        app.errorhandler(500)(self.handle_internal_error)
    
    def before_request_security(self):
        """Security checks before processing request"""
        # Check for blocked IPs
        client_ip = self.get_client_ip()
        if client_ip in self.blocked_ips:
            return jsonify({"error": "Access denied"}), 403
        
        # Rate limiting
        if self.is_rate_limited(client_ip):
            return jsonify({"error": "Rate limit exceeded"}), 429
        
        # Input validation
        if request.method in ['POST', 'PUT', 'PATCH']:
            if not self.validate_request_data():
                return jsonify({"error": "Invalid request data"}), 400
        
        # SQL injection protection
        if not self.check_sql_injection():
            logging.warning(f"SQL injection attempt from {client_ip}")
            return jsonify({"error": "Invalid request"}), 400
        
        # XSS protection
        if not self.check_xss_protection():
            logging.warning(f"XSS attempt from {client_ip}")
            return jsonify({"error": "Invalid request"}), 400
    
    def after_request_security(self, response):
        """Add security headers to response"""
        for header, value in self.security_headers.items():
            response.headers[header] = value
        
        # Remove sensitive headers
        response.headers.pop('Server', None)
        response.headers.pop('X-Powered-By', None)
        
        return response
    
    def get_client_ip(self) -> str:
        """Get client IP address"""
        # Check for forwarded headers
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        else:
            return request.remote_addr or '127.0.0.1'
    
    def is_rate_limited(self, client_ip: str) -> bool:
        """Check if client is rate limited"""
        current_time = time.time()
        window_size = 60  # 1 minute window
        max_requests = 100  # 100 requests per minute
        
        # Clean old entries
        self.rate_limit_storage = {
            ip: requests for ip, requests in self.rate_limit_storage.items()
            if any(timestamp > current_time - window_size for timestamp in requests)
        }
        
        # Get client's request history
        if client_ip not in self.rate_limit_storage:
            self.rate_limit_storage[client_ip] = []
        
        # Filter recent requests
        recent_requests = [
            timestamp for timestamp in self.rate_limit_storage[client_ip]
            if timestamp > current_time - window_size
        ]
        
        # Check rate limit
        if len(recent_requests) >= max_requests:
            return True
        
        # Add current request
        recent_requests.append(current_time)
        self.rate_limit_storage[client_ip] = recent_requests
        
        return False
    
    def validate_request_data(self) -> bool:
        """Validate request data for security issues"""
        try:
            if request.is_json:
                data = request.get_json()
                if data:
                    return self.validate_json_data(data)
            
            # Validate form data
            for key, value in request.form.items():
                if not self.validate_input_field(key, value):
                    return False
            
            # Validate query parameters
            for key, value in request.args.items():
                if not self.validate_input_field(key, value):
                    return False
            
            return True
            
        except Exception as e:
            logging.error(f"Error validating request data: {e}")
            return False
    
    def validate_json_data(self, data: Any) -> bool:
        """Validate JSON data recursively"""
        if isinstance(data, dict):
            for key, value in data.items():
                if not self.validate_input_field(str(key), str(value)):
                    return False
                if isinstance(value, (dict, list)):
                    if not self.validate_json_data(value):
                        return False
        elif isinstance(data, list):
            for item in data:
                if not self.validate_json_data(item):
                    return False
        else:
            if not self.validate_input_field("value", str(data)):
                return False
        
        return True
    
    def validate_input_field(self, key: str, value: str) -> bool:
        """Validate individual input field"""
        # Check for null bytes
        if '\x00' in value:
            return False
        
        # Check for excessive length
        if len(value) > 10000:
            return False
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'onload\s*=',
            r'onerror\s*=',
            r'onfocus\s*=',
            r'onmouseover\s*=',
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return False
        
        return True
    
    def check_sql_injection(self) -> bool:
        """Check for SQL injection attempts"""
        sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
            r"(\b(OR|AND)\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?)",
            r"(--|#|/\*|\*/)",
            r"(\bUNION\b.*\bSELECT\b)",
            r"(\bDROP\b.*\bTABLE\b)",
            r"(\bINSERT\b.*\bINTO\b)",
            r"(\bEXEC\b.*\bxp_cmdshell\b)"
        ]
        
        # Check all input sources
        all_inputs = []
        
        # Query parameters
        all_inputs.extend(request.args.values())
        
        # Form data
        all_inputs.extend(request.form.values())
        
        # JSON data
        if request.is_json:
            json_data = request.get_json()
            if json_data:
                all_inputs.extend(self.extract_json_values(json_data))
        
        # Check each input
        for input_value in all_inputs:
            input_str = str(input_value)
            for pattern in sql_patterns:
                if re.search(pattern, input_str, re.IGNORECASE):
                    return False
        
        return True
    
    def check_xss_protection(self) -> bool:
        """Check for XSS attempts"""
        xss_patterns = [
            r'<script[^>]*>.*?</script>',
            r'<iframe[^>]*>.*?</iframe>',
            r'<object[^>]*>.*?</object>',
            r'<embed[^>]*>.*?</embed>',
            r'<link[^>]*>',
            r'<meta[^>]*>',
            r'javascript:',
            r'vbscript:',
            r'data:text/html',
            r'on\w+\s*=',
        ]
        
        # Check all input sources
        all_inputs = []
        
        # Query parameters
        all_inputs.extend(request.args.values())
        
        # Form data
        all_inputs.extend(request.form.values())
        
        # JSON data
        if request.is_json:
            json_data = request.get_json()
            if json_data:
                all_inputs.extend(self.extract_json_values(json_data))
        
        # Check each input
        for input_value in all_inputs:
            input_str = str(input_value)
            for pattern in xss_patterns:
                if re.search(pattern, input_str, re.IGNORECASE):
                    return False
        
        return True
    
    def extract_json_values(self, data: Any) -> List[str]:
        """Extract all string values from JSON data"""
        values = []
        
        if isinstance(data, dict):
            for value in data.values():
                if isinstance(value, str):
                    values.append(value)
                elif isinstance(value, (dict, list)):
                    values.extend(self.extract_json_values(value))
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, str):
                    values.append(item)
                elif isinstance(item, (dict, list)):
                    values.extend(self.extract_json_values(item))
        elif isinstance(data, str):
            values.append(data)
        
        return values
    
    def handle_bad_request(self, error):
        """Handle 400 Bad Request errors"""
        return jsonify({
            "error": "Bad request",
            "message": "The request could not be processed due to invalid data"
        }), 400
    
    def handle_forbidden(self, error):
        """Handle 403 Forbidden errors"""
        return jsonify({
            "error": "Access denied",
            "message": "You do not have permission to access this resource"
        }), 403
    
    def handle_rate_limit(self, error):
        """Handle 429 Rate Limit errors"""
        return jsonify({
            "error": "Rate limit exceeded",
            "message": "Too many requests. Please try again later."
        }), 429
    
    def handle_internal_error(self, error):
        """Handle 500 Internal Server errors"""
        # Log the error but don't expose details
        logging.error(f"Internal server error: {error}")
        
        return jsonify({
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later."
        }), 500
    
    def block_ip(self, ip_address: str):
        """Block an IP address"""
        self.blocked_ips.add(ip_address)
        logging.warning(f"Blocked IP address: {ip_address}")
    
    def unblock_ip(self, ip_address: str):
        """Unblock an IP address"""
        self.blocked_ips.discard(ip_address)
        logging.info(f"Unblocked IP address: {ip_address}")


def require_auth(f):
    """Decorator for endpoints that require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for API key or token
        api_key = request.headers.get('X-API-Key')
        auth_header = request.headers.get('Authorization')
        
        if not api_key and not auth_header:
            return jsonify({"error": "Authentication required"}), 401
        
        # Validate API key or token
        if api_key:
            if not validate_api_key(api_key):
                return jsonify({"error": "Invalid API key"}), 401
        
        if auth_header:
            if not validate_auth_token(auth_header):
                return jsonify({"error": "Invalid authentication token"}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function


def validate_api_key(api_key: str) -> bool:
    """Validate API key"""
    # In production, this would check against a database
    # For now, accept any non-empty key
    return bool(api_key and len(api_key) > 10)


def validate_auth_token(auth_header: str) -> bool:
    """Validate authentication token"""
    # In production, this would validate JWT tokens
    # For now, accept Bearer tokens
    return auth_header.startswith('Bearer ') and len(auth_header) > 20


def sanitize_input(data: Any) -> Any:
    """Sanitize input data"""
    if isinstance(data, str):
        # Remove null bytes
        data = data.replace('\x00', '')
        
        # Escape HTML entities
        data = data.replace('<', '&lt;').replace('>', '&gt;')
        data = data.replace('"', '&quot;').replace("'", '&#x27;')
        
        # Remove potentially dangerous characters
        data = re.sub(r'[^\w\s\-.,@+()€$%]', '', data)
        
        return data
    elif isinstance(data, dict):
        return {key: sanitize_input(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    else:
        return data


def log_security_event(event_type: str, details: Dict[str, Any]):
    """Log security events"""
    security_logger = logging.getLogger('security')
    
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,
        'client_ip': request.remote_addr if request else 'unknown',
        'user_agent': request.headers.get('User-Agent') if request else 'unknown',
        'details': details
    }
    
    security_logger.warning(f"Security event: {log_entry}")


# Security configuration
SECURITY_CONFIG = {
    'rate_limit': {
        'window_size': 60,  # seconds
        'max_requests': 100  # per window
    },
    'input_validation': {
        'max_length': 10000,
        'allow_html': False,
        'allow_scripts': False
    },
    'headers': {
        'force_https': True,
        'hsts_max_age': 31536000,
        'csp_policy': "default-src 'self'"
    }
}

