"""
Form Generation and Management API Routes
Handle Malta tax form creation, filling, validation, and submission
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import logging
from typing import Dict, Any

from ..services.form_generator import MaltaFormGenerator, FormType, FormStatus

forms_bp = Blueprint('forms', __name__)

# Initialize form generator
form_generator = MaltaFormGenerator()

@forms_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'forms',
        'timestamp': datetime.utcnow().isoformat()
    })

@forms_bp.route('/templates', methods=['GET'])
def get_form_templates():
    """Get all available form templates"""
    try:
        templates = form_generator.get_form_templates()
        
        return jsonify({
            'success': True,
            'templates': templates
        })
        
    except Exception as e:
        logging.error(f"Error getting form templates: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@forms_bp.route('/templates/<form_type>', methods=['GET'])
def get_form_template(form_type):
    """Get specific form template"""
    try:
        try:
            form_type_enum = FormType(form_type)
        except ValueError:
            return jsonify({'error': 'Invalid form type'}), 400
        
        template = form_generator.form_templates.get(form_type_enum)
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        
        return jsonify({
            'success': True,
            'template': template
        })
        
    except Exception as e:
        logging.error(f"Error getting form template: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@forms_bp.route('/create', methods=['POST'])
def create_form():
    """Create a new form instance"""
    try:
        data = request.get_json()
        
        if 'form_type' not in data:
            return jsonify({'error': 'Form type is required'}), 400
        
        if 'user_id' not in data:
            return jsonify({'error': 'User ID is required'}), 400
        
        try:
            form_type = FormType(data['form_type'])
        except ValueError:
            return jsonify({'error': 'Invalid form type'}), 400
        
        user_id = data['user_id']
        initial_data = data.get('data', {})
        
        form_id = form_generator.create_form(form_type, user_id, initial_data)
        
        return jsonify({
            'success': True,
            'form_id': form_id,
            'message': 'Form created successfully'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error creating form: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@forms_bp.route('/<form_id>', methods=['GET'])
def get_form(form_id):
    """Get form by ID"""
    try:
        form = form_generator.get_form(form_id)
        if not form:
            return jsonify({'error': 'Form not found'}), 404
        
        return jsonify({
            'success': True,
            'form': form
        })
        
    except Exception as e:
        logging.error(f"Error getting form: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@forms_bp.route('/<form_id>/update', methods=['PUT'])
def update_form(form_id):
    """Update form field data"""
    try:
        data = request.get_json()
        
        if 'field_updates' not in data:
            return jsonify({'error': 'Field updates are required'}), 400
        
        field_updates = data['field_updates']
        
        success = form_generator.update_form_data(form_id, field_updates)
        if not success:
            return jsonify({'error': 'Form not found or update failed'}), 404
        
        # Get updated form
        updated_form = form_generator.get_form(form_id)
        
        return jsonify({
            'success': True,
            'form': updated_form,
            'message': 'Form updated successfully'
        })
        
    except Exception as e:
        logging.error(f"Error updating form: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@forms_bp.route('/<form_id>/auto-fill', methods=['POST'])
def auto_fill_form(form_id):
    """Auto-fill form from extracted document data"""
    try:
        data = request.get_json()
        
        if 'extracted_data' not in data:
            return jsonify({'error': 'Extracted data is required'}), 400
        
        extracted_data = data['extracted_data']
        
        success = form_generator.auto_fill_form(form_id, extracted_data)
        if not success:
            return jsonify({'error': 'Form not found or auto-fill failed'}), 404
        
        # Get updated form
        updated_form = form_generator.get_form(form_id)
        
        return jsonify({
            'success': True,
            'form': updated_form,
            'message': 'Form auto-filled successfully'
        })
        
    except Exception as e:
        logging.error(f"Error auto-filling form: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@forms_bp.route('/<form_id>/validate', methods=['POST'])
def validate_form(form_id):
    """Validate form data"""
    try:
        form = form_generator.get_form(form_id)
        if not form:
            return jsonify({'error': 'Form not found'}), 404
        
        # Validation is automatically performed during updates
        # Just return current validation status
        
        is_valid = len(form['validation_errors']) == 0
        
        return jsonify({
            'success': True,
            'is_valid': is_valid,
            'validation_errors': form['validation_errors'],
            'status': form['status']
        })
        
    except Exception as e:
        logging.error(f"Error validating form: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@forms_bp.route('/<form_id>/generate-pdf', methods=['POST'])
def generate_form_pdf(form_id):
    """Generate PDF from completed form"""
    try:
        pdf_path = form_generator.generate_pdf(form_id)
        if not pdf_path:
            return jsonify({'error': 'Form not found or PDF generation failed'}), 404
        
        return jsonify({
            'success': True,
            'pdf_path': pdf_path,
            'message': 'PDF generated successfully'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error generating PDF: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@forms_bp.route('/<form_id>/submit', methods=['POST'])
def submit_form(form_id):
    """Submit form to tax authorities"""
    try:
        data = request.get_json() or {}
        submission_method = data.get('submission_method', 'electronic')
        
        success = form_generator.submit_form(form_id, submission_method)
        if not success:
            return jsonify({'error': 'Form not found or submission failed'}), 404
        
        # Get updated form with submission details
        updated_form = form_generator.get_form(form_id)
        
        return jsonify({
            'success': True,
            'form': updated_form,
            'message': 'Form submitted successfully'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error submitting form: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@forms_bp.route('/user/<user_id>', methods=['GET'])
def get_user_forms(user_id):
    """Get all forms for a user"""
    try:
        form_type_param = request.args.get('form_type')
        form_type = None
        
        if form_type_param:
            try:
                form_type = FormType(form_type_param)
            except ValueError:
                return jsonify({'error': 'Invalid form type'}), 400
        
        user_forms = form_generator.get_user_forms(user_id, form_type)
        
        return jsonify({
            'success': True,
            'forms': user_forms,
            'count': len(user_forms)
        })
        
    except Exception as e:
        logging.error(f"Error getting user forms: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@forms_bp.route('/status/<status>', methods=['GET'])
def get_forms_by_status(status):
    """Get forms by status (admin endpoint)"""
    try:
        try:
            status_enum = FormStatus(status)
        except ValueError:
            return jsonify({'error': 'Invalid status'}), 400
        
        # Filter forms by status
        filtered_forms = [
            form for form in form_generator.forms.values() 
            if form['status'] == status_enum.value
        ]
        
        return jsonify({
            'success': True,
            'forms': filtered_forms,
            'count': len(filtered_forms)
        })
        
    except Exception as e:
        logging.error(f"Error getting forms by status: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@forms_bp.route('/statistics', methods=['GET'])
def get_form_statistics():
    """Get form statistics (admin endpoint)"""
    try:
        all_forms = list(form_generator.forms.values())
        
        # Calculate statistics
        stats = {
            'total_forms': len(all_forms),
            'by_status': {},
            'by_type': {},
            'recent_submissions': 0
        }
        
        # Count by status
        for status in FormStatus:
            count = len([f for f in all_forms if f['status'] == status.value])
            stats['by_status'][status.value] = count
        
        # Count by type
        for form_type in FormType:
            count = len([f for f in all_forms if f['form_type'] == form_type.value])
            stats['by_type'][form_type.value] = count
        
        # Count recent submissions (last 7 days)
        from datetime import timedelta
        week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
        stats['recent_submissions'] = len([
            f for f in all_forms 
            if f['status'] == FormStatus.SUBMITTED.value and f['updated_at'] > week_ago
        ])
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        logging.error(f"Error getting form statistics: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

