"""
Learning System API Routes
Handles document processing, vector search, and knowledge management
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import logging

# Import learning system components
import sys
sys.path.append('/home/ubuntu/malta-tax-ai-learning')

try:
    from document_processor.processor import DocumentProcessor, DocumentType, ProcessingStatus
    from pinecone.vector_service import VectorService, KnowledgeBaseManager
    LEARNING_AVAILABLE = True
except ImportError as e:
    LEARNING_AVAILABLE = False
    logging.warning(f"Learning system not available: {e}")

learning_bp = Blueprint('learning', __name__, url_prefix='/api/learning')

# Initialize services
if LEARNING_AVAILABLE:
    document_processor = DocumentProcessor()
    vector_service = VectorService()
    knowledge_manager = KnowledgeBaseManager(vector_service)
else:
    document_processor = None
    vector_service = None
    knowledge_manager = None


@learning_bp.route('/health', methods=['GET'])
def health_check():
    """Health check for learning system"""
    return jsonify({
        'status': 'healthy' if LEARNING_AVAILABLE else 'degraded',
        'learning_available': LEARNING_AVAILABLE,
        'timestamp': datetime.utcnow().isoformat(),
        'components': {
            'document_processor': document_processor is not None,
            'vector_service': vector_service is not None,
            'knowledge_manager': knowledge_manager is not None
        }
    })


@learning_bp.route('/documents/upload', methods=['POST'])
def upload_document():
    """Upload and process a document"""
    if not LEARNING_AVAILABLE:
        return jsonify({'error': 'Learning system not available'}), 503
    
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get additional parameters
        document_type_str = request.form.get('document_type', 'unknown')
        user_id = request.form.get('user_id', 'anonymous')
        metadata = json.loads(request.form.get('metadata', '{}'))
        
        # Convert document type
        try:
            document_type = DocumentType(document_type_str)
        except ValueError:
            document_type = DocumentType.UNKNOWN
        
        # Read file data
        file_data = file.read()
        filename = secure_filename(file.filename)
        
        # Process document asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                document_processor.process_document(
                    file_data=file_data,
                    filename=filename,
                    document_type=document_type
                )
            )
        finally:
            loop.close()
        
        # Store in vector database if processing succeeded
        if result.status == ProcessingStatus.COMPLETED:
            # Combine text for embedding
            full_text = f"{result.structured_text}\n\nExtracted Data: {json.dumps(result.extracted_data.fields)}"
            
            # Prepare metadata for vector storage
            vector_metadata = {
                'user_id': user_id,
                'filename': filename,
                'document_type': document_type.value,
                'file_type': result.metadata.file_type,
                'processing_confidence': result.metadata.confidence,
                **metadata,
                **result.extracted_data.fields
            }
            
            # Store in vector database
            vector_success = vector_service.upsert_document(
                document_id=result.document_id,
                text=full_text,
                metadata=vector_metadata
            )
            
            if not vector_success:
                logging.warning(f"Failed to store document {result.document_id} in vector database")
        
        # Return processing result
        return jsonify({
            'success': True,
            'document_id': result.document_id,
            'status': result.status.value,
            'metadata': {
                'filename': result.metadata.filename,
                'file_type': result.metadata.file_type,
                'file_size': result.metadata.file_size,
                'document_type': result.metadata.document_type.value,
                'confidence': result.metadata.confidence,
                'processing_time': result.metadata.processing_time,
                'pages': result.metadata.pages
            },
            'extracted_data': {
                'fields': result.extracted_data.fields,
                'confidence_scores': result.extracted_data.confidence_scores,
                'validation_errors': result.extracted_data.validation_errors
            },
            'text_preview': result.raw_text[:500] if result.raw_text else "",
            'error_message': result.error_message
        })
        
    except Exception as e:
        logging.error(f"Document upload failed: {e}")
        return jsonify({
            'error': 'Document processing failed',
            'details': str(e)
        }), 500


@learning_bp.route('/documents/search', methods=['POST'])
def search_documents():
    """Search documents using vector similarity"""
    if not LEARNING_AVAILABLE:
        return jsonify({'error': 'Learning system not available'}), 503
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        query = data.get('query', '')
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        top_k = data.get('top_k', 10)
        filters = data.get('filters', {})
        user_id = data.get('user_id')
        
        # Add user filter if provided
        if user_id:
            filters['user_id'] = user_id
        
        # Perform vector search
        results = vector_service.search_similar(
            query=query,
            top_k=top_k,
            filters=filters,
            include_metadata=True
        )
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_result = {
                'document_id': result['id'],
                'similarity_score': result['score'],
                'metadata': result.get('metadata', {}),
                'text_preview': result.get('metadata', {}).get('text_preview', '')
            }
            formatted_results.append(formatted_result)
        
        return jsonify({
            'success': True,
            'query': query,
            'results': formatted_results,
            'total_results': len(formatted_results)
        })
        
    except Exception as e:
        logging.error(f"Document search failed: {e}")
        return jsonify({
            'error': 'Document search failed',
            'details': str(e)
        }), 500


@learning_bp.route('/knowledge/search', methods=['POST'])
def search_knowledge():
    """Search knowledge base"""
    if not LEARNING_AVAILABLE:
        return jsonify({'error': 'Learning system not available'}), 503
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        query = data.get('query', '')
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        category = data.get('category')
        tags = data.get('tags', [])
        top_k = data.get('top_k', 10)
        
        # Search knowledge base
        results = knowledge_manager.search_knowledge(
            query=query,
            category=category,
            tags=tags,
            top_k=top_k
        )
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_result = {
                'knowledge_id': result['id'],
                'relevance_score': result['score'],
                'title': result.get('metadata', {}).get('title', 'Unknown'),
                'category': result.get('metadata', {}).get('category', 'Unknown'),
                'tags': result.get('metadata', {}).get('tags', []),
                'content_preview': result.get('metadata', {}).get('text_preview', '')
            }
            formatted_results.append(formatted_result)
        
        return jsonify({
            'success': True,
            'query': query,
            'results': formatted_results,
            'total_results': len(formatted_results)
        })
        
    except Exception as e:
        logging.error(f"Knowledge search failed: {e}")
        return jsonify({
            'error': 'Knowledge search failed',
            'details': str(e)
        }), 500


@learning_bp.route('/knowledge/add', methods=['POST'])
def add_knowledge():
    """Add knowledge item to the knowledge base"""
    if not LEARNING_AVAILABLE:
        return jsonify({'error': 'Learning system not available'}), 503
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Required fields
        title = data.get('title', '')
        content = data.get('content', '')
        category = data.get('category', 'general')
        
        if not title or not content:
            return jsonify({'error': 'Title and content are required'}), 400
        
        # Optional fields
        tags = data.get('tags', [])
        metadata = data.get('metadata', {})
        
        # Generate knowledge item ID
        item_id = f"kb_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(title) % 10000:04d}"
        
        # Add to knowledge base
        success = knowledge_manager.add_knowledge_item(
            item_id=item_id,
            title=title,
            content=content,
            category=category,
            tags=tags,
            metadata=metadata
        )
        
        if success:
            return jsonify({
                'success': True,
                'knowledge_id': item_id,
                'message': 'Knowledge item added successfully'
            })
        else:
            return jsonify({
                'error': 'Failed to add knowledge item'
            }), 500
        
    except Exception as e:
        logging.error(f"Add knowledge failed: {e}")
        return jsonify({
            'error': 'Failed to add knowledge item',
            'details': str(e)
        }), 500


@learning_bp.route('/vector/stats', methods=['GET'])
def vector_stats():
    """Get vector database statistics"""
    if not LEARNING_AVAILABLE:
        return jsonify({'error': 'Learning system not available'}), 503
    
    try:
        stats = vector_service.get_index_stats()
        
        return jsonify({
            'success': True,
            'stats': stats,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logging.error(f"Vector stats failed: {e}")
        return jsonify({
            'error': 'Failed to get vector statistics',
            'details': str(e)
        }), 500


@learning_bp.route('/documents/<document_id>', methods=['GET'])
def get_document(document_id):
    """Get document by ID"""
    if not LEARNING_AVAILABLE:
        return jsonify({'error': 'Learning system not available'}), 503
    
    try:
        # This would typically query a database
        # For now, return a placeholder response
        return jsonify({
            'success': True,
            'document_id': document_id,
            'message': 'Document retrieval not yet implemented'
        })
        
    except Exception as e:
        logging.error(f"Get document failed: {e}")
        return jsonify({
            'error': 'Failed to get document',
            'details': str(e)
        }), 500


@learning_bp.route('/documents/<document_id>', methods=['DELETE'])
def delete_document(document_id):
    """Delete document by ID"""
    if not LEARNING_AVAILABLE:
        return jsonify({'error': 'Learning system not available'}), 503
    
    try:
        # Delete from vector database
        success = vector_service.delete_document(document_id)
        
        if success:
            return jsonify({
                'success': True,
                'document_id': document_id,
                'message': 'Document deleted successfully'
            })
        else:
            return jsonify({
                'error': 'Failed to delete document'
            }), 500
        
    except Exception as e:
        logging.error(f"Delete document failed: {e}")
        return jsonify({
            'error': 'Failed to delete document',
            'details': str(e)
        }), 500


@learning_bp.route('/batch/upload', methods=['POST'])
def batch_upload():
    """Batch upload multiple documents"""
    if not LEARNING_AVAILABLE:
        return jsonify({'error': 'Learning system not available'}), 503
    
    try:
        # Check if files are present
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        if not files:
            return jsonify({'error': 'No files selected'}), 400
        
        # Get parameters
        user_id = request.form.get('user_id', 'anonymous')
        document_type_str = request.form.get('document_type', 'unknown')
        
        try:
            document_type = DocumentType(document_type_str)
        except ValueError:
            document_type = DocumentType.UNKNOWN
        
        # Process files
        results = []
        successful = 0
        failed = 0
        
        for file in files:
            try:
                if file.filename == '':
                    continue
                
                file_data = file.read()
                filename = secure_filename(file.filename)
                
                # Process document
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    result = loop.run_until_complete(
                        document_processor.process_document(
                            file_data=file_data,
                            filename=filename,
                            document_type=document_type
                        )
                    )
                finally:
                    loop.close()
                
                if result.status == ProcessingStatus.COMPLETED:
                    successful += 1
                    
                    # Store in vector database
                    full_text = f"{result.structured_text}\n\nExtracted Data: {json.dumps(result.extracted_data.fields)}"
                    vector_metadata = {
                        'user_id': user_id,
                        'filename': filename,
                        'document_type': document_type.value,
                        'file_type': result.metadata.file_type,
                        **result.extracted_data.fields
                    }
                    
                    vector_service.upsert_document(
                        document_id=result.document_id,
                        text=full_text,
                        metadata=vector_metadata
                    )
                else:
                    failed += 1
                
                results.append({
                    'filename': filename,
                    'document_id': result.document_id,
                    'status': result.status.value,
                    'error_message': result.error_message
                })
                
            except Exception as e:
                failed += 1
                results.append({
                    'filename': file.filename,
                    'status': 'failed',
                    'error_message': str(e)
                })
        
        return jsonify({
            'success': True,
            'total_files': len(files),
            'successful': successful,
            'failed': failed,
            'results': results
        })
        
    except Exception as e:
        logging.error(f"Batch upload failed: {e}")
        return jsonify({
            'error': 'Batch upload failed',
            'details': str(e)
        }), 500


@learning_bp.route('/embeddings/generate', methods=['POST'])
def generate_embeddings():
    """Generate embeddings for text"""
    if not LEARNING_AVAILABLE:
        return jsonify({'error': 'Learning system not available'}), 503
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        text = data.get('text', '')
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        # Generate embeddings
        embeddings = vector_service.generate_embeddings(text)
        
        return jsonify({
            'success': True,
            'text': text[:100] + '...' if len(text) > 100 else text,
            'embeddings': embeddings,
            'dimension': len(embeddings)
        })
        
    except Exception as e:
        logging.error(f"Generate embeddings failed: {e}")
        return jsonify({
            'error': 'Failed to generate embeddings',
            'details': str(e)
        }), 500


# Error handlers
@learning_bp.errorhandler(413)
def file_too_large(error):
    return jsonify({
        'error': 'File too large',
        'message': 'The uploaded file exceeds the maximum size limit'
    }), 413


@learning_bp.errorhandler(415)
def unsupported_media_type(error):
    return jsonify({
        'error': 'Unsupported media type',
        'message': 'The uploaded file type is not supported'
    }), 415


# Register blueprint with main app
def register_learning_routes(app):
    """Register learning routes with Flask app"""
    app.register_blueprint(learning_bp)
    
    # Configure file upload limits
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
    
    logging.info("Learning system routes registered")

