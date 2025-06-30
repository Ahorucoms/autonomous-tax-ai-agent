"""
White-Label Branding API Routes
Dynamic branding and customization capabilities for Malta Tax AI Agent
"""

from flask import Blueprint, request, jsonify
from ..services.branding_service import BrandingService

branding_bp = Blueprint('branding', __name__)
branding_service = BrandingService()

@branding_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for branding service"""
    return jsonify({
        'status': 'healthy',
        'service': 'branding',
        'version': '1.0.0'
    })

@branding_bp.route('/brands', methods=['POST'])
def create_brand():
    """Create a new brand configuration"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No brand data provided'
            }), 400
        
        # Add user ID from headers if available
        data['user_id'] = request.headers.get('X-User-ID', 'system')
        
        result = branding_service.create_brand_config(data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@branding_bp.route('/brands/<brand_id>', methods=['GET'])
def get_brand(brand_id):
    """Get a specific brand configuration"""
    try:
        result = branding_service.get_brand_config(brand_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@branding_bp.route('/brands/<brand_id>', methods=['PUT'])
def update_brand(brand_id):
    """Update a brand configuration"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No update data provided'
            }), 400
        
        # Add user ID from headers if available
        data['user_id'] = request.headers.get('X-User-ID', 'system')
        
        result = branding_service.update_brand_config(brand_id, data)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@branding_bp.route('/brands/<brand_id>', methods=['DELETE'])
def delete_brand(brand_id):
    """Delete a brand configuration"""
    try:
        result = branding_service.delete_brand_config(brand_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@branding_bp.route('/brands', methods=['GET'])
def get_brands():
    """Get all brand configurations"""
    try:
        tenant_id = request.args.get('tenant_id')
        
        result = branding_service.get_brand_configs(tenant_id=tenant_id)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@branding_bp.route('/themes', methods=['GET'])
def get_theme_templates():
    """Get available theme templates"""
    try:
        result = branding_service.get_theme_templates()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@branding_bp.route('/brands/<brand_id>/apply-theme', methods=['POST'])
def apply_theme_template(brand_id):
    """Apply a theme template to a brand configuration"""
    try:
        data = request.get_json()
        
        if not data or 'template_id' not in data:
            return jsonify({
                'success': False,
                'error': 'Template ID is required'
            }), 400
        
        result = branding_service.apply_theme_template(brand_id, data['template_id'])
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@branding_bp.route('/brands/<brand_id>/assets', methods=['POST'])
def upload_brand_asset(brand_id):
    """Upload a brand asset (logo, favicon, etc.)"""
    try:
        data = request.get_json()
        
        if not data or 'asset_type' not in data or 'asset_data' not in data:
            return jsonify({
                'success': False,
                'error': 'Asset type and data are required'
            }), 400
        
        result = branding_service.upload_brand_asset(
            brand_id, 
            data['asset_type'], 
            data['asset_data']
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@branding_bp.route('/brands/<brand_id>/css', methods=['GET'])
def generate_brand_css(brand_id):
    """Generate CSS variables for a brand configuration"""
    try:
        result = branding_service.generate_css_variables(brand_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@branding_bp.route('/tenants/<tenant_id>/brand', methods=['GET'])
def get_tenant_brand(tenant_id):
    """Get brand configuration for a specific tenant"""
    try:
        result = branding_service.get_brand_by_tenant(tenant_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@branding_bp.route('/preview', methods=['POST'])
def preview_brand():
    """Preview a brand configuration without saving it"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No brand data provided for preview'
            }), 400
        
        result = branding_service.preview_brand_config(data)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@branding_bp.route('/component-types', methods=['GET'])
def get_component_types():
    """Get available component types for customization"""
    try:
        from ..services.branding_service import ComponentType
        
        component_types = [
            {
                'value': ComponentType.HEADER.value,
                'label': 'Header',
                'description': 'Top navigation and branding area'
            },
            {
                'value': ComponentType.SIDEBAR.value,
                'label': 'Sidebar',
                'description': 'Side navigation menu'
            },
            {
                'value': ComponentType.FOOTER.value,
                'label': 'Footer',
                'description': 'Bottom page footer'
            },
            {
                'value': ComponentType.DASHBOARD.value,
                'label': 'Dashboard',
                'description': 'Main dashboard layout and widgets'
            },
            {
                'value': ComponentType.FORMS.value,
                'label': 'Forms',
                'description': 'Form inputs and validation styling'
            },
            {
                'value': ComponentType.BUTTONS.value,
                'label': 'Buttons',
                'description': 'Button styles and interactions'
            },
            {
                'value': ComponentType.CARDS.value,
                'label': 'Cards',
                'description': 'Card components and containers'
            }
        ]
        
        return jsonify({
            'success': True,
            'component_types': component_types
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@branding_bp.route('/default', methods=['GET'])
def get_default_brand():
    """Get the default brand configuration"""
    try:
        result = branding_service.get_brand_config('default')
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

