"""
Supabase Client Service
Handles all database operations and authentication
"""

import os
import logging
from typing import Dict, List, Any, Optional
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class SupabaseService:
    """Service for Supabase database operations"""
    
    def __init__(self):
        """Initialize Supabase client"""
        self.url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        self.anon_key = os.getenv('SUPABASE_ANON_KEY')
        
        if not self.url or not self.key:
            raise ValueError("Missing Supabase credentials in environment variables")
        
        try:
            # Create service role client for backend operations
            self.client: Client = create_client(self.url, self.key)
            
            # Create anon client for frontend operations
            self.anon_client: Client = create_client(self.url, self.anon_key)
            
            logger.info("✅ Supabase client initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase client: {e}")
            raise
    
    # =============================================
    # USER MANAGEMENT
    # =============================================
    
    async def create_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create user profile"""
        try:
            response = self.client.table('user_profiles').insert({
                'user_id': user_id,
                **profile_data
            }).execute()
            
            return response.data[0] if response.data else {}
            
        except Exception as e:
            logger.error(f"Failed to create user profile: {e}")
            raise
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile"""
        try:
            response = self.client.table('user_profiles').select('*').eq('user_id', user_id).execute()
            
            return response.data[0] if response.data else None
            
        except Exception as e:
            logger.error(f"Failed to get user profile: {e}")
            return None
    
    async def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile"""
        try:
            response = self.client.table('user_profiles').update(profile_data).eq('user_id', user_id).execute()
            
            return response.data[0] if response.data else {}
            
        except Exception as e:
            logger.error(f"Failed to update user profile: {e}")
            raise
    
    # =============================================
    # CONVERSATION MANAGEMENT
    # =============================================
    
    async def create_conversation(self, user_id: str, title: str, language: str = 'en', 
                                jurisdiction: str = 'MT') -> Dict[str, Any]:
        """Create new conversation"""
        try:
            response = self.client.table('conversations').insert({
                'user_id': user_id,
                'title': title,
                'language': language,
                'jurisdiction': jurisdiction,
                'status': 'active'
            }).execute()
            
            return response.data[0] if response.data else {}
            
        except Exception as e:
            logger.error(f"Failed to create conversation: {e}")
            raise
    
    async def get_user_conversations(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user conversations"""
        try:
            response = self.client.table('conversations').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(limit).execute()
            
            return response.data or []
            
        except Exception as e:
            logger.error(f"Failed to get user conversations: {e}")
            return []
    
    async def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get specific conversation"""
        try:
            response = self.client.table('conversations').select('*').eq('id', conversation_id).execute()
            
            return response.data[0] if response.data else None
            
        except Exception as e:
            logger.error(f"Failed to get conversation: {e}")
            return None
    
    async def update_conversation(self, conversation_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update conversation"""
        try:
            response = self.client.table('conversations').update(updates).eq('id', conversation_id).execute()
            
            return response.data[0] if response.data else {}
            
        except Exception as e:
            logger.error(f"Failed to update conversation: {e}")
            raise
    
    # =============================================
    # MESSAGE MANAGEMENT
    # =============================================
    
    async def add_message(self, conversation_id: str, message_type: str, content: str,
                         metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add message to conversation"""
        try:
            response = self.client.table('messages').insert({
                'conversation_id': conversation_id,
                'type': message_type,
                'content': content,
                'metadata': metadata or {}
            }).execute()
            
            return response.data[0] if response.data else {}
            
        except Exception as e:
            logger.error(f"Failed to add message: {e}")
            raise
    
    async def get_conversation_messages(self, conversation_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get messages for conversation"""
        try:
            response = self.client.table('messages').select('*').eq('conversation_id', conversation_id).order('created_at', desc=False).limit(limit).execute()
            
            return response.data or []
            
        except Exception as e:
            logger.error(f"Failed to get conversation messages: {e}")
            return []
    
    # =============================================
    # DOCUMENT MANAGEMENT
    # =============================================
    
    async def create_document_record(self, user_id: str, filename: str, file_path: str,
                                   file_size: int, mime_type: str, document_type: str = 'other',
                                   conversation_id: str = None) -> Dict[str, Any]:
        """Create document record"""
        try:
            response = self.client.table('documents').insert({
                'user_id': user_id,
                'conversation_id': conversation_id,
                'filename': filename,
                'original_filename': filename,
                'file_path': file_path,
                'file_size': file_size,
                'mime_type': mime_type,
                'document_type': document_type,
                'is_processed': False,
                'processing_status': 'pending'
            }).execute()
            
            return response.data[0] if response.data else {}
            
        except Exception as e:
            logger.error(f"Failed to create document record: {e}")
            raise
    
    async def get_user_documents(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user documents"""
        try:
            response = self.client.table('documents').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(limit).execute()
            
            return response.data or []
            
        except Exception as e:
            logger.error(f"Failed to get user documents: {e}")
            return []
    
    async def update_document_processing(self, document_id: str, status: str, 
                                       extracted_text: str = None, error: str = None) -> Dict[str, Any]:
        """Update document processing status"""
        try:
            updates = {
                'processing_status': status,
                'is_processed': status == 'completed'
            }
            
            if extracted_text:
                updates['extracted_text'] = extracted_text
            
            if error:
                updates['processing_error'] = error
            
            response = self.client.table('documents').update(updates).eq('id', document_id).execute()
            
            return response.data[0] if response.data else {}
            
        except Exception as e:
            logger.error(f"Failed to update document processing: {e}")
            raise
    
    # =============================================
    # KNOWLEDGE BASE MANAGEMENT
    # =============================================
    
    async def add_knowledge_entry(self, title: str, content: str, document_type: str,
                                jurisdiction: str, language: str, source_authority: str = None,
                                tags: List[str] = None, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add knowledge base entry"""
        try:
            response = self.client.table('knowledge_base').insert({
                'title': title,
                'content': content,
                'document_type': document_type,
                'jurisdiction': jurisdiction,
                'language': language,
                'source_authority': source_authority,
                'tags': tags or [],
                'metadata': metadata or {},
                'is_active': True
            }).execute()
            
            return response.data[0] if response.data else {}
            
        except Exception as e:
            logger.error(f"Failed to add knowledge entry: {e}")
            raise
    
    async def search_knowledge_base(self, query: str, jurisdiction: str = None, 
                                  language: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search knowledge base"""
        try:
            query_builder = self.client.table('knowledge_base').select('*')
            
            if jurisdiction:
                query_builder = query_builder.eq('jurisdiction', jurisdiction)
            
            if language:
                query_builder = query_builder.eq('language', language)
            
            # Simple text search (in production, use full-text search or vector search)
            query_builder = query_builder.ilike('content', f'%{query}%')
            
            response = query_builder.eq('is_active', True).limit(limit).execute()
            
            return response.data or []
            
        except Exception as e:
            logger.error(f"Failed to search knowledge base: {e}")
            return []
    
    # =============================================
    # FEEDBACK MANAGEMENT
    # =============================================
    
    async def add_feedback(self, user_id: str, conversation_id: str = None, message_id: str = None,
                         rating: str = None, feedback_type: str = 'general', comment: str = None,
                         metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add user feedback"""
        try:
            response = self.client.table('feedback').insert({
                'user_id': user_id,
                'conversation_id': conversation_id,
                'message_id': message_id,
                'rating': rating,
                'feedback_type': feedback_type,
                'comment': comment,
                'metadata': metadata or {}
            }).execute()
            
            return response.data[0] if response.data else {}
            
        except Exception as e:
            logger.error(f"Failed to add feedback: {e}")
            raise
    
    async def get_feedback_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get feedback analytics"""
        try:
            # Get feedback from last N days
            response = self.client.table('feedback').select('*').gte('created_at', f'now() - interval \'{days} days\'').execute()
            
            feedback_data = response.data or []
            
            # Calculate analytics
            total_feedback = len(feedback_data)
            ratings = [f['rating'] for f in feedback_data if f['rating']]
            
            analytics = {
                'total_feedback': total_feedback,
                'average_rating': sum(int(r) for r in ratings) / len(ratings) if ratings else 0,
                'rating_distribution': {},
                'feedback_types': {},
                'recent_comments': []
            }
            
            # Rating distribution
            for rating in ['1', '2', '3', '4', '5']:
                analytics['rating_distribution'][rating] = ratings.count(rating)
            
            # Feedback types
            for feedback in feedback_data:
                feedback_type = feedback['feedback_type']
                analytics['feedback_types'][feedback_type] = analytics['feedback_types'].get(feedback_type, 0) + 1
            
            # Recent comments
            comments = [f for f in feedback_data if f['comment']]
            analytics['recent_comments'] = sorted(comments, key=lambda x: x['created_at'], reverse=True)[:10]
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get feedback analytics: {e}")
            return {}
    
    # =============================================
    # ANALYTICS AND LOGGING
    # =============================================
    
    async def log_analytics_event(self, event_type: str, user_id: str = None, 
                                conversation_id: str = None, jurisdiction: str = None,
                                language: str = None, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Log analytics event"""
        try:
            response = self.client.table('analytics').insert({
                'event_type': event_type,
                'user_id': user_id,
                'conversation_id': conversation_id,
                'jurisdiction': jurisdiction,
                'language': language,
                'metadata': metadata or {}
            }).execute()
            
            return response.data[0] if response.data else {}
            
        except Exception as e:
            logger.error(f"Failed to log analytics event: {e}")
            return {}
    
    async def get_analytics_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get analytics summary"""
        try:
            # Get analytics from last N days
            response = self.client.table('analytics').select('*').gte('created_at', f'now() - interval \'{days} days\'').execute()
            
            analytics_data = response.data or []
            
            # Calculate summary
            summary = {
                'total_events': len(analytics_data),
                'unique_users': len(set(a['user_id'] for a in analytics_data if a['user_id'])),
                'event_types': {},
                'jurisdictions': {},
                'languages': {}
            }
            
            for event in analytics_data:
                # Event types
                event_type = event['event_type']
                summary['event_types'][event_type] = summary['event_types'].get(event_type, 0) + 1
                
                # Jurisdictions
                if event['jurisdiction']:
                    jurisdiction = event['jurisdiction']
                    summary['jurisdictions'][jurisdiction] = summary['jurisdictions'].get(jurisdiction, 0) + 1
                
                # Languages
                if event['language']:
                    language = event['language']
                    summary['languages'][language] = summary['languages'].get(language, 0) + 1
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get analytics summary: {e}")
            return {}
    
    # =============================================
    # JURISDICTIONS AND FORMS
    # =============================================
    
    async def get_jurisdictions(self) -> List[Dict[str, Any]]:
        """Get all active jurisdictions"""
        try:
            response = self.client.table('jurisdictions').select('*').eq('is_active', True).execute()
            
            return response.data or []
            
        except Exception as e:
            logger.error(f"Failed to get jurisdictions: {e}")
            return []
    
    async def get_tax_forms(self, jurisdiction: str, language: str = 'en') -> List[Dict[str, Any]]:
        """Get tax forms for jurisdiction"""
        try:
            response = self.client.table('tax_forms').select('*').eq('jurisdiction', jurisdiction).eq('language', language).eq('is_active', True).execute()
            
            return response.data or []
            
        except Exception as e:
            logger.error(f"Failed to get tax forms: {e}")
            return []

# Global instance
supabase_client = SupabaseService()

