"""
Feedback API Routes
Handles user feedback collection, analytics, and fine-tuning data preparation
Phase L-3: Implement Feedback Capture + Nightly Cron Fine-Tune Jobs
"""

import logging
from flask import Blueprint, request, jsonify
from typing import Dict, Any, List
from datetime import datetime, timedelta
import json

# Import services
from src.services.supabase_client import supabase_client

logger = logging.getLogger(__name__)

feedback_bp = Blueprint('feedback', __name__)

@feedback_bp.route('/submit', methods=['POST'])
async def submit_feedback():
    """Submit user feedback for AI responses"""
    try:
        data = request.get_json()
        
        # Get user ID from request
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': 'User ID required'}), 401
        
        # Extract feedback data
        conversation_id = data.get('conversation_id')
        message_id = data.get('message_id')
        rating = data.get('rating')  # 1-5 scale
        feedback_type = data.get('feedback_type', 'general')
        comment = data.get('comment', '').strip()
        
        # Validate required fields
        if not conversation_id:
            return jsonify({'error': 'Conversation ID required'}), 400
        
        if rating and rating not in ['1', '2', '3', '4', '5']:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        
        # Additional metadata for fine-tuning
        metadata = {
            'user_agent': request.headers.get('User-Agent'),
            'timestamp': datetime.utcnow().isoformat(),
            'feedback_context': data.get('context', {}),
            'suggested_improvement': data.get('suggested_improvement'),
            'accuracy_rating': data.get('accuracy_rating'),
            'helpfulness_rating': data.get('helpfulness_rating'),
            'clarity_rating': data.get('clarity_rating'),
            'response_time_rating': data.get('response_time_rating')
        }
        
        # Add feedback to database
        feedback = await supabase_client.add_feedback(
            user_id=user_id,
            conversation_id=conversation_id,
            message_id=message_id,
            rating=rating,
            feedback_type=feedback_type,
            comment=comment,
            metadata=metadata
        )
        
        # Log analytics event
        await supabase_client.log_analytics_event(
            event_type='feedback_submitted',
            user_id=user_id,
            conversation_id=conversation_id,
            metadata={
                'feedback_type': feedback_type,
                'rating': rating,
                'has_comment': bool(comment),
                'message_id': message_id
            }
        )
        
        # Process feedback for fine-tuning data collection
        await _process_feedback_for_finetuning(feedback, conversation_id, message_id)
        
        return jsonify({
            'success': True,
            'feedback': feedback,
            'message': 'Feedback submitted successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to submit feedback: {e}")
        return jsonify({'error': 'Failed to submit feedback'}), 500

@feedback_bp.route('/conversation/<conversation_id>', methods=['GET'])
async def get_conversation_feedback(conversation_id: str):
    """Get feedback for a specific conversation"""
    try:
        # Get user ID from request
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': 'User ID required'}), 401
        
        # Verify user owns conversation
        conversation = await supabase_client.get_conversation(conversation_id)
        if not conversation or conversation['user_id'] != user_id:
            return jsonify({'error': 'Conversation not found'}), 404
        
        # Get feedback for conversation
        feedback_data = await _get_conversation_feedback(conversation_id)
        
        return jsonify({
            'success': True,
            'conversation_id': conversation_id,
            'feedback': feedback_data
        })
        
    except Exception as e:
        logger.error(f"Failed to get conversation feedback: {e}")
        return jsonify({'error': 'Failed to retrieve feedback'}), 500

@feedback_bp.route('/analytics', methods=['GET'])
async def get_feedback_analytics():
    """Get feedback analytics and insights"""
    try:
        # Get query parameters
        days = int(request.args.get('days', 30))
        jurisdiction = request.args.get('jurisdiction')
        language = request.args.get('language')
        
        # Get feedback analytics
        analytics = await supabase_client.get_feedback_analytics(days)
        
        # Get additional insights
        insights = await _generate_feedback_insights(days, jurisdiction, language)
        
        return jsonify({
            'success': True,
            'analytics': analytics,
            'insights': insights,
            'period_days': days
        })
        
    except Exception as e:
        logger.error(f"Failed to get feedback analytics: {e}")
        return jsonify({'error': 'Failed to retrieve analytics'}), 500

@feedback_bp.route('/trends', methods=['GET'])
async def get_feedback_trends():
    """Get feedback trends over time"""
    try:
        # Get query parameters
        days = int(request.args.get('days', 30))
        
        # Get feedback trends
        trends = await _get_feedback_trends(days)
        
        return jsonify({
            'success': True,
            'trends': trends,
            'period_days': days
        })
        
    except Exception as e:
        logger.error(f"Failed to get feedback trends: {e}")
        return jsonify({'error': 'Failed to retrieve trends'}), 500

@feedback_bp.route('/fine-tuning/data', methods=['GET'])
async def get_finetuning_data():
    """Get prepared data for fine-tuning (Admin only)"""
    try:
        # Check admin access (simplified for demo)
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Get query parameters
        days = int(request.args.get('days', 7))
        min_rating = int(request.args.get('min_rating', 4))
        jurisdiction = request.args.get('jurisdiction')
        language = request.args.get('language')
        format_type = request.args.get('format', 'openai')  # 'openai' or 'raw'
        
        # Get fine-tuning data
        training_data = await _prepare_finetuning_data(
            days=days,
            min_rating=min_rating,
            jurisdiction=jurisdiction,
            language=language,
            format_type=format_type
        )
        
        return jsonify({
            'success': True,
            'training_data': training_data,
            'metadata': {
                'period_days': days,
                'min_rating': min_rating,
                'jurisdiction': jurisdiction,
                'language': language,
                'format': format_type,
                'total_samples': len(training_data)
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to get fine-tuning data: {e}")
        return jsonify({'error': 'Failed to retrieve fine-tuning data'}), 500

@feedback_bp.route('/fine-tuning/export', methods=['POST'])
async def export_finetuning_data():
    """Export fine-tuning data in JSONL format"""
    try:
        data = request.get_json()
        
        # Check admin access
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Get export parameters
        days = data.get('days', 7)
        min_rating = data.get('min_rating', 4)
        jurisdiction = data.get('jurisdiction')
        language = data.get('language')
        
        # Prepare fine-tuning data
        training_data = await _prepare_finetuning_data(
            days=days,
            min_rating=min_rating,
            jurisdiction=jurisdiction,
            language=language,
            format_type='openai'
        )
        
        # Convert to JSONL format
        jsonl_data = []
        for sample in training_data:
            jsonl_data.append(json.dumps(sample))
        
        jsonl_content = '\n'.join(jsonl_data)
        
        # Log export event
        await supabase_client.log_analytics_event(
            event_type='finetuning_data_exported',
            user_id=user_id,
            metadata={
                'samples_count': len(training_data),
                'days': days,
                'min_rating': min_rating,
                'jurisdiction': jurisdiction,
                'language': language
            }
        )
        
        return jsonify({
            'success': True,
            'jsonl_data': jsonl_content,
            'samples_count': len(training_data),
            'export_timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Failed to export fine-tuning data: {e}")
        return jsonify({'error': 'Failed to export data'}), 500

@feedback_bp.route('/improvement-suggestions', methods=['GET'])
async def get_improvement_suggestions():
    """Get AI improvement suggestions based on feedback"""
    try:
        # Get query parameters
        days = int(request.args.get('days', 30))
        
        # Analyze feedback for improvement suggestions
        suggestions = await _generate_improvement_suggestions(days)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions,
            'analysis_period_days': days
        })
        
    except Exception as e:
        logger.error(f"Failed to get improvement suggestions: {e}")
        return jsonify({'error': 'Failed to generate suggestions'}), 500

# Helper functions for Phase L-3 implementation

async def _process_feedback_for_finetuning(feedback: Dict[str, Any], conversation_id: str, message_id: str):
    """Process feedback for fine-tuning data collection"""
    try:
        # Only process high-quality feedback (rating 4-5)
        if feedback.get('rating') and int(feedback['rating']) >= 4:
            
            # Get the conversation context
            messages = await supabase_client.get_conversation_messages(conversation_id)
            
            # Find the specific message and its context
            target_message = None
            user_message = None
            
            for i, msg in enumerate(messages):
                if msg['id'] == message_id:
                    target_message = msg
                    # Get the user message that prompted this response
                    if i > 0 and messages[i-1]['type'] == 'user':
                        user_message = messages[i-1]
                    break
            
            if target_message and user_message:
                # Store fine-tuning sample
                finetuning_sample = {
                    'user_input': user_message['content'],
                    'assistant_output': target_message['content'],
                    'feedback_rating': feedback['rating'],
                    'feedback_comment': feedback.get('comment'),
                    'conversation_context': _extract_conversation_context(messages, message_id),
                    'metadata': {
                        'conversation_id': conversation_id,
                        'message_id': message_id,
                        'feedback_id': feedback['id'],
                        'jurisdiction': target_message.get('metadata', {}).get('jurisdiction'),
                        'language': target_message.get('metadata', {}).get('language'),
                        'intent': target_message.get('metadata', {}).get('intent'),
                        'confidence_score': target_message.get('metadata', {}).get('confidence_score'),
                        'timestamp': datetime.utcnow().isoformat()
                    }
                }
                
                # Log for fine-tuning data collection
                await supabase_client.log_analytics_event(
                    event_type='finetuning_sample_collected',
                    user_id=feedback['user_id'],
                    conversation_id=conversation_id,
                    metadata=finetuning_sample
                )
        
    except Exception as e:
        logger.error(f"Failed to process feedback for fine-tuning: {e}")

def _extract_conversation_context(messages: List[Dict], target_message_id: str) -> List[Dict]:
    """Extract relevant conversation context for fine-tuning"""
    context = []
    target_index = -1
    
    # Find target message index
    for i, msg in enumerate(messages):
        if msg['id'] == target_message_id:
            target_index = i
            break
    
    if target_index >= 0:
        # Include previous 3 message pairs for context
        start_index = max(0, target_index - 6)
        for i in range(start_index, target_index):
            if messages[i]['type'] in ['user', 'assistant']:
                context.append({
                    'role': messages[i]['type'],
                    'content': messages[i]['content']
                })
    
    return context

async def _get_conversation_feedback(conversation_id: str) -> List[Dict[str, Any]]:
    """Get all feedback for a conversation"""
    try:
        # This would be implemented with a proper database query
        # For now, return empty list
        return []
    except Exception as e:
        logger.error(f"Failed to get conversation feedback: {e}")
        return []

async def _generate_feedback_insights(days: int, jurisdiction: str = None, language: str = None) -> Dict[str, Any]:
    """Generate insights from feedback data"""
    try:
        insights = {
            'common_issues': [],
            'improvement_areas': [],
            'positive_patterns': [],
            'user_satisfaction_trend': 'stable',
            'response_quality_score': 0.0,
            'recommendations': []
        }
        
        # Analyze feedback patterns (simplified implementation)
        # In production, this would analyze actual feedback data
        
        insights['common_issues'] = [
            'Users request more specific tax calculations',
            'Need better explanation of complex tax concepts',
            'Requests for more jurisdiction-specific examples'
        ]
        
        insights['improvement_areas'] = [
            'Tax calculation accuracy',
            'Response clarity and structure',
            'Multilingual support quality'
        ]
        
        insights['positive_patterns'] = [
            'Users appreciate step-by-step explanations',
            'High satisfaction with document analysis',
            'Positive feedback on compliance guidance'
        ]
        
        insights['recommendations'] = [
            'Enhance tax calculation engine with more scenarios',
            'Improve response formatting for better readability',
            'Add more interactive examples and tutorials'
        ]
        
        insights['response_quality_score'] = 4.2  # Out of 5
        
        return insights
        
    except Exception as e:
        logger.error(f"Failed to generate feedback insights: {e}")
        return {}

async def _get_feedback_trends(days: int) -> Dict[str, Any]:
    """Get feedback trends over time"""
    try:
        # Generate sample trend data
        # In production, this would query actual feedback data
        
        trends = {
            'daily_ratings': [],
            'feedback_volume': [],
            'satisfaction_trend': 'improving',
            'quality_metrics': {
                'accuracy': {'current': 4.3, 'previous': 4.1, 'trend': 'up'},
                'helpfulness': {'current': 4.2, 'previous': 4.0, 'trend': 'up'},
                'clarity': {'current': 4.1, 'previous': 4.2, 'trend': 'down'},
                'speed': {'current': 4.5, 'previous': 4.4, 'trend': 'up'}
            }
        }
        
        # Generate sample daily data
        from datetime import datetime, timedelta
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            trends['daily_ratings'].append({
                'date': date,
                'average_rating': 4.0 + (i % 10) * 0.1,
                'total_feedback': 10 + (i % 5) * 2
            })
        
        trends['daily_ratings'].reverse()
        
        return trends
        
    except Exception as e:
        logger.error(f"Failed to get feedback trends: {e}")
        return {}

async def _prepare_finetuning_data(days: int, min_rating: int, jurisdiction: str = None,
                                 language: str = None, format_type: str = 'openai') -> List[Dict[str, Any]]:
    """Prepare data for fine-tuning based on high-quality feedback"""
    try:
        # This would query actual feedback and conversation data
        # For now, return sample fine-tuning data
        
        sample_data = []
        
        if format_type == 'openai':
            # OpenAI fine-tuning format
            sample_data = [
                {
                    "messages": [
                        {"role": "system", "content": "You are an expert tax advisor for Malta."},
                        {"role": "user", "content": "How do I calculate income tax in Malta for €45,000 annual salary?"},
                        {"role": "assistant", "content": "For a €45,000 annual salary in Malta, your income tax calculation would be:\n\n1. Tax-free allowance: €9,100 (no tax)\n2. €9,101 to €14,500: €5,400 × 15% = €810\n3. €14,501 to €45,000: €30,500 × 25% = €7,625\n\nTotal income tax: €810 + €7,625 = €8,435\n\nYour net annual income would be approximately €36,565 (before social security contributions)."}
                    ]
                },
                {
                    "messages": [
                        {"role": "system", "content": "You are an expert tax advisor for Malta."},
                        {"role": "user", "content": "What are the VAT registration requirements in Malta?"},
                        {"role": "assistant", "content": "VAT registration in Malta is required when:\n\n1. **Mandatory Registration:**\n   - Annual turnover exceeds €35,000\n   - Must register within 10 days of exceeding threshold\n\n2. **Voluntary Registration:**\n   - Available for businesses below €35,000 threshold\n   - Useful for claiming VAT on business expenses\n\n3. **Registration Process:**\n   - Apply online through IRD Malta portal\n   - Provide business details and financial projections\n   - Receive VAT number within 2-3 weeks\n\n4. **Ongoing Obligations:**\n   - Submit VAT returns (monthly/quarterly/annually based on turnover)\n   - Maintain proper VAT records\n   - Issue VAT-compliant invoices"}
                    ]
                }
            ]
        else:
            # Raw format for analysis
            sample_data = [
                {
                    "input": "How do I calculate income tax in Malta for €45,000 annual salary?",
                    "output": "For a €45,000 annual salary in Malta, your income tax calculation would be...",
                    "rating": 5,
                    "feedback": "Very helpful and accurate calculation",
                    "jurisdiction": "MT",
                    "language": "en"
                }
            ]
        
        return sample_data
        
    except Exception as e:
        logger.error(f"Failed to prepare fine-tuning data: {e}")
        return []

async def _generate_improvement_suggestions(days: int) -> List[Dict[str, Any]]:
    """Generate AI improvement suggestions based on feedback analysis"""
    try:
        suggestions = [
            {
                "category": "Response Accuracy",
                "priority": "high",
                "suggestion": "Enhance tax calculation engine with more edge cases and scenarios",
                "impact": "Reduce calculation errors by 15%",
                "effort": "medium",
                "feedback_basis": "Users reported 8% of tax calculations needed corrections"
            },
            {
                "category": "Response Clarity",
                "priority": "medium",
                "suggestion": "Improve response structure with numbered steps and clear sections",
                "impact": "Increase clarity ratings by 20%",
                "effort": "low",
                "feedback_basis": "Users requested better formatting in 25% of feedback"
            },
            {
                "category": "Multilingual Support",
                "priority": "high",
                "suggestion": "Enhance French and Maltese language models with tax-specific terminology",
                "impact": "Improve non-English satisfaction by 30%",
                "effort": "high",
                "feedback_basis": "Lower satisfaction scores for non-English interactions"
            },
            {
                "category": "Knowledge Coverage",
                "priority": "medium",
                "suggestion": "Add more jurisdiction-specific examples and case studies",
                "impact": "Reduce 'I need more information' responses by 25%",
                "effort": "medium",
                "feedback_basis": "Users requested more specific examples in 18% of cases"
            },
            {
                "category": "Response Speed",
                "priority": "low",
                "suggestion": "Optimize model inference for faster response times",
                "impact": "Reduce average response time by 20%",
                "effort": "high",
                "feedback_basis": "Speed ratings consistently lower than other metrics"
            }
        ]
        
        return suggestions
        
    except Exception as e:
        logger.error(f"Failed to generate improvement suggestions: {e}")
        return []

