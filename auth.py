"""
Authentication API Routes
Handles user authentication, registration, and profile management
"""

import logging
from flask import Blueprint, request, jsonify
from typing import Dict, Any

# Import services
from src.services.supabase_client import supabase_client

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/profile', methods=['GET'])
async def get_profile():
    """Get user profile"""
    try:
        # Get user ID from request (in production, extract from JWT token)
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': 'User ID required'}), 401
        
        # Get user profile from database
        profile = await supabase_client.get_user_profile(user_id)
        
        if profile:
            return jsonify({
                'success': True,
                'profile': profile
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Profile not found'
            }), 404
        
    except Exception as e:
        logger.error(f"Failed to get profile: {e}")
        return jsonify({'error': 'Failed to retrieve profile'}), 500

@auth_bp.route('/profile', methods=['POST'])
async def create_profile():
    """Create user profile"""
    try:
        data = request.get_json()
        
        # Get user ID from request
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': 'User ID required'}), 401
        
        # Extract profile data
        profile_data = {
            'employment_status': data.get('employment_status'),
            'marital_status': data.get('marital_status'),
            'number_of_dependents': data.get('number_of_dependents', 0),
            'annual_income': data.get('annual_income'),
            'tax_residency': data.get('tax_residency', 'MT'),
            'business_type': data.get('business_type'),
            'industry': data.get('industry'),
            'preferences': data.get('preferences', {})
        }
        
        # Create profile in database
        profile = await supabase_client.create_user_profile(user_id, profile_data)
        
        # Log analytics event
        await supabase_client.log_analytics_event(
            event_type='profile_created',
            user_id=user_id,
            jurisdiction=profile_data.get('tax_residency'),
            metadata=profile_data
        )
        
        return jsonify({
            'success': True,
            'profile': profile
        })
        
    except Exception as e:
        logger.error(f"Failed to create profile: {e}")
        return jsonify({'error': 'Failed to create profile'}), 500

@auth_bp.route('/profile', methods=['PUT'])
async def update_profile():
    """Update user profile"""
    try:
        data = request.get_json()
        
        # Get user ID from request
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': 'User ID required'}), 401
        
        # Extract profile updates
        profile_updates = {}
        
        allowed_fields = [
            'employment_status', 'marital_status', 'number_of_dependents',
            'annual_income', 'tax_residency', 'business_type', 'industry', 'preferences'
        ]
        
        for field in allowed_fields:
            if field in data:
                profile_updates[field] = data[field]
        
        if not profile_updates:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        # Update profile in database
        profile = await supabase_client.update_user_profile(user_id, profile_updates)
        
        # Log analytics event
        await supabase_client.log_analytics_event(
            event_type='profile_updated',
            user_id=user_id,
            metadata=profile_updates
        )
        
        return jsonify({
            'success': True,
            'profile': profile
        })
        
    except Exception as e:
        logger.error(f"Failed to update profile: {e}")
        return jsonify({'error': 'Failed to update profile'}), 500

@auth_bp.route('/preferences', methods=['GET'])
async def get_preferences():
    """Get user preferences"""
    try:
        # Get user ID from request
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': 'User ID required'}), 401
        
        # Get user profile
        profile = await supabase_client.get_user_profile(user_id)
        
        if profile:
            preferences = profile.get('preferences', {})
            
            # Add default preferences if not set
            default_preferences = {
                'language': 'en',
                'jurisdiction': 'MT',
                'notifications': True,
                'theme': 'light',
                'currency': 'EUR',
                'date_format': 'DD/MM/YYYY',
                'number_format': 'european'
            }
            
            # Merge with user preferences
            for key, value in default_preferences.items():
                if key not in preferences:
                    preferences[key] = value
            
            return jsonify({
                'success': True,
                'preferences': preferences
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Profile not found'
            }), 404
        
    except Exception as e:
        logger.error(f"Failed to get preferences: {e}")
        return jsonify({'error': 'Failed to retrieve preferences'}), 500

