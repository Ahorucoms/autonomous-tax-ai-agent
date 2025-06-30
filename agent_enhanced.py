"""
Enhanced Agent API Routes with Vector Search and Reasoning
Provides intelligent agent capabilities with semantic search and pre-execution reasoning
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from flask import Blueprint, request, jsonify, current_app
import logging

# Import agent services
import sys
sys.path.append('/home/ubuntu/malta-tax-ai-backend/src/services')

try:
    from agent_sdk import (
        reasoning_engine, process_tax_query, get_tax_guidance,
        UserContext, QueryType, ConfidenceLevel
    )
    from vector_search_service import (
        vector_search_service, search_knowledge, add_knowledge_document,
        VectorDocument, DocumentType
    )
    AGENT_SDK_AVAILABLE = True
except ImportError as e:
    AGENT_SDK_AVAILABLE = False
    logging.warning(f"Enhanced agent SDK not available: {e}")

agent_enhanced_bp = Blueprint('agent_enhanced', __name__, url_prefix='/api/agent-enhanced')


@agent_enhanced_bp.route('/health', methods=['GET'])
def health_check():
    """Health check for enhanced agent system"""
    return jsonify({
        'status': 'healthy' if AGENT_SDK_AVAILABLE else 'degraded',
        'agent_sdk_available': AGENT_SDK_AVAILABLE,
        'vector_search_available': AGENT_SDK_AVAILABLE,
        'timestamp': datetime.utcnow().isoformat()
    })


@agent_enhanced_bp.route('/query', methods=['POST'])
def process_query():
    """Process user query with enhanced reasoning"""
    if not AGENT_SDK_AVAILABLE:
        return jsonify({'error': 'Enhanced agent system not available'}), 503
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Validate required fields
        if 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data['query']
        user_id = data.get('user_id', 'anonymous')
        user_type = data.get('user_type', 'individual')
        jurisdiction = data.get('jurisdiction', 'malta')
        language = data.get('language', 'en')
        tax_year = data.get('tax_year', 2025)
        
        # Create user context
        context = UserContext(
            user_id=user_id,
            user_type=user_type,
            jurisdiction=jurisdiction,
            language=language,
            tax_year=tax_year,
            previous_queries=data.get('previous_queries', []),
            preferences=data.get('preferences', {})
        )
        
        # Process query asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            response = loop.run_until_complete(
                reasoning_engine.process_query(query, context)
            )
        finally:
            loop.close()
        
        return jsonify({
            'success': True,
            'response': response.to_dict()
        })
        
    except Exception as e:
        logging.error(f"Query processing failed: {e}")
        return jsonify({
            'error': 'Failed to process query',
            'details': str(e)
        }), 500


@agent_enhanced_bp.route('/search', methods=['POST'])
def search_knowledge_base():
    """Search knowledge base with semantic similarity"""
    if not AGENT_SDK_AVAILABLE:
        return jsonify({'error': 'Enhanced agent system not available'}), 503
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Validate required fields
        if 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data['query']
        document_types = data.get('document_types', [])
        max_results = data.get('max_results', 10)
        
        # Perform search asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            results = loop.run_until_complete(
                search_knowledge(query, document_types, max_results)
            )
        finally:
            loop.close()
        
        return jsonify({
            'success': True,
            'query': query,
            'results': results,
            'total_results': len(results)
        })
        
    except Exception as e:
        logging.error(f"Knowledge search failed: {e}")
        return jsonify({
            'error': 'Failed to search knowledge base',
            'details': str(e)
        }), 500


@agent_enhanced_bp.route('/knowledge', methods=['POST'])
def add_knowledge():
    """Add document to knowledge base"""
    if not AGENT_SDK_AVAILABLE:
        return jsonify({'error': 'Enhanced agent system not available'}), 503
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Validate required fields
        required_fields = ['title', 'content']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        title = data['title']
        content = data['content']
        document_type = data.get('document_type', 'unknown')
        metadata = data.get('metadata', {})
        
        # Add document asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            success = loop.run_until_complete(
                add_knowledge_document(title, content, document_type, metadata)
            )
        finally:
            loop.close()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Document added to knowledge base',
                'title': title,
                'document_type': document_type
            })
        else:
            return jsonify({
                'error': 'Failed to add document to knowledge base'
            }), 500
        
    except Exception as e:
        logging.error(f"Add knowledge failed: {e}")
        return jsonify({
            'error': 'Failed to add knowledge',
            'details': str(e)
        }), 500


@agent_enhanced_bp.route('/guidance/<topic>', methods=['GET'])
def get_guidance(topic):
    """Get guidance on specific tax topic"""
    if not AGENT_SDK_AVAILABLE:
        return jsonify({'error': 'Enhanced agent system not available'}), 503
    
    try:
        user_type = request.args.get('user_type', 'individual')
        jurisdiction = request.args.get('jurisdiction', 'malta')
        
        # Get guidance asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            response = loop.run_until_complete(
                get_tax_guidance(topic, user_type)
            )
        finally:
            loop.close()
        
        return jsonify({
            'success': True,
            'topic': topic,
            'guidance': response
        })
        
    except Exception as e:
        logging.error(f"Get guidance failed: {e}")
        return jsonify({
            'error': 'Failed to get guidance',
            'details': str(e)
        }), 500


@agent_enhanced_bp.route('/vector-stats', methods=['GET'])
def get_vector_stats():
    """Get vector database statistics"""
    if not AGENT_SDK_AVAILABLE:
        return jsonify({'error': 'Enhanced agent system not available'}), 503
    
    try:
        stats = vector_search_service.get_index_stats()
        
        return jsonify({
            'success': True,
            'vector_database_stats': stats,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logging.error(f"Get vector stats failed: {e}")
        return jsonify({
            'error': 'Failed to get vector statistics',
            'details': str(e)
        }), 500


@agent_enhanced_bp.route('/document-types', methods=['GET'])
def get_document_types():
    """Get available document types for knowledge base"""
    if not AGENT_SDK_AVAILABLE:
        return jsonify({'error': 'Enhanced agent system not available'}), 503
    
    try:
        document_types = []
        
        for doc_type in DocumentType:
            type_info = {
                'type': doc_type.value,
                'name': doc_type.value.replace('_', ' ').title(),
                'description': _get_document_type_description(doc_type)
            }
            document_types.append(type_info)
        
        return jsonify({
            'success': True,
            'document_types': document_types
        })
        
    except Exception as e:
        logging.error(f"Get document types failed: {e}")
        return jsonify({
            'error': 'Failed to get document types',
            'details': str(e)
        }), 500


@agent_enhanced_bp.route('/query-types', methods=['GET'])
def get_query_types():
    """Get available query types"""
    if not AGENT_SDK_AVAILABLE:
        return jsonify({'error': 'Enhanced agent system not available'}), 503
    
    try:
        query_types = []
        
        for query_type in QueryType:
            type_info = {
                'type': query_type.value,
                'name': query_type.value.replace('_', ' ').title(),
                'description': _get_query_type_description(query_type)
            }
            query_types.append(type_info)
        
        return jsonify({
            'success': True,
            'query_types': query_types
        })
        
    except Exception as e:
        logging.error(f"Get query types failed: {e}")
        return jsonify({
            'error': 'Failed to get query types',
            'details': str(e)
        }), 500


@agent_enhanced_bp.route('/batch-knowledge', methods=['POST'])
def add_batch_knowledge():
    """Add multiple documents to knowledge base in batch"""
    if not AGENT_SDK_AVAILABLE:
        return jsonify({'error': 'Enhanced agent system not available'}), 503
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Validate required fields
        if 'documents' not in data:
            return jsonify({'error': 'Documents array is required'}), 400
        
        documents_data = data['documents']
        if not isinstance(documents_data, list):
            return jsonify({'error': 'Documents must be an array'}), 400
        
        # Create VectorDocument objects
        documents = []
        for doc_data in documents_data:
            if 'title' not in doc_data or 'content' not in doc_data:
                continue
            
            # Generate document ID
            import hashlib
            doc_id = hashlib.sha256(f"{doc_data['title']}_{doc_data['content'][:100]}".encode()).hexdigest()[:16]
            
            document = VectorDocument(
                id=doc_id,
                title=doc_data['title'],
                content=doc_data['content'],
                document_type=DocumentType(doc_data.get('document_type', 'unknown')),
                metadata=doc_data.get('metadata', {})
            )
            documents.append(document)
        
        if not documents:
            return jsonify({'error': 'No valid documents provided'}), 400
        
        # Add documents in batch asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            successful, failed = loop.run_until_complete(
                vector_search_service.add_documents_batch(documents)
            )
        finally:
            loop.close()
        
        return jsonify({
            'success': True,
            'message': f'Batch knowledge upload completed',
            'successful_documents': successful,
            'failed_documents': failed,
            'total_documents': len(documents)
        })
        
    except Exception as e:
        logging.error(f"Batch knowledge upload failed: {e}")
        return jsonify({
            'error': 'Failed to upload batch knowledge',
            'details': str(e)
        }), 500


@agent_enhanced_bp.route('/similar-queries', methods=['POST'])
def find_similar_queries():
    """Find similar queries based on semantic similarity"""
    if not AGENT_SDK_AVAILABLE:
        return jsonify({'error': 'Enhanced agent system not available'}), 503
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        if 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data['query']
        max_results = data.get('max_results', 5)
        
        # Search for similar FAQ or guidance documents
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            results = loop.run_until_complete(
                search_knowledge(
                    query, 
                    document_types=['faq', 'guidance_note', 'procedure'],
                    max_results=max_results
                )
            )
        finally:
            loop.close()
        
        # Extract similar queries from results
        similar_queries = []
        for result in results:
            if result.get('score', 0) > 0.7:  # High similarity threshold
                similar_queries.append({
                    'query': result.get('title', ''),
                    'answer': result.get('content', '')[:200] + "...",
                    'similarity_score': result.get('score', 0),
                    'document_type': result.get('document_type', 'unknown')
                })
        
        return jsonify({
            'success': True,
            'query': query,
            'similar_queries': similar_queries,
            'total_found': len(similar_queries)
        })
        
    except Exception as e:
        logging.error(f"Find similar queries failed: {e}")
        return jsonify({
            'error': 'Failed to find similar queries',
            'details': str(e)
        }), 500


def _get_document_type_description(doc_type: DocumentType) -> str:
    """Get description for document type"""
    descriptions = {
        DocumentType.TAX_REGULATION: "Official tax regulations and laws",
        DocumentType.TAX_FORM: "Tax forms and filing documents",
        DocumentType.GUIDANCE_NOTE: "Official guidance notes and instructions",
        DocumentType.CASE_LAW: "Tax case law and legal precedents",
        DocumentType.FAQ: "Frequently asked questions and answers",
        DocumentType.PROCEDURE: "Step-by-step procedures and processes",
        DocumentType.CALCULATION_EXAMPLE: "Tax calculation examples and scenarios",
        DocumentType.TEMPLATE: "Document templates and forms",
        DocumentType.UNKNOWN: "Unclassified documents"
    }
    
    return descriptions.get(doc_type, "Unknown document type")


def _get_query_type_description(query_type: QueryType) -> str:
    """Get description for query type"""
    descriptions = {
        QueryType.TAX_CALCULATION: "Queries about tax calculations and computations",
        QueryType.TAX_REGULATION: "Questions about tax laws and regulations",
        QueryType.FORM_ASSISTANCE: "Help with tax forms and filing",
        QueryType.COMPLIANCE_CHECK: "Compliance verification and checking",
        QueryType.GENERAL_QUESTION: "General tax-related questions",
        QueryType.PROCEDURAL_GUIDANCE: "Step-by-step procedural guidance",
        QueryType.CASE_SPECIFIC: "Specific case or scenario questions",
        QueryType.UNKNOWN: "Unclassified query types"
    }
    
    return descriptions.get(query_type, "Unknown query type")


# Register blueprint with main app
def register_agent_enhanced_routes(app):
    """Register enhanced agent routes with Flask app"""
    app.register_blueprint(agent_enhanced_bp)
    logging.info("Enhanced agent routes registered")

