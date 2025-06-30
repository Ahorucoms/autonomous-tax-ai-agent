"""
Knowledge Base API Routes
Handles knowledge base queries and management
"""

from flask import Blueprint, request, jsonify
import logging

logger = logging.getLogger(__name__)

knowledge_bp = Blueprint('knowledge', __name__)

@knowledge_bp.route('/search', methods=['POST'])
def search_knowledge():
    """Search the knowledge base"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        jurisdiction = data.get('jurisdiction', 'MT')
        language = data.get('language', 'en')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Simulate knowledge base search
        results = [
            {
                'id': 'kb-1',
                'title': 'Malta Income Tax Rates 2025',
                'content': 'Malta operates a progressive income tax system with rates ranging from 0% to 35%...',
                'relevance_score': 0.95,
                'source': 'Malta Tax Authority',
                'last_updated': '2024-01-01T00:00:00Z'
            },
            {
                'id': 'kb-2',
                'title': 'VAT Registration Requirements',
                'content': 'Businesses must register for VAT if their annual turnover exceeds €35,000...',
                'relevance_score': 0.87,
                'source': 'Malta VAT Act',
                'last_updated': '2024-01-01T00:00:00Z'
            }
        ]
        
        return jsonify({
            'success': True,
            'query': query,
            'results': results,
            'total_results': len(results)
        })
        
    except Exception as e:
        logger.error(f"Knowledge search failed: {e}")
        return jsonify({'error': 'Search failed'}), 500

@knowledge_bp.route('/topics', methods=['GET'])
def get_topics():
    """Get available knowledge topics"""
    try:
        jurisdiction = request.args.get('jurisdiction', 'MT')
        language = request.args.get('language', 'en')
        
        topics = [
            {
                'id': 'income_tax',
                'name': 'Income Tax',
                'description': 'Personal and corporate income tax information',
                'article_count': 25
            },
            {
                'id': 'vat',
                'name': 'VAT',
                'description': 'Value Added Tax registration and compliance',
                'article_count': 18
            },
            {
                'id': 'deductions',
                'name': 'Deductions',
                'description': 'Available tax deductions and allowances',
                'article_count': 12
            },
            {
                'id': 'compliance',
                'name': 'Compliance',
                'description': 'Filing requirements and deadlines',
                'article_count': 15
            }
        ]
        
        return jsonify({
            'success': True,
            'topics': topics
        })
        
    except Exception as e:
        logger.error(f"Failed to get topics: {e}")
        return jsonify({'error': 'Failed to retrieve topics'}), 500

@knowledge_bp.route('/articles/<topic_id>', methods=['GET'])
def get_topic_articles(topic_id):
    """Get articles for a specific topic"""
    try:
        articles = [
            {
                'id': 'art-1',
                'title': 'Understanding Malta Income Tax Brackets',
                'summary': 'A comprehensive guide to Malta\'s progressive income tax system',
                'content': 'Malta operates a progressive income tax system...',
                'last_updated': '2024-01-01T00:00:00Z',
                'tags': ['income_tax', 'brackets', 'malta']
            },
            {
                'id': 'art-2',
                'title': 'Married Couple Tax Allowances',
                'summary': 'How married couples can benefit from additional tax allowances',
                'content': 'Married couples in Malta are entitled to additional allowances...',
                'last_updated': '2024-01-01T00:00:00Z',
                'tags': ['income_tax', 'allowances', 'married']
            }
        ]
        
        return jsonify({
            'success': True,
            'topic_id': topic_id,
            'articles': articles
        })
        
    except Exception as e:
        logger.error(f"Failed to get articles for topic {topic_id}: {e}")
        return jsonify({'error': 'Failed to retrieve articles'}), 500

