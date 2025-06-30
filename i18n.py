"""
Internationalization (i18n) API Routes
Multilingual support and localization for Malta Tax AI Agent
"""

from flask import Blueprint, request, jsonify
from ..services.i18n_service import I18nService

i18n_bp = Blueprint('i18n', __name__)
i18n_service = I18nService()

@i18n_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for i18n service"""
    return jsonify({
        'status': 'healthy',
        'service': 'i18n',
        'version': '1.0.0'
    })

@i18n_bp.route('/languages', methods=['GET'])
def get_supported_languages():
    """Get all supported languages"""
    try:
        result = i18n_service.get_supported_languages()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@i18n_bp.route('/languages/<language_code>', methods=['GET'])
def get_language_config(language_code):
    """Get configuration for a specific language"""
    try:
        result = i18n_service.get_language_config(language_code)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@i18n_bp.route('/translations/<language_code>', methods=['GET'])
def get_translations(language_code):
    """Get translations for a language"""
    try:
        category = request.args.get('category')
        
        result = i18n_service.get_translations(language_code, category)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@i18n_bp.route('/translations/<language_code>/<key>', methods=['GET'])
def get_translation(language_code, key):
    """Get a specific translation"""
    try:
        category = request.args.get('category')
        
        result = i18n_service.get_translation(language_code, key, category)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@i18n_bp.route('/translations/<language_code>/<key>', methods=['POST'])
def add_translation(language_code, key):
    """Add or update a translation"""
    try:
        data = request.get_json()
        
        if not data or 'value' not in data:
            return jsonify({
                'success': False,
                'error': 'Translation value is required'
            }), 400
        
        category = data.get('category', 'custom')
        
        result = i18n_service.add_translation(language_code, key, data['value'], category)
        
        return jsonify(result), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@i18n_bp.route('/detect-language', methods=['POST'])
def detect_language():
    """Detect language from text"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': 'Text is required for language detection'
            }), 400
        
        result = i18n_service.detect_language(data['text'])
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@i18n_bp.route('/users/<user_id>/language', methods=['GET'])
def get_user_language_preference(user_id):
    """Get language preference for a user"""
    try:
        result = i18n_service.get_user_language_preference(user_id)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@i18n_bp.route('/users/<user_id>/language', methods=['POST'])
def set_user_language_preference(user_id):
    """Set language preference for a user"""
    try:
        data = request.get_json()
        
        if not data or 'language' not in data:
            return jsonify({
                'success': False,
                'error': 'Language code is required'
            }), 400
        
        result = i18n_service.set_user_language_preference(user_id, data['language'])
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@i18n_bp.route('/format/number', methods=['POST'])
def format_number():
    """Format a number according to language locale"""
    try:
        data = request.get_json()
        
        if not data or 'number' not in data or 'language' not in data:
            return jsonify({
                'success': False,
                'error': 'Number and language are required'
            }), 400
        
        result = i18n_service.format_number(data['number'], data['language'])
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@i18n_bp.route('/format/currency', methods=['POST'])
def format_currency():
    """Format currency according to language locale"""
    try:
        data = request.get_json()
        
        if not data or 'amount' not in data or 'language' not in data:
            return jsonify({
                'success': False,
                'error': 'Amount and language are required'
            }), 400
        
        currency = data.get('currency', 'EUR')
        
        result = i18n_service.format_currency(data['amount'], data['language'], currency)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@i18n_bp.route('/format/date', methods=['POST'])
def format_date():
    """Format date according to language locale"""
    try:
        data = request.get_json()
        
        if not data or 'date' not in data or 'language' not in data:
            return jsonify({
                'success': False,
                'error': 'Date and language are required'
            }), 400
        
        result = i18n_service.format_date(data['date'], data['language'])
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@i18n_bp.route('/completeness', methods=['GET'])
def get_translation_completeness():
    """Get translation completeness statistics"""
    try:
        result = i18n_service.get_translation_completeness()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@i18n_bp.route('/bulk-translate', methods=['POST'])
def bulk_translate():
    """Translate multiple keys at once"""
    try:
        data = request.get_json()
        
        if not data or 'keys' not in data or 'language' not in data:
            return jsonify({
                'success': False,
                'error': 'Keys and language are required'
            }), 400
        
        keys = data['keys']
        language = data['language']
        category = data.get('category')
        
        translations = {}
        
        for key in keys:
            result = i18n_service.get_translation(language, key, category)
            translations[key] = result.get('translation', key)
        
        return jsonify({
            'success': True,
            'translations': translations,
            'language': language,
            'total_keys': len(keys)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@i18n_bp.route('/categories', methods=['GET'])
def get_translation_categories():
    """Get available translation categories"""
    try:
        # Get categories from English translations (base language)
        result = i18n_service.get_translations('en')
        
        if result['success']:
            categories = list(result['translations'].keys())
            return jsonify({
                'success': True,
                'categories': categories,
                'total_count': len(categories)
            })
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@i18n_bp.route('/export/<language_code>', methods=['GET'])
def export_translations(language_code):
    """Export translations for a language"""
    try:
        format_type = request.args.get('format', 'json')
        category = request.args.get('category')
        
        result = i18n_service.get_translations(language_code, category)
        
        if not result['success']:
            return jsonify(result), 404
        
        if format_type == 'json':
            return jsonify({
                'success': True,
                'language': language_code,
                'category': category,
                'translations': result['translations'],
                'exported_at': datetime.utcnow().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Export format {format_type} not supported'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@i18n_bp.route('/import/<language_code>', methods=['POST'])
def import_translations(language_code):
    """Import translations for a language"""
    try:
        data = request.get_json()
        
        if not data or 'translations' not in data:
            return jsonify({
                'success': False,
                'error': 'Translations data is required'
            }), 400
        
        translations = data['translations']
        category = data.get('category', 'imported')
        
        imported_count = 0
        errors = []
        
        # Handle nested translations (category -> key -> value)
        if isinstance(translations, dict):
            for cat_name, cat_translations in translations.items():
                if isinstance(cat_translations, dict):
                    for key, value in cat_translations.items():
                        try:
                            result = i18n_service.add_translation(language_code, key, value, cat_name)
                            if result['success']:
                                imported_count += 1
                            else:
                                errors.append(f"Failed to import {cat_name}.{key}: {result.get('error', 'Unknown error')}")
                        except Exception as e:
                            errors.append(f"Error importing {cat_name}.{key}: {str(e)}")
                else:
                    # Direct key-value pairs
                    try:
                        result = i18n_service.add_translation(language_code, cat_name, cat_translations, category)
                        if result['success']:
                            imported_count += 1
                        else:
                            errors.append(f"Failed to import {cat_name}: {result.get('error', 'Unknown error')}")
                    except Exception as e:
                        errors.append(f"Error importing {cat_name}: {str(e)}")
        
        return jsonify({
            'success': True,
            'imported_count': imported_count,
            'errors': errors,
            'language': language_code,
            'category': category
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