@auth_bp.route('/preferences', methods=['PUT'])
async def update_preferences():
    """Update user preferences"""
    try:
        data = request.get_json()
        
        # Get user ID from request
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': 'User ID required'}), 401
        
        # Get current profile
        profile = await supabase_client.get_user_profile(user_id)
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404
        
        # Update preferences
        current_preferences = profile.get('preferences', {})
        
        allowed_preference_fields = [
            'language', 'jurisdiction', 'notifications', 'theme',
            'currency', 'date_format', 'number_format'
        ]
        
        for field in allowed_preference_fields:
            if field in data:
                current_preferences[field] = data[field]
        
        # Update profile with new preferences
        profile = await supabase_client.update_user_profile(
            user_id, 
            {'preferences': current_preferences}
        )
        
        # Log analytics event
        await supabase_client.log_analytics_event(
            event_type='preferences_updated',
            user_id=user_id,
            metadata={'updated_preferences': data}
        )
        
        return jsonify({
            'success': True,
            'preferences': current_preferences
        })
        
    except Exception as e:
        logger.error(f"Failed to update preferences: {e}")
        return jsonify({'error': 'Failed to update preferences'}), 500

@auth_bp.route('/onboarding', methods=['POST'])
async def complete_onboarding():
    """Complete user onboarding process"""
    try:
        data = request.get_json()
        
        # Get user ID from request
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': 'User ID required'}), 401
        
        # Extract onboarding data
        onboarding_data = {
            'employment_status': data.get('employment_status'),
            'marital_status': data.get('marital_status'),
            'number_of_dependents': data.get('number_of_dependents', 0),
            'annual_income': data.get('annual_income'),
            'tax_residency': data.get('tax_residency', 'MT'),
            'business_type': data.get('business_type'),
            'industry': data.get('industry'),
            'preferences': {
                'language': data.get('language', 'en'),
                'jurisdiction': data.get('jurisdiction', 'MT'),
                'notifications': data.get('notifications', True),
                'theme': data.get('theme', 'light'),
                'currency': 'EUR',
                'onboarding_completed': True,
                'onboarding_date': data.get('onboarding_date')
            }
        }
        
        # Check if profile exists
        existing_profile = await supabase_client.get_user_profile(user_id)
        
        if existing_profile:
            # Update existing profile
            profile = await supabase_client.update_user_profile(user_id, onboarding_data)
        else:
            # Create new profile
            profile = await supabase_client.create_user_profile(user_id, onboarding_data)
        
        # Log analytics event
        await supabase_client.log_analytics_event(
            event_type='onboarding_completed',
            user_id=user_id,
            jurisdiction=onboarding_data.get('tax_residency'),
            language=onboarding_data['preferences']['language'],
            metadata=onboarding_data
        )
        
        return jsonify({
            'success': True,
            'profile': profile,
            'message': 'Onboarding completed successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to complete onboarding: {e}")
        return jsonify({'error': 'Failed to complete onboarding'}), 500

@auth_bp.route('/session', methods=['GET'])
async def get_session():
    """Get current user session information"""
    try:
        # Get user ID from request
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': 'User ID required'}), 401
        
        # Get user profile
        profile = await supabase_client.get_user_profile(user_id)
        
        # Build session information
        session_info = {
            'user_id': user_id,
            'authenticated': True,
            'profile_exists': profile is not None,
            'onboarding_completed': False,
            'preferences': {}
        }
        
        if profile:
            session_info['onboarding_completed'] = profile.get('preferences', {}).get('onboarding_completed', False)
            session_info['preferences'] = profile.get('preferences', {})
            session_info['tax_residency'] = profile.get('tax_residency', 'MT')
            session_info['employment_status'] = profile.get('employment_status')
        
        return jsonify({
            'success': True,
            'session': session_info
        })
        
    except Exception as e:
        logger.error(f"Failed to get session: {e}")
        return jsonify({'error': 'Failed to retrieve session'}), 500

@auth_bp.route('/validate', methods=['POST'])
async def validate_token():
    """Validate authentication token"""
    try:
        # In a real implementation, this would validate JWT tokens
        # For now, we'll just check if user ID is provided
        
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({
                'success': False,
                'valid': False,
                'error': 'No user ID provided'
            }), 401
        
        # Check if user profile exists
        profile = await supabase_client.get_user_profile(user_id)
        
        return jsonify({
            'success': True,
            'valid': True,
            'user_id': user_id,
            'profile_exists': profile is not None
        })
        
    except Exception as e:
        logger.error(f"Failed to validate token: {e}")
        return jsonify({
            'success': False,
            'valid': False,
            'error': 'Token validation failed'
        }), 500

