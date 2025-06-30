"""
White-Label Branding Service for Malta Tax AI Agent
Dynamic branding and customization capabilities
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid
from enum import Enum
import base64

class BrandingTheme(Enum):
    LIGHT = "light"
    DARK = "dark"
    CUSTOM = "custom"

class ComponentType(Enum):
    HEADER = "header"
    SIDEBAR = "sidebar"
    FOOTER = "footer"
    DASHBOARD = "dashboard"
    FORMS = "forms"
    BUTTONS = "buttons"
    CARDS = "cards"

class BrandingService:
    """White-label branding service for Malta Tax AI Agent"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Branding configurations storage
        self.brand_configs = {}
        self.theme_templates = {}
        self.custom_assets = {}
        self.tenant_brands = {}
        
        # Initialize default branding
        self._initialize_default_branding()
        self._initialize_theme_templates()
    
    def _initialize_default_branding(self):
        """Initialize default branding configuration"""
        self.default_brand = {
            'brand_id': 'default',
            'organization_name': 'Malta Tax AI Agent',
            'logo_url': '/assets/logo-default.png',
            'favicon_url': '/assets/favicon-default.ico',
            'primary_color': '#2563eb',
            'secondary_color': '#64748b',
            'accent_color': '#f59e0b',
            'background_color': '#ffffff',
            'text_color': '#1f2937',
            'theme': BrandingTheme.LIGHT.value,
            'font_family': 'Inter, system-ui, sans-serif',
            'border_radius': '8px',
            'shadow_style': '0 1px 3px 0 rgb(0 0 0 / 0.1)',
            'custom_css': '',
            'footer_text': '© 2025 Malta Tax AI Agent. All rights reserved.',
            'contact_email': 'support@maltataxai.com',
            'support_url': 'https://maltataxai.com/support',
            'privacy_url': 'https://maltataxai.com/privacy',
            'terms_url': 'https://maltataxai.com/terms',
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        self.brand_configs['default'] = self.default_brand
    
    def _initialize_theme_templates(self):
        """Initialize predefined theme templates"""
        self.theme_templates = {
            'professional_blue': {
                'name': 'Professional Blue',
                'description': 'Clean and professional blue theme',
                'primary_color': '#2563eb',
                'secondary_color': '#64748b',
                'accent_color': '#3b82f6',
                'background_color': '#ffffff',
                'text_color': '#1f2937',
                'theme': BrandingTheme.LIGHT.value
            },
            'corporate_gray': {
                'name': 'Corporate Gray',
                'description': 'Sophisticated gray corporate theme',
                'primary_color': '#374151',
                'secondary_color': '#6b7280',
                'accent_color': '#f59e0b',
                'background_color': '#f9fafb',
                'text_color': '#111827',
                'theme': BrandingTheme.LIGHT.value
            },
            'modern_dark': {
                'name': 'Modern Dark',
                'description': 'Sleek modern dark theme',
                'primary_color': '#3b82f6',
                'secondary_color': '#64748b',
                'accent_color': '#10b981',
                'background_color': '#1f2937',
                'text_color': '#f9fafb',
                'theme': BrandingTheme.DARK.value
            },
            'malta_government': {
                'name': 'Malta Government',
                'description': 'Official Malta government styling',
                'primary_color': '#dc2626',
                'secondary_color': '#991b1b',
                'accent_color': '#fbbf24',
                'background_color': '#ffffff',
                'text_color': '#1f2937',
                'theme': BrandingTheme.LIGHT.value
            },
            'financial_green': {
                'name': 'Financial Green',
                'description': 'Trust-inspiring green financial theme',
                'primary_color': '#059669',
                'secondary_color': '#047857',
                'accent_color': '#10b981',
                'background_color': '#f0fdf4',
                'text_color': '#064e3b',
                'theme': BrandingTheme.LIGHT.value
            }
        }
    
    def create_brand_config(self, brand_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new brand configuration"""
        try:
            # Generate brand ID
            brand_id = brand_data.get('brand_id', str(uuid.uuid4()))
            
            # Validate required fields
            required_fields = ['organization_name']
            for field in required_fields:
                if field not in brand_data:
                    return {
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }
            
            # Create brand configuration
            brand_config = {
                'brand_id': brand_id,
                'organization_name': brand_data['organization_name'],
                'logo_url': brand_data.get('logo_url', self.default_brand['logo_url']),
                'favicon_url': brand_data.get('favicon_url', self.default_brand['favicon_url']),
                'primary_color': brand_data.get('primary_color', self.default_brand['primary_color']),
                'secondary_color': brand_data.get('secondary_color', self.default_brand['secondary_color']),
                'accent_color': brand_data.get('accent_color', self.default_brand['accent_color']),
                'background_color': brand_data.get('background_color', self.default_brand['background_color']),
                'text_color': brand_data.get('text_color', self.default_brand['text_color']),
                'theme': brand_data.get('theme', BrandingTheme.LIGHT.value),
                'font_family': brand_data.get('font_family', self.default_brand['font_family']),
                'border_radius': brand_data.get('border_radius', self.default_brand['border_radius']),
                'shadow_style': brand_data.get('shadow_style', self.default_brand['shadow_style']),
                'custom_css': brand_data.get('custom_css', ''),
                'footer_text': brand_data.get('footer_text', f"© 2025 {brand_data['organization_name']}. All rights reserved."),
                'contact_email': brand_data.get('contact_email', self.default_brand['contact_email']),
                'support_url': brand_data.get('support_url', self.default_brand['support_url']),
                'privacy_url': brand_data.get('privacy_url', self.default_brand['privacy_url']),
                'terms_url': brand_data.get('terms_url', self.default_brand['terms_url']),
                'tenant_id': brand_data.get('tenant_id'),
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'created_by': brand_data.get('user_id', 'system')
            }
            
            # Store brand configuration
            self.brand_configs[brand_id] = brand_config
            
            # Associate with tenant if specified
            if brand_config['tenant_id']:
                self.tenant_brands[brand_config['tenant_id']] = brand_id
            
            return {
                'success': True,
                'brand_id': brand_id,
                'brand_config': brand_config
            }
            
        except Exception as e:
            self.logger.error(f"Error creating brand config: {str(e)}")
            raise ValueError(f"Brand config creation failed: {str(e)}")
    
    def get_brand_config(self, brand_id: str) -> Dict[str, Any]:
        """Get brand configuration by ID"""
        try:
            if brand_id not in self.brand_configs:
                return {
                    'success': False,
                    'error': 'Brand configuration not found'
                }
            
            brand_config = self.brand_configs[brand_id]
            
            return {
                'success': True,
                'brand_config': brand_config
            }
            
        except Exception as e:
            self.logger.error(f"Error getting brand config: {str(e)}")
            raise ValueError(f"Brand config retrieval failed: {str(e)}")
    
    def update_brand_config(self, brand_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update brand configuration"""
        try:
            if brand_id not in self.brand_configs:
                return {
                    'success': False,
                    'error': 'Brand configuration not found'
                }
            
            # Get current configuration
            brand_config = self.brand_configs[brand_id].copy()
            
            # Apply updates
            for key, value in updates.items():
                if key in brand_config and key not in ['brand_id', 'created_at', 'created_by']:
                    brand_config[key] = value
            
            # Update timestamp
            brand_config['updated_at'] = datetime.utcnow().isoformat()
            brand_config['updated_by'] = updates.get('user_id', 'system')
            
            # Store updated configuration
            self.brand_configs[brand_id] = brand_config
            
            return {
                'success': True,
                'brand_config': brand_config
            }
            
        except Exception as e:
            self.logger.error(f"Error updating brand config: {str(e)}")
            raise ValueError(f"Brand config update failed: {str(e)}")
    
    def get_brand_configs(self, tenant_id: str = None) -> Dict[str, Any]:
        """Get all brand configurations, optionally filtered by tenant"""
        try:
            if tenant_id:
                # Filter by tenant
                tenant_configs = {}
                for brand_id, config in self.brand_configs.items():
                    if config.get('tenant_id') == tenant_id:
                        tenant_configs[brand_id] = config
                
                return {
                    'success': True,
                    'brand_configs': tenant_configs,
                    'total_count': len(tenant_configs)
                }
            else:
                return {
                    'success': True,
                    'brand_configs': self.brand_configs,
                    'total_count': len(self.brand_configs)
                }
            
        except Exception as e:
            self.logger.error(f"Error getting brand configs: {str(e)}")
            raise ValueError(f"Brand configs retrieval failed: {str(e)}")
    
    def get_theme_templates(self) -> Dict[str, Any]:
        """Get available theme templates"""
        try:
            return {
                'success': True,
                'theme_templates': self.theme_templates
            }
            
        except Exception as e:
            self.logger.error(f"Error getting theme templates: {str(e)}")
            raise ValueError(f"Theme templates retrieval failed: {str(e)}")
    
    def apply_theme_template(self, brand_id: str, template_id: str) -> Dict[str, Any]:
        """Apply a theme template to a brand configuration"""
        try:
            if brand_id not in self.brand_configs:
                return {
                    'success': False,
                    'error': 'Brand configuration not found'
                }
            
            if template_id not in self.theme_templates:
                return {
                    'success': False,
                    'error': 'Theme template not found'
                }
            
            # Get current brand config and template
            brand_config = self.brand_configs[brand_id].copy()
            template = self.theme_templates[template_id]
            
            # Apply template colors and theme
            brand_config.update({
                'primary_color': template['primary_color'],
                'secondary_color': template['secondary_color'],
                'accent_color': template['accent_color'],
                'background_color': template['background_color'],
                'text_color': template['text_color'],
                'theme': template['theme'],
                'updated_at': datetime.utcnow().isoformat()
            })
            
            # Store updated configuration
            self.brand_configs[brand_id] = brand_config
            
            return {
                'success': True,
                'brand_config': brand_config,
                'applied_template': template_id
            }
            
        except Exception as e:
            self.logger.error(f"Error applying theme template: {str(e)}")
            raise ValueError(f"Theme template application failed: {str(e)}")
    
    def upload_brand_asset(self, brand_id: str, asset_type: str, asset_data: str) -> Dict[str, Any]:
        """Upload a brand asset (logo, favicon, etc.)"""
        try:
            if brand_id not in self.brand_configs:
                return {
                    'success': False,
                    'error': 'Brand configuration not found'
                }
            
            # Validate asset type
            valid_asset_types = ['logo', 'favicon', 'background', 'watermark']
            if asset_type not in valid_asset_types:
                return {
                    'success': False,
                    'error': f'Invalid asset type. Must be one of: {valid_asset_types}'
                }
            
            # Generate asset ID and file path
            asset_id = str(uuid.uuid4())
            file_extension = self._get_file_extension_from_data(asset_data)
            file_path = f'/assets/brands/{brand_id}/{asset_type}_{asset_id}.{file_extension}'
            
            # Store asset information
            asset_info = {
                'asset_id': asset_id,
                'brand_id': brand_id,
                'asset_type': asset_type,
                'file_path': file_path,
                'uploaded_at': datetime.utcnow().isoformat(),
                'file_size': len(asset_data),
                'mime_type': self._get_mime_type_from_data(asset_data)
            }
            
            # Store asset data (in production, this would be saved to file system or cloud storage)
            if brand_id not in self.custom_assets:
                self.custom_assets[brand_id] = {}
            self.custom_assets[brand_id][asset_id] = {
                'info': asset_info,
                'data': asset_data
            }
            
            # Update brand configuration with new asset URL
            brand_config = self.brand_configs[brand_id]
            if asset_type == 'logo':
                brand_config['logo_url'] = file_path
            elif asset_type == 'favicon':
                brand_config['favicon_url'] = file_path
            
            brand_config['updated_at'] = datetime.utcnow().isoformat()
            
            return {
                'success': True,
                'asset_info': asset_info,
                'file_path': file_path
            }
            
        except Exception as e:
            self.logger.error(f"Error uploading brand asset: {str(e)}")
            raise ValueError(f"Brand asset upload failed: {str(e)}")
    
    def _get_file_extension_from_data(self, data: str) -> str:
        """Get file extension from base64 data"""
        # Simple detection based on data prefix
        if data.startswith('data:image/png'):
            return 'png'
        elif data.startswith('data:image/jpeg') or data.startswith('data:image/jpg'):
            return 'jpg'
        elif data.startswith('data:image/svg'):
            return 'svg'
        elif data.startswith('data:image/gif'):
            return 'gif'
        else:
            return 'png'  # Default
    
    def _get_mime_type_from_data(self, data: str) -> str:
        """Get MIME type from base64 data"""
        if data.startswith('data:'):
            return data.split(';')[0].replace('data:', '')
        return 'image/png'  # Default
    
    def generate_css_variables(self, brand_id: str) -> Dict[str, Any]:
        """Generate CSS variables for a brand configuration"""
        try:
            if brand_id not in self.brand_configs:
                return {
                    'success': False,
                    'error': 'Brand configuration not found'
                }
            
            brand_config = self.brand_configs[brand_id]
            
            # Generate CSS variables
            css_variables = f"""
:root {{
  --brand-primary-color: {brand_config['primary_color']};
  --brand-secondary-color: {brand_config['secondary_color']};
  --brand-accent-color: {brand_config['accent_color']};
  --brand-background-color: {brand_config['background_color']};
  --brand-text-color: {brand_config['text_color']};
  --brand-font-family: {brand_config['font_family']};
  --brand-border-radius: {brand_config['border_radius']};
  --brand-shadow-style: {brand_config['shadow_style']};
}}

.brand-theme {{
  color: var(--brand-text-color);
  background-color: var(--brand-background-color);
  font-family: var(--brand-font-family);
}}

.brand-primary {{
  background-color: var(--brand-primary-color);
  color: white;
}}

.brand-secondary {{
  background-color: var(--brand-secondary-color);
  color: white;
}}

.brand-accent {{
  background-color: var(--brand-accent-color);
  color: white;
}}

.brand-button {{
  background-color: var(--brand-primary-color);
  color: white;
  border-radius: var(--brand-border-radius);
  box-shadow: var(--brand-shadow-style);
  border: none;
  padding: 0.5rem 1rem;
  font-family: var(--brand-font-family);
  cursor: pointer;
  transition: all 0.2s ease;
}}

.brand-button:hover {{
  background-color: var(--brand-secondary-color);
}}

.brand-card {{
  background-color: var(--brand-background-color);
  border-radius: var(--brand-border-radius);
  box-shadow: var(--brand-shadow-style);
  padding: 1rem;
  border: 1px solid var(--brand-secondary-color);
}}

{brand_config['custom_css']}
"""
            
            return {
                'success': True,
                'css_variables': css_variables,
                'brand_id': brand_id
            }
            
        except Exception as e:
            self.logger.error(f"Error generating CSS variables: {str(e)}")
            raise ValueError(f"CSS variables generation failed: {str(e)}")
    
    def get_brand_by_tenant(self, tenant_id: str) -> Dict[str, Any]:
        """Get brand configuration for a specific tenant"""
        try:
            if tenant_id in self.tenant_brands:
                brand_id = self.tenant_brands[tenant_id]
                return self.get_brand_config(brand_id)
            else:
                # Return default brand if no specific brand is configured
                return self.get_brand_config('default')
            
        except Exception as e:
            self.logger.error(f"Error getting brand by tenant: {str(e)}")
            raise ValueError(f"Brand retrieval by tenant failed: {str(e)}")
    
    def delete_brand_config(self, brand_id: str) -> Dict[str, Any]:
        """Delete a brand configuration"""
        try:
            if brand_id == 'default':
                return {
                    'success': False,
                    'error': 'Cannot delete default brand configuration'
                }
            
            if brand_id not in self.brand_configs:
                return {
                    'success': False,
                    'error': 'Brand configuration not found'
                }
            
            # Remove brand configuration
            del self.brand_configs[brand_id]
            
            # Remove tenant association if exists
            tenant_to_remove = None
            for tenant_id, associated_brand_id in self.tenant_brands.items():
                if associated_brand_id == brand_id:
                    tenant_to_remove = tenant_id
                    break
            
            if tenant_to_remove:
                del self.tenant_brands[tenant_to_remove]
            
            # Remove custom assets
            if brand_id in self.custom_assets:
                del self.custom_assets[brand_id]
            
            return {
                'success': True,
                'message': 'Brand configuration deleted successfully'
            }
            
        except Exception as e:
            self.logger.error(f"Error deleting brand config: {str(e)}")
            raise ValueError(f"Brand config deletion failed: {str(e)}")
    
    def preview_brand_config(self, brand_data: Dict[str, Any]) -> Dict[str, Any]:
        """Preview a brand configuration without saving it"""
        try:
            # Create temporary brand configuration
            temp_brand = {
                'brand_id': 'preview',
                'organization_name': brand_data.get('organization_name', 'Preview Organization'),
                'primary_color': brand_data.get('primary_color', self.default_brand['primary_color']),
                'secondary_color': brand_data.get('secondary_color', self.default_brand['secondary_color']),
                'accent_color': brand_data.get('accent_color', self.default_brand['accent_color']),
                'background_color': brand_data.get('background_color', self.default_brand['background_color']),
                'text_color': brand_data.get('text_color', self.default_brand['text_color']),
                'theme': brand_data.get('theme', BrandingTheme.LIGHT.value),
                'font_family': brand_data.get('font_family', self.default_brand['font_family']),
                'border_radius': brand_data.get('border_radius', self.default_brand['border_radius']),
                'shadow_style': brand_data.get('shadow_style', self.default_brand['shadow_style']),
                'custom_css': brand_data.get('custom_css', '')
            }
            
            # Temporarily store for CSS generation
            self.brand_configs['preview'] = temp_brand
            
            # Generate CSS variables
            css_result = self.generate_css_variables('preview')
            
            # Remove temporary configuration
            del self.brand_configs['preview']
            
            return {
                'success': True,
                'preview_config': temp_brand,
                'css_variables': css_result.get('css_variables', '') if css_result['success'] else ''
            }
            
        except Exception as e:
            self.logger.error(f"Error previewing brand config: {str(e)}")
            raise ValueError(f"Brand config preview failed: {str(e)}")

