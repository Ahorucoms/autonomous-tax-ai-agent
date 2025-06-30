"""
Document Management API Routes
Handles file upload, processing, and document management
"""

from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import mimetypes
import logging
from typing import Dict, List, Any

from ..models.document import Document, DocumentType, DocumentStatus, ProcessingStage, DocumentManager

# Initialize document manager
document_manager = DocumentManager(upload_directory="/tmp/malta_tax_uploads")

documents_bp = Blueprint('documents', __name__)

# Allowed file extensions and MIME types
ALLOWED_EXTENSIONS = {
    'pdf', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff',
    'csv', 'xlsx', 'xls', 'txt', 'doc', 'docx'
}

ALLOWED_MIME_TYPES = {
    'application/pdf',
    'image/png', 'image/jpeg', 'image/gif', 'image/bmp', 'image/tiff',
    'text/csv', 'text/plain',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
}

def allowed_file(filename: str, mime_type: str) -> bool:
    """Check if file is allowed based on extension and MIME type"""
    if not filename:
        return False
    
    # Check extension
    file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    if file_ext not in ALLOWED_EXTENSIONS:
        return False
    
    # Check MIME type
    if mime_type not in ALLOWED_MIME_TYPES:
        return False
    
    return True

@documents_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'document_management',
        'timestamp': datetime.utcnow().isoformat()
    })

