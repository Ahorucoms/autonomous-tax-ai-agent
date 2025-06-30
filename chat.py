"""
Chat API Routes
Handles AI conversation with autonomous reasoning and planning using OpenAI Agents SDK
"""

import asyncio
import logging
from flask import Blueprint, request, jsonify
from typing import Dict, Any, List

from services.agents_sdk import get_autonomous_agent, AgentResponse
from services.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/send', methods=['POST'])
def send_message():
    """Send message to autonomous AI agent"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'error': 'Message is required',
                'status': 'error'
            }), 400
        
        message = data['message']
        user_id = data.get('user_id', 'anonymous')
        context = {
            'jurisdiction': data.get('jurisdiction', 'MT'),
            'language': data.get('language', 'en'),
            'user_type': data.get('user_type', 'individual'),
            'session_id': data.get('session_id')
        }
        
        # Get autonomous agent
        agent = get_autonomous_agent()
        
        # Process request with autonomous reasoning (run async in sync context)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response = loop.run_until_complete(
                agent.process_user_request(user_id, message, context)
            )
        finally:
            loop.close()
        
        # Log conversation to Supabase
        _log_conversation(user_id, message, response, context)
        
        return jsonify({
            'response': response.message,
            'task_status': response.task_status,
            'confidence': response.confidence,
            'requirements_met': response.requirements_met,
            'missing_info': response.missing_info,
            'suggested_actions': response.suggested_actions,
            'generated_content': response.generated_content,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"❌ Chat send error: {e}")
        return jsonify({
            'error': f'Failed to process message: {str(e)}',
            'status': 'error'
        }), 500

@chat_bp.route('/history/<user_id>', methods=['GET'])
def get_chat_history(user_id: str):
    """Get chat history for user"""
    try:
        # Get autonomous agent
        agent = get_autonomous_agent()
        
        # Load user memory
        memory = agent._load_user_memory(user_id)
        
        # Return conversation history
        return jsonify({
            'conversations': memory.conversation_history,
            'task_history': memory.task_history,
            'user_context': memory.user_context,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"❌ Chat history error: {e}")
        return jsonify({
            'error': f'Failed to get chat history: {str(e)}',
            'status': 'error'
        }), 500

@chat_bp.route('/memory/search', methods=['POST'])
def search_memory():
    """Search user memory for relevant information"""
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'error': 'Query is required',
                'status': 'error'
            }), 400
        
        query = data['query']
        user_id = data.get('user_id', 'anonymous')
        
        # Get autonomous agent
        agent = get_autonomous_agent()
        
        # Search memory (run async in sync context)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            results = loop.run_until_complete(
                agent._memory_search_tool(query, user_id)
            )
        finally:
            loop.close()
        
        return jsonify({
            'results': results['results'],
            'count': results['count'],
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"❌ Memory search error: {e}")
        return jsonify({
            'error': f'Failed to search memory: {str(e)}',
            'status': 'error'
        }), 500

@chat_bp.route('/task/analyze', methods=['POST'])
def analyze_task():
    """Analyze user task and identify requirements"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'error': 'Message is required',
                'status': 'error'
            }), 400
        
        message = data['message']
        user_id = data.get('user_id', 'anonymous')
        context = {
            'jurisdiction': data.get('jurisdiction', 'MT'),
            'language': data.get('language', 'en'),
            'user_type': data.get('user_type', 'individual')
        }
        
        # Get autonomous agent
        agent = get_autonomous_agent()
        
        # Load user memory
        memory = agent._load_user_memory(user_id)
        memory.user_context.update(context)
        
        # Analyze task (run async in sync context)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            analysis = loop.run_until_complete(
                agent._analyze_task(message, memory)
            )
        finally:
            loop.close()
        
        return jsonify({
            'task_type': analysis.task_type,
            'jurisdiction': analysis.jurisdiction,
            'complexity': analysis.complexity,
            'requirements': [req.dict() for req in analysis.requirements],
            'missing_info': analysis.missing_info,
            'confidence': analysis.confidence,
            'estimated_duration': analysis.estimated_duration,
            'next_steps': analysis.next_steps,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"❌ Task analysis error: {e}")
        return jsonify({
            'error': f'Failed to analyze task: {str(e)}',
            'status': 'error'
        }), 500

@chat_bp.route('/context/update', methods=['POST'])
def update_context():
    """Update user context information"""
    try:
        data = request.get_json()
        
        if not data or 'user_id' not in data:
            return jsonify({
                'error': 'User ID is required',
                'status': 'error'
            }), 400
        
        user_id = data['user_id']
        context_updates = data.get('context', {})
        
        # Get autonomous agent
        agent = get_autonomous_agent()
        
        # Load and update user memory
        memory = agent._load_user_memory(user_id)
        memory.user_context.update(context_updates)
        
        # Update memory store
        agent.memory_store[user_id] = memory
        
        return jsonify({
            'updated_context': memory.user_context,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"❌ Context update error: {e}")
        return jsonify({
            'error': f'Failed to update context: {str(e)}',
            'status': 'error'
        }), 500

@chat_bp.route('/reasoning/trace/<user_id>', methods=['GET'])
def get_reasoning_trace(user_id: str):
    """Get agent reasoning trace for debugging"""
    try:
        # Get autonomous agent
        agent = get_autonomous_agent()
        
        # Load user memory
        memory = agent._load_user_memory(user_id)
        
        # Extract reasoning information from conversation history
        reasoning_trace = []
        for conv in memory.conversation_history:
            if conv.get('role') == 'assistant':
                reasoning_trace.append({
                    'timestamp': conv.get('timestamp'),
                    'task_status': conv.get('task_status'),
                    'confidence': conv.get('confidence'),
                    'message': conv.get('content')
                })
        
        return jsonify({
            'reasoning_trace': reasoning_trace,
            'total_interactions': len(reasoning_trace),
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"❌ Reasoning trace error: {e}")
        return jsonify({
            'error': f'Failed to get reasoning trace: {str(e)}',
            'status': 'error'
        }), 500

def _log_conversation(user_id: str, 
                     message: str, 
                     response: AgentResponse, 
                     context: Dict[str, Any]):
    """Log conversation to Supabase"""
    try:
        supabase = get_supabase_client()
        
        # Log user message
        supabase.table('conversations').insert({
            'user_id': user_id,
            'role': 'user',
            'content': message,
            'context': context,
            'session_id': context.get('session_id'),
            'jurisdiction': context.get('jurisdiction'),
            'language': context.get('language')
        }).execute()
        
        # Log agent response
        supabase.table('conversations').insert({
            'user_id': user_id,
            'role': 'assistant',
            'content': response.message,
            'context': {
                'task_status': response.task_status,
                'confidence': response.confidence,
                'requirements_met': response.requirements_met,
                'missing_info': response.missing_info,
                'suggested_actions': response.suggested_actions,
                'generated_content': response.generated_content
            },
            'session_id': context.get('session_id'),
            'jurisdiction': context.get('jurisdiction'),
            'language': context.get('language')
        }).execute()
        
        logger.info(f"✅ Conversation logged for user {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Failed to log conversation: {e}")

def register_chat_routes(app):
    """Register chat routes with Flask app"""
    app.register_blueprint(chat_bp, url_prefix='/api/chat')

