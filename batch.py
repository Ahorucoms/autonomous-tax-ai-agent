"""
Batch Processing API Routes
Handle bulk operations and batch filing functionality
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import logging
from typing import Dict, Any

from ..services.batch_service import BatchService, BatchJobStatus, BatchJobType

batch_bp = Blueprint('batch', __name__)

# Initialize batch service
batch_service = BatchService()

@batch_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'batch',
        'timestamp': datetime.utcnow().isoformat()
    })

@batch_bp.route('/templates', methods=['GET'])
def get_batch_templates():
    """Get available batch processing templates"""
    try:
        result = batch_service.get_batch_templates()
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error getting batch templates: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@batch_bp.route('/jobs', methods=['POST'])
def create_batch_job():
    """Create new batch processing job"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request data is required'}), 400
        
        # Get user ID from session (simplified for development)
        user_id = request.headers.get('X-User-ID', 'user_001')
        data['user_id'] = user_id
        
        result = batch_service.create_batch_job(data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error creating batch job: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@batch_bp.route('/jobs', methods=['GET'])
def get_batch_jobs():
    """Get paginated list of batch jobs"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        user_id = request.args.get('user_id')
        status = request.args.get('status')
        
        if page < 1:
            return jsonify({'error': 'Page must be >= 1'}), 400
        if per_page < 1 or per_page > 100:
            return jsonify({'error': 'Per page must be between 1 and 100'}), 400
        
        result = batch_service.get_batch_jobs(user_id, status, page, per_page)
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error getting batch jobs: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@batch_bp.route('/jobs/<job_id>', methods=['GET'])
def get_batch_job_status(job_id):
    """Get batch job status and progress"""
    try:
        result = batch_service.get_batch_job_status(job_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 404
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error getting batch job status: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@batch_bp.route('/jobs/<job_id>/upload', methods=['POST'])
def upload_batch_data(job_id):
    """Upload batch data for processing"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request data is required'}), 400
        
        if 'file_data' not in data:
            return jsonify({'error': 'file_data is required'}), 400
        
        file_format = data.get('file_format', 'csv')
        file_data = data['file_data']
        
        result = batch_service.upload_batch_data(job_id, file_data, file_format)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error uploading batch data: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@batch_bp.route('/jobs/<job_id>/process', methods=['POST'])
def start_batch_processing(job_id):
    """Start processing batch job"""
    try:
        result = batch_service.start_batch_processing(job_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error starting batch processing: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@batch_bp.route('/jobs/<job_id>/validate', methods=['POST'])
def validate_batch_data(job_id):
    """Validate batch data without processing"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request data is required'}), 400
        
        if 'file_data' not in data:
            return jsonify({'error': 'file_data is required'}), 400
        
        file_format = data.get('file_format', 'csv')
        file_data = data['file_data']
        
        # Upload and validate data (without processing)
        result = batch_service.upload_batch_data(job_id, file_data, file_format)
        
        if result['success']:
            return jsonify({
                'success': True,
                'validation_result': {
                    'is_valid': True,
                    'total_records': result['total_records'],
                    'warnings': result.get('validation_warnings', [])
                }
            })
        else:
            return jsonify({
                'success': False,
                'validation_result': {
                    'is_valid': False,
                    'errors': result.get('validation_errors', [result.get('error')])
                }
            }), 400
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error validating batch data: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@batch_bp.route('/statistics', methods=['GET'])
def get_processing_statistics():
    """Get batch processing statistics"""
    try:
        result = batch_service.get_processing_statistics()
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error getting processing statistics: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@batch_bp.route('/job-types', methods=['GET'])
def get_job_types():
    """Get available batch job types"""
    try:
        job_types = [
            {
                'value': job_type.value,
                'name': job_type.name.replace('_', ' ').title(),
                'description': f'{job_type.value.replace("_", " ").title()} processing'
            }
            for job_type in BatchJobType
        ]
        
        return jsonify({
            'success': True,
            'job_types': job_types
        })
        
    except Exception as e:
        logging.error(f"Error getting job types: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@batch_bp.route('/job-statuses', methods=['GET'])
def get_job_statuses():
    """Get available batch job statuses"""
    try:
        statuses = [
            {
                'value': status.value,
                'name': status.name.replace('_', ' ').title(),
                'description': f'{status.value.replace("_", " ").title()} status'
            }
            for status in BatchJobStatus
        ]
        
        return jsonify({
            'success': True,
            'statuses': statuses
        })
        
    except Exception as e:
        logging.error(f"Error getting job statuses: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@batch_bp.route('/sample-data/<template_name>', methods=['GET'])
def get_sample_data(template_name):
    """Get sample data for batch template"""
    try:
        templates_result = batch_service.get_batch_templates()
        
        if not templates_result['success']:
            return jsonify({'error': 'Failed to get templates'}), 500
        
        templates = templates_result['templates']
        
        if template_name not in templates:
            return jsonify({'error': 'Template not found'}), 404
        
        template = templates[template_name]
        
        # Generate sample data based on template
        sample_data = []
        required_columns = template['required_columns']
        optional_columns = template.get('optional_columns', [])
        
        # Create sample records
        for i in range(3):  # 3 sample records
            record = {}
            
            # Add required columns with sample data
            for col in required_columns:
                if col == 'taxpayer_name':
                    record[col] = f'Sample Taxpayer {i+1}'
                elif col == 'tax_number':
                    record[col] = f'MT{12345678 + i}'
                elif col == 'gross_income':
                    record[col] = str(45000 + (i * 5000))
                elif col == 'tax_year':
                    record[col] = '2024'
                elif col == 'marital_status':
                    record[col] = ['single', 'married', 'divorced'][i % 3]
                elif col == 'business_name':
                    record[col] = f'Sample Business {i+1}'
                elif col == 'vat_number':
                    record[col] = f'MT{87654321 + i}'
                elif col == 'total_sales':
                    record[col] = str(100000 + (i * 10000))
                elif col == 'vat_due':
                    record[col] = str(18000 + (i * 1800))
                elif col == 'amount':
                    record[col] = str(2500 + (i * 250))
                elif col == 'payment_method':
                    record[col] = ['bank_transfer', 'credit_card', 'debit_card'][i % 3]
                else:
                    record[col] = f'sample_{col}_{i+1}'
            
            # Add some optional columns
            for col in optional_columns[:2]:  # Add first 2 optional columns
                if col == 'email':
                    record[col] = f'sample{i+1}@example.com'
                elif col == 'phone':
                    record[col] = f'+356 2{i+1}{i+1}{i+1}{i+1}{i+1}{i+1}{i+1}'
                else:
                    record[col] = f'optional_{col}_{i+1}'
            
            sample_data.append(record)
        
        return jsonify({
            'success': True,
            'template_name': template_name,
            'sample_data': sample_data,
            'template_info': {
                'required_columns': required_columns,
                'optional_columns': optional_columns,
                'max_records': template['max_records']
            }
        })
        
    except Exception as e:
        logging.error(f"Error getting sample data: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@batch_bp.route('/export/<job_id>', methods=['GET'])
def export_batch_results(job_id):
    """Export batch processing results"""
    try:
        result = batch_service.get_batch_job_status(job_id)
        
        if not result['success']:
            return jsonify(result), 404
        
        job_status = result['job_status']
        
        if job_status['status'] not in ['completed', 'failed']:
            return jsonify({'error': 'Job not ready for export'}), 400
        
        # Get full job details including results
        if job_id not in batch_service.batch_jobs:
            return jsonify({'error': 'Job details not found'}), 404
        
        batch_job = batch_service.batch_jobs[job_id]
        
        export_data = {
            'job_summary': {
                'job_id': job_id,
                'status': job_status['status'],
                'total_records': job_status['total_records'],
                'successful_records': job_status['successful_records'],
                'failed_records': job_status['failed_records'],
                'processing_time': job_status.get('processing_end_time'),
                'created_at': job_status['created_at']
            },
            'results': batch_job.get('results', []),
            'errors': batch_job.get('errors', [])
        }
        
        return jsonify({
            'success': True,
            'export_data': export_data
        })
        
    except Exception as e:
        logging.error(f"Error exporting batch results: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