@documents_bp.route('/documents/upload', methods=['POST'])
def upload_document():
    """Upload a document"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get additional parameters
        user_id = request.form.get('user_id')
        document_type = request.form.get('document_type', 'other')
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        # Validate file
        filename = secure_filename(file.filename)
        mime_type = file.content_type or mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        
        if not allowed_file(filename, mime_type):
            return jsonify({
                'error': 'File type not allowed',
                'allowed_extensions': list(ALLOWED_EXTENSIONS),
                'detected_mime_type': mime_type
            }), 400
        
        # Read file data
        file_data = file.read()
        file_size = len(file_data)
        
        # Check file size (max 50MB)
        max_size = 50 * 1024 * 1024  # 50MB
        if file_size > max_size:
            return jsonify({'error': f'File too large. Maximum size is {max_size // (1024*1024)}MB'}), 400
        
        # Save file
        file_path = document_manager.save_uploaded_file(file_data, filename, user_id)
        
        # Create document record
        document = Document(
            filename=filename,
            user_id=user_id,
            file_path=file_path,
            file_size=file_size,
            mime_type=mime_type,
            document_type=DocumentType(document_type)
        )
        
        # Calculate file hash
        document.calculate_file_hash()
        
        # Auto-classify document type if not specified
        if document_type == 'other':
            document.document_type = document_manager.classify_document_type(filename)
        
        # Save document
        document_id = document_manager.create_document(document)
        
        # Update status to processing
        document.update_status(DocumentStatus.PROCESSING, ProcessingStage.VIRUS_SCAN, "File uploaded successfully")
        
        return jsonify({
            'success': True,
            'document_id': document_id,
            'document': document.to_dict(),
            'message': 'File uploaded successfully'
        }), 201
        
    except Exception as e:
        logging.error(f"Error uploading document: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@documents_bp.route('/documents/<document_id>', methods=['GET'])
def get_document(document_id):
    """Get document details by ID"""
    try:
        document = document_manager.get_document(document_id)
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        return jsonify({
            'success': True,
            'document': document.to_dict()
        })
        
    except Exception as e:
        logging.error(f"Error getting document {document_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@documents_bp.route('/documents/<document_id>/download', methods=['GET'])
def download_document(document_id):
    """Download document file"""
    try:
        document = document_manager.get_document(document_id)
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        if not os.path.exists(document.file_path):
            return jsonify({'error': 'File not found on disk'}), 404
        
        return send_file(
            document.file_path,
            as_attachment=True,
            download_name=document.filename,
            mimetype=document.mime_type
        )
        
    except Exception as e:
        logging.error(f"Error downloading document {document_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@documents_bp.route('/documents/<document_id>', methods=['PUT'])
def update_document(document_id):
    """Update document metadata"""
    try:
        data = request.get_json()
        
        document = document_manager.get_document(document_id)
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        # Update allowed fields
        if 'document_type' in data:
            document.document_type = DocumentType(data['document_type'])
        if 'tags' in data:
            document.tags = data['tags']
        if 'tax_year' in data:
            document.tax_year = data['tax_year']
        if 'tax_period' in data:
            document.tax_period = data['tax_period']
        if 'entity_name' in data:
            document.entity_name = data['entity_name']
        if 'entity_id' in data:
            document.entity_id = data['entity_id']
        
        document.updated_at = datetime.utcnow()
        
        return jsonify({
            'success': True,
            'document': document.to_dict()
        })
        
    except ValueError as e:
        return jsonify({'error': f'Invalid data: {str(e)}'}), 400
    except Exception as e:
        logging.error(f"Error updating document {document_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@documents_bp.route('/documents/<document_id>', methods=['DELETE'])
def delete_document(document_id):
    """Delete a document"""
    try:
        success = document_manager.delete_document(document_id)
        if not success:
            return jsonify({'error': 'Document not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Document deleted successfully'
        })
        
    except Exception as e:
        logging.error(f"Error deleting document {document_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@documents_bp.route('/users/<user_id>/documents', methods=['GET'])
def get_user_documents(user_id):
    """Get all documents for a user"""
    try:
        document_type = request.args.get('type')
        doc_type = DocumentType(document_type) if document_type else None
        
        documents = document_manager.get_user_documents(user_id, doc_type)
        
        return jsonify({
            'success': True,
            'documents': [doc.to_dict() for doc in documents],
            'count': len(documents)
        })
        
    except ValueError as e:
        return jsonify({'error': f'Invalid document type: {str(e)}'}), 400
    except Exception as e:
        logging.error(f"Error getting documents for user {user_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@documents_bp.route('/documents/<document_id>/process', methods=['POST'])
def process_document(document_id):
    """Trigger document processing"""
    try:
        document = document_manager.get_document(document_id)
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        # Simulate document processing
        if document.is_pdf():
            # Simulate PDF text extraction
            document.update_status(DocumentStatus.PROCESSING, ProcessingStage.OCR, "Extracting text from PDF")
            document.text_content = "Sample extracted text from PDF document..."
            document.add_extracted_data("total_amount", 1500.00, 0.95)
            document.add_extracted_data("date", "2024-06-30", 0.90)
            
        elif document.is_image():
            # Simulate OCR processing
            document.update_status(DocumentStatus.PROCESSING, ProcessingStage.OCR, "Performing OCR on image")
            document.text_content = "Sample OCR text from image document..."
            document.add_extracted_data("invoice_number", "INV-2024-001", 0.85)
            
        elif document.is_spreadsheet():
            # Simulate spreadsheet processing
            document.update_status(DocumentStatus.PROCESSING, ProcessingStage.DATA_EXTRACTION, "Processing spreadsheet")
            document.add_extracted_data("total_rows", 150, 1.0)
            document.add_extracted_data("sum_column_b", 25000.00, 1.0)
        
        # Add AI analysis
        document.add_ai_analysis("classification", {
            "predicted_type": document.document_type.value,
            "confidence": 0.92,
            "alternative_types": ["invoice", "receipt"]
        })
        
        # Mark as processed
        document.update_status(DocumentStatus.PROCESSED, ProcessingStage.COMPLETED, "Document processing completed")
        document.confidence_score = 0.90
        
        return jsonify({
            'success': True,
            'document': document.to_dict(),
            'message': 'Document processed successfully'
        })
        
    except Exception as e:
        logging.error(f"Error processing document {document_id}: {str(e)}")
        document.add_error(f"Processing failed: {str(e)}", ProcessingStage.DATA_EXTRACTION)
        return jsonify({'error': 'Processing failed'}), 500

@documents_bp.route('/documents/<document_id>/extract-data', methods=['POST'])
def extract_data(document_id):
    """Extract specific data from document"""
    try:
        data = request.get_json()
        fields = data.get('fields', [])
        
        document = document_manager.get_document(document_id)
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        # Simulate data extraction for requested fields
        extracted = {}
        for field in fields:
            if field == 'amount':
                extracted[field] = {'value': 1250.00, 'confidence': 0.95}
            elif field == 'date':
                extracted[field] = {'value': '2024-06-30', 'confidence': 0.90}
            elif field == 'invoice_number':
                extracted[field] = {'value': 'INV-2024-001', 'confidence': 0.85}
            elif field == 'vat_amount':
                extracted[field] = {'value': 225.00, 'confidence': 0.88}
            else:
                extracted[field] = {'value': None, 'confidence': 0.0}
        
        # Update document with extracted data
        for field, result in extracted.items():
            document.add_extracted_data(field, result['value'], result['confidence'])
        
        return jsonify({
            'success': True,
            'extracted_data': extracted,
            'document': document.to_dict()
        })
        
    except Exception as e:
        logging.error(f"Error extracting data from document {document_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@documents_bp.route('/documents/types', methods=['GET'])
def get_document_types():
    """Get available document types"""
    try:
        types = [
            {
                'value': doc_type.value,
                'label': doc_type.value.replace('_', ' ').title(),
                'description': f"Malta tax document type: {doc_type.value}"
            }
            for doc_type in DocumentType
        ]
        
        return jsonify({
            'success': True,
            'document_types': types
        })
        
    except Exception as e:
        logging.error(f"Error getting document types: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@documents_bp.route('/documents/processing-queue', methods=['GET'])
def get_processing_queue():
    """Get documents in processing queue"""
    try:
        queue = document_manager.get_processing_queue()
        
        return jsonify({
            'success': True,
            'queue': [doc.to_dict() for doc in queue],
            'count': len(queue)
        })
        
    except Exception as e:
        logging.error(f"Error getting processing queue: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@documents_bp.route('/documents/<document_id>/ai-analysis', methods=['POST'])
def add_ai_analysis(document_id):
    """Add AI analysis result to document"""
    try:
        data = request.get_json()
        
        if 'analysis_type' not in data or 'result' not in data:
            return jsonify({'error': 'Missing required fields: analysis_type, result'}), 400
        
        document = document_manager.get_document(document_id)
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        document.add_ai_analysis(data['analysis_type'], data['result'])
        
        return jsonify({
            'success': True,
            'document': document.to_dict()
        })
        
    except Exception as e:
        logging.error(f"Error adding AI analysis to document {document_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@documents_bp.route('/stats/<user_id>', methods=['GET'])
def get_document_stats(user_id):
    """Get document statistics for a user"""
    try:
        documents = document_manager.get_user_documents(user_id)
        
        stats = {
            'total_documents': len(documents),
            'processed_documents': len([d for d in documents if d.status == DocumentStatus.PROCESSED]),
            'processing_documents': len([d for d in documents if d.status == DocumentStatus.PROCESSING]),
            'failed_documents': len([d for d in documents if d.status == DocumentStatus.FAILED]),
            'total_file_size': sum(d.file_size for d in documents),
            'document_types': {},
            'recent_uploads': len([d for d in documents if (datetime.utcnow() - d.created_at).days <= 7])
        }
        
        # Count by document type
        for doc in documents:
            doc_type = doc.document_type.value
            if doc_type not in stats['document_types']:
                stats['document_types'][doc_type] = 0
            stats['document_types'][doc_type] += 1
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logging.error(f"Error getting document stats for user {user_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

