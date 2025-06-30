"""
Advanced Document Processing API Routes
Handle intelligent document classification, data extraction, and validation
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import logging
import json
from typing import Dict, Any

from ..services.document_processor import AdvancedDocumentProcessor, DocumentType, ProcessingStatus

document_processing_bp = Blueprint('document_processing', __name__)

# Initialize document processor
doc_processor = AdvancedDocumentProcessor()

@document_processing_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'document_processing',
        'timestamp': datetime.utcnow().isoformat()
    })

@document_processing_bp.route('/classify', methods=['POST'])
def classify_document():
    """Classify document type"""
    try:
        data = request.get_json()
        
        if 'content' not in data:
            return jsonify({'error': 'Document content is required'}), 400
        
        content = data['content']
        filename = data.get('filename', '')
        
        document_type = doc_processor.classify_document(content, filename)
        
        return jsonify({
            'success': True,
            'document_type': document_type.value,
            'confidence': 'high' if document_type != DocumentType.UNKNOWN else 'low',
            'classification_timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logging.error(f"Error classifying document: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@document_processing_bp.route('/extract', methods=['POST'])
def extract_data():
    """Extract structured data from document"""
    try:
        data = request.get_json()
        
        required_fields = ['content']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        content = data['content']
        filename = data.get('filename', '')
        document_type_str = data.get('document_type')
        
        # Classify document if type not provided
        if document_type_str:
            try:
                document_type = DocumentType(document_type_str)
            except ValueError:
                return jsonify({'error': 'Invalid document type'}), 400
        else:
            document_type = doc_processor.classify_document(content, filename)
        
        # Extract structured data
        extracted_data = doc_processor.extract_structured_data(content, document_type)
        
        return jsonify({
            'success': True,
            'extraction_result': extracted_data
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error extracting data: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@document_processing_bp.route('/process-batch', methods=['POST'])
def process_batch():
    """Process multiple documents in batch"""
    try:
        data = request.get_json()
        
        if 'documents' not in data:
            return jsonify({'error': 'Documents array is required'}), 400
        
        documents = data['documents']
        
        if not isinstance(documents, list):
            return jsonify({'error': 'Documents must be an array'}), 400
        
        if len(documents) == 0:
            return jsonify({'error': 'At least one document is required'}), 400
        
        # Validate document structure
        for i, doc in enumerate(documents):
            if 'content' not in doc:
                return jsonify({'error': f'Document {i} missing content field'}), 400
        
        batch_result = doc_processor.process_document_batch(documents)
        
        return jsonify({
            'success': True,
            'batch_result': batch_result
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error processing batch: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@document_processing_bp.route('/reconcile', methods=['POST'])
def reconcile_documents():
    """Reconcile data across multiple documents"""
    try:
        data = request.get_json()
        
        if 'document_ids' not in data:
            return jsonify({'error': 'Document IDs array is required'}), 400
        
        document_ids = data['document_ids']
        
        if not isinstance(document_ids, list):
            return jsonify({'error': 'Document IDs must be an array'}), 400
        
        if len(document_ids) < 2:
            return jsonify({'error': 'At least two documents are required for reconciliation'}), 400
        
        reconciliation_result = doc_processor.reconcile_documents(document_ids)
        
        return jsonify({
            'success': True,
            'reconciliation_result': reconciliation_result
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error reconciling documents: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@document_processing_bp.route('/validate', methods=['POST'])
def validate_extracted_data():
    """Validate extracted document data"""
    try:
        data = request.get_json()
        
        required_fields = ['extracted_data', 'document_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        extracted_data = data['extracted_data']
        document_type_str = data['document_type']
        
        try:
            document_type = DocumentType(document_type_str)
        except ValueError:
            return jsonify({'error': 'Invalid document type'}), 400
        
        # Perform validation
        validation_result = {
            'document_type': document_type.value,
            'validation_timestamp': datetime.utcnow().isoformat(),
            'is_valid': True,
            'validation_errors': [],
            'validation_warnings': [],
            'confidence_score': 0.0
        }
        
        # Add validation errors to the extracted data structure
        if 'validation_errors' not in extracted_data:
            extracted_data['validation_errors'] = []
        
        # Validate using the processor's validation logic
        doc_processor._validate_extracted_data(extracted_data, document_type)
        
        validation_result['validation_errors'] = extracted_data['validation_errors']
        validation_result['is_valid'] = len(extracted_data['validation_errors']) == 0
        validation_result['confidence_score'] = doc_processor._calculate_confidence_score(extracted_data)
        
        return jsonify({
            'success': True,
            'validation_result': validation_result
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error validating data: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@document_processing_bp.route('/statistics', methods=['GET'])
def get_processing_statistics():
    """Get document processing statistics"""
    try:
        stats = doc_processor.get_processing_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        logging.error(f"Error getting statistics: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@document_processing_bp.route('/document-types', methods=['GET'])
def get_supported_document_types():
    """Get list of supported document types"""
    try:
        document_types = [
            {
                'type': doc_type.value,
                'name': doc_type.name.replace('_', ' ').title(),
                'description': f'Malta-specific {doc_type.value.replace("_", " ")} processing'
            }
            for doc_type in DocumentType
        ]
        
        return jsonify({
            'success': True,
            'document_types': document_types,
            'count': len(document_types)
        })
        
    except Exception as e:
        logging.error(f"Error getting document types: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@document_processing_bp.route('/field-mappings/<document_type>', methods=['GET'])
def get_field_mappings(document_type):
    """Get field mappings for a specific document type"""
    try:
        try:
            DocumentType(document_type)
        except ValueError:
            return jsonify({'error': 'Invalid document type'}), 400
        
        mappings = doc_processor.field_mappings.get(document_type, {})
        
        return jsonify({
            'success': True,
            'document_type': document_type,
            'field_mappings': mappings
        })
        
    except Exception as e:
        logging.error(f"Error getting field mappings: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@document_processing_bp.route('/validation-rules/<document_type>', methods=['GET'])
def get_validation_rules(document_type):
    """Get validation rules for a specific document type"""
    try:
        try:
            DocumentType(document_type)
        except ValueError:
            return jsonify({'error': 'Invalid document type'}), 400
        
        rules = doc_processor.validation_rules.get(document_type, {})
        
        return jsonify({
            'success': True,
            'document_type': document_type,
            'validation_rules': rules
        })
        
    except Exception as e:
        logging.error(f"Error getting validation rules: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@document_processing_bp.route('/batch-status/<batch_id>', methods=['GET'])
def get_batch_status(batch_id):
    """Get status of a batch processing job"""
    try:
        batch_result = doc_processor.processing_results.get(batch_id)
        
        if not batch_result:
            return jsonify({'error': 'Batch not found'}), 404
        
        return jsonify({
            'success': True,
            'batch_result': batch_result
        })
        
    except Exception as e:
        logging.error(f"Error getting batch status: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@document_processing_bp.route('/enhance-ocr', methods=['POST'])
def enhance_ocr():
    """Enhance OCR accuracy for Malta-specific forms"""
    try:
        data = request.get_json()
        
        if 'raw_ocr_text' not in data:
            return jsonify({'error': 'Raw OCR text is required'}), 400
        
        raw_text = data['raw_ocr_text']
        document_type_str = data.get('document_type', 'unknown')
        
        # Apply Malta-specific OCR enhancements
        enhanced_text = raw_text
        
        # Common OCR corrections for Malta documents
        corrections = {
            'Matta': 'Malta',
            'Govemment': 'Government',
            'Commlssioner': 'Commissioner',
            'Reverue': 'Revenue',
            'Soclal': 'Social',
            'Securlty': 'Security',
            'Contrlbutlons': 'Contributions',
            'Wlthholding': 'Withholding',
            'Certlflcate': 'Certificate',
            'Deducted': 'Deducted',
            'Emplover': 'Employer',
            'Emplovee': 'Employee'
        }
        
        for wrong, correct in corrections.items():
            enhanced_text = enhanced_text.replace(wrong, correct)
        
        # Fix common number/currency OCR errors
        import re
        
        # Fix Euro symbol recognition
        enhanced_text = re.sub(r'[€E]\s*(\d)', r'€\1', enhanced_text)
        
        # Fix decimal separators
        enhanced_text = re.sub(r'(\d),(\d{2})\b', r'\1.\2', enhanced_text)
        
        # Fix Malta VAT number format
        enhanced_text = re.sub(r'MT\s*(\d{8})', r'MT\1', enhanced_text)
        
        enhancement_result = {
            'original_text': raw_text,
            'enhanced_text': enhanced_text,
            'corrections_applied': len([k for k in corrections.keys() if k in raw_text]),
            'enhancement_timestamp': datetime.utcnow().isoformat(),
            'document_type': document_type_str
        }
        
        return jsonify({
            'success': True,
            'enhancement_result': enhancement_result
        })
        
    except Exception as e:
        logging.error(f"Error enhancing OCR: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

