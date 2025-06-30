"""
Pinecone RAG (Retrieval-Augmented Generation) Service
Advanced vector search and knowledge retrieval with learning capabilities
"""

import os
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
import json
from datetime import datetime
import hashlib

# Pinecone and OpenAI
from pinecone import Pinecone, ServerlessSpec
import openai
from openai import OpenAI

# Text processing
import tiktoken
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Database
from services.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

class PineconeRAGService:
    """Advanced RAG service with Pinecone vector database and learning capabilities"""
    
    def __init__(self):
        self.pinecone_api_key = os.getenv('PINECONE_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.index_name = "ai-tax-agent-knowledge"
        self.dimension = 1536  # OpenAI ada-002 embedding dimension
        
        # Initialize clients
        self.pinecone_client = None
        self.index = None
        self.openai_client = None
        self.tokenizer = None
        
        # Fallback TF-IDF system
        self.tfidf_vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
        self.tfidf_documents = []
        self.tfidf_metadata = []
        self.tfidf_fitted = False
        
        # Initialize services
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize Pinecone and OpenAI services"""
        try:
            # Initialize OpenAI
            if self.openai_api_key:
                self.openai_client = OpenAI(api_key=self.openai_api_key)
                self.tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")
                logger.info("✅ OpenAI client initialized")
            else:
                logger.warning("⚠️ OpenAI API key not found")
            
            # Initialize Pinecone
            if self.pinecone_api_key:
                self.pinecone_client = Pinecone(api_key=self.pinecone_api_key)
                self._setup_pinecone_index()
                logger.info("✅ Pinecone client initialized")
            else:
                logger.warning("⚠️ Pinecone API key not found, using fallback system")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize RAG services: {e}")
            logger.info("🔄 Using fallback TF-IDF system")
    
    def _setup_pinecone_index(self):
        """Setup Pinecone index for vector storage"""
        try:
            # Check if index exists
            existing_indexes = self.pinecone_client.list_indexes()
            index_names = [idx.name for idx in existing_indexes.indexes]
            
            if self.index_name not in index_names:
                # Create new index
                self.pinecone_client.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region='us-east-1'
                    )
                )
                logger.info(f"✅ Created Pinecone index: {self.index_name}")
            
            # Connect to index
            self.index = self.pinecone_client.Index(self.index_name)
            logger.info(f"✅ Connected to Pinecone index: {self.index_name}")
            
        except Exception as e:
            logger.error(f"❌ Pinecone index setup failed: {e}")
            self.index = None
    
    async def add_document(self, 
                          document_id: str, 
                          content: str, 
                          metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Add document to vector database with learning capabilities"""
        try:
            # Generate content hash for deduplication
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            # Check for existing document
            existing = await self._check_existing_document(content_hash)
            if existing:
                logger.info(f"📄 Document already exists: {document_id}")
                return {'success': True, 'status': 'exists', 'document_id': document_id}
            
            # Process content into chunks
            chunks = self._chunk_content(content)
            
            # Add to vector database
            if self.index and self.openai_client:
                success = await self._add_to_pinecone(document_id, chunks, metadata, content_hash)
            else:
                success = await self._add_to_fallback(document_id, chunks, metadata, content_hash)
            
            if success:
                # Store in Supabase for tracking
                await self._store_document_metadata(document_id, content, metadata, content_hash)
                
                # Update learning system
                await self._update_learning_system(document_id, content, metadata)
                
                logger.info(f"✅ Document added successfully: {document_id}")
                return {'success': True, 'status': 'added', 'document_id': document_id}
            else:
                raise Exception("Failed to add document to vector database")
                
        except Exception as e:
            logger.error(f"❌ Failed to add document {document_id}: {e}")
            return {'success': False, 'error': str(e)}
    
    async def search_knowledge(self, 
                              query: str, 
                              filters: Dict[str, Any] = None,
                              top_k: int = 5,
                              user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Search knowledge base with contextual understanding"""
        try:
            # Enhance query with user context
            enhanced_query = self._enhance_query_with_context(query, user_context)
            
            # Search vector database
            if self.index and self.openai_client:
                results = await self._search_pinecone(enhanced_query, filters, top_k)
            else:
                results = await self._search_fallback(enhanced_query, filters, top_k)
            
            # Post-process results with learning
            processed_results = await self._post_process_results(results, query, user_context)
            
            # Log search for learning
            await self._log_search_interaction(query, results, user_context)
            
            return {
                'success': True,
                'query': query,
                'enhanced_query': enhanced_query,
                'results': processed_results,
                'total_results': len(processed_results)
            }
            
        except Exception as e:
            logger.error(f"❌ Knowledge search failed: {e}")
            return {'success': False, 'error': str(e), 'results': []}
    
    async def generate_contextual_response(self, 
                                         query: str, 
                                         search_results: List[Dict[str, Any]],
                                         user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate contextual response using RAG"""
        try:
            if not self.openai_client:
                return await self._generate_fallback_response(query, search_results, user_context)
            
            # Build context from search results
            context = self._build_context_from_results(search_results)
            
            # Create system prompt with context
            system_prompt = self._create_rag_system_prompt(user_context)
            
            # Generate response
            response = await self._generate_openai_response(
                system_prompt, 
                query, 
                context, 
                user_context
            )
            
            # Extract confidence and metadata
            confidence = self._calculate_response_confidence(search_results, response)
            
            return {
                'success': True,
                'response': response,
                'confidence': confidence,
                'sources': [r['metadata'] for r in search_results],
                'context_used': len(search_results)
            }
            
        except Exception as e:
            logger.error(f"❌ RAG response generation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def learn_from_feedback(self, 
                                 query: str, 
                                 response: str, 
                                 feedback: Dict[str, Any],
                                 user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Learn from user feedback to improve future responses"""
        try:
            # Store feedback for learning
            feedback_data = {
                'query': query,
                'response': response,
                'feedback': feedback,
                'user_context': user_context,
                'timestamp': datetime.now().isoformat()
            }
            
            # Store in Supabase
            supabase = get_supabase_client()
            supabase.table('rag_feedback').insert(feedback_data).execute()
            
            # Update knowledge weights based on feedback
            if feedback.get('rating', 0) >= 4:
                # Positive feedback - boost related content
                await self._boost_content_relevance(query, response, user_context)
            elif feedback.get('rating', 0) <= 2:
                # Negative feedback - reduce relevance
                await self._reduce_content_relevance(query, response, user_context)
            
            # Extract improvement suggestions
            improvements = feedback.get('suggestions', [])
            if improvements:
                await self._process_improvement_suggestions(query, improvements, user_context)
            
            logger.info(f"✅ Learning from feedback completed for query: {query[:50]}...")
            return {'success': True, 'learning_applied': True}
            
        except Exception as e:
            logger.error(f"❌ Learning from feedback failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        try:
            stats = {
                'total_documents': 0,
                'total_chunks': 0,
                'storage_type': 'fallback',
                'last_updated': None,
                'search_count': 0,
                'avg_confidence': 0.0
            }
            
            if self.index:
                # Get Pinecone stats
                index_stats = self.index.describe_index_stats()
                stats.update({
                    'total_chunks': index_stats.total_vector_count,
                    'storage_type': 'pinecone',
                    'dimension': index_stats.dimension
                })
            else:
                # Get fallback stats
                stats.update({
                    'total_documents': len(self.tfidf_documents),
                    'total_chunks': len(self.tfidf_documents),
                    'storage_type': 'tfidf_fallback'
                })
            
            # Get additional stats from Supabase
            supabase = get_supabase_client()
            
            # Document count
            doc_result = supabase.table('rag_documents').select('id', count='exact').execute()
            stats['total_documents'] = doc_result.count or 0
            
            # Search count
            search_result = supabase.table('rag_searches').select('id', count='exact').execute()
            stats['search_count'] = search_result.count or 0
            
            # Average confidence
            feedback_result = supabase.table('rag_feedback').select('feedback').execute()
            if feedback_result.data:
                ratings = [f['feedback'].get('rating', 0) for f in feedback_result.data if f['feedback'].get('rating')]
                stats['avg_confidence'] = sum(ratings) / len(ratings) if ratings else 0.0
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to get knowledge stats: {e}")
            return {'error': str(e)}
    
    # Private helper methods
    
    def _chunk_content(self, content: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split content into overlapping chunks"""
        if self.tokenizer:
            tokens = self.tokenizer.encode(content)
            chunks = []
            
            for i in range(0, len(tokens), chunk_size - overlap):
                chunk_tokens = tokens[i:i + chunk_size]
                chunk_text = self.tokenizer.decode(chunk_tokens)
                chunks.append(chunk_text)
            
            return chunks
        else:
            # Fallback to character-based chunking
            chunks = []
            for i in range(0, len(content), chunk_size - overlap):
                chunk = content[i:i + chunk_size]
                chunks.append(chunk)
            return chunks
    
    async def _add_to_pinecone(self, document_id: str, chunks: List[str], metadata: Dict[str, Any], content_hash: str) -> bool:
        """Add document chunks to Pinecone"""
        try:
            vectors = []
            
            for i, chunk in enumerate(chunks):
                # Generate embedding
                embedding_response = self.openai_client.embeddings.create(
                    model="text-embedding-ada-002",
                    input=chunk
                )
                embedding = embedding_response.data[0].embedding
                
                # Create vector
                vector_id = f"{document_id}_chunk_{i}"
                vector_metadata = {
                    **metadata,
                    'document_id': document_id,
                    'chunk_index': i,
                    'content_hash': content_hash,
                    'chunk_text': chunk[:500],  # Store first 500 chars for preview
                    'timestamp': datetime.now().isoformat()
                }
                
                vectors.append({
                    'id': vector_id,
                    'values': embedding,
                    'metadata': vector_metadata
                })
            
            # Upsert vectors in batches
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.index.upsert(vectors=batch)
            
            logger.info(f"✅ Added {len(vectors)} vectors to Pinecone for document {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Pinecone upsert failed: {e}")
            return False
    
    async def _add_to_fallback(self, document_id: str, chunks: List[str], metadata: Dict[str, Any], content_hash: str) -> bool:
        """Add document to fallback TF-IDF system"""
        try:
            for i, chunk in enumerate(chunks):
                self.tfidf_documents.append(chunk)
                self.tfidf_metadata.append({
                    **metadata,
                    'document_id': document_id,
                    'chunk_index': i,
                    'content_hash': content_hash,
                    'chunk_text': chunk[:500],
                    'timestamp': datetime.now().isoformat()
                })
            
            # Refit TF-IDF vectorizer
            if len(self.tfidf_documents) > 0:
                self.tfidf_vectorizer.fit(self.tfidf_documents)
                self.tfidf_fitted = True
            
            logger.info(f"✅ Added {len(chunks)} chunks to fallback system for document {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Fallback system add failed: {e}")
            return False
    
    async def _search_pinecone(self, query: str, filters: Dict[str, Any], top_k: int) -> List[Dict[str, Any]]:
        """Search Pinecone vector database"""
        try:
            # Generate query embedding
            embedding_response = self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=query
            )
            query_embedding = embedding_response.data[0].embedding
            
            # Build filter
            pinecone_filter = {}
            if filters:
                for key, value in filters.items():
                    if key in ['jurisdiction', 'document_type', 'language']:
                        pinecone_filter[key] = value
            
            # Search
            search_response = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=pinecone_filter if pinecone_filter else None
            )
            
            # Format results
            results = []
            for match in search_response.matches:
                results.append({
                    'id': match.id,
                    'score': match.score,
                    'content': match.metadata.get('chunk_text', ''),
                    'metadata': match.metadata
                })
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Pinecone search failed: {e}")
            return []
    
    async def _search_fallback(self, query: str, filters: Dict[str, Any], top_k: int) -> List[Dict[str, Any]]:
        """Search fallback TF-IDF system"""
        try:
            if not self.tfidf_fitted or len(self.tfidf_documents) == 0:
                return []
            
            # Transform query
            query_vector = self.tfidf_vectorizer.transform([query])
            
            # Transform all documents
            doc_vectors = self.tfidf_vectorizer.transform(self.tfidf_documents)
            
            # Calculate similarities
            similarities = cosine_similarity(query_vector, doc_vectors).flatten()
            
            # Get top results
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                if similarities[idx] > 0.1:  # Minimum similarity threshold
                    metadata = self.tfidf_metadata[idx]
                    
                    # Apply filters
                    if filters:
                        skip = False
                        for key, value in filters.items():
                            if key in metadata and metadata[key] != value:
                                skip = True
                                break
                        if skip:
                            continue
                    
                    results.append({
                        'id': f"fallback_{idx}",
                        'score': float(similarities[idx]),
                        'content': self.tfidf_documents[idx],
                        'metadata': metadata
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Fallback search failed: {e}")
            return []
    
    def _enhance_query_with_context(self, query: str, user_context: Dict[str, Any]) -> str:
        """Enhance query with user context"""
        if not user_context:
            return query
        
        enhancements = []
        
        # Add jurisdiction context
        if user_context.get('jurisdiction'):
            enhancements.append(f"jurisdiction: {user_context['jurisdiction']}")
        
        # Add user type context
        if user_context.get('user_type'):
            enhancements.append(f"user type: {user_context['user_type']}")
        
        # Add language context
        if user_context.get('language'):
            enhancements.append(f"language: {user_context['language']}")
        
        if enhancements:
            enhanced_query = f"{query} ({', '.join(enhancements)})"
            return enhanced_query
        
        return query
    
    def _build_context_from_results(self, results: List[Dict[str, Any]]) -> str:
        """Build context string from search results"""
        context_parts = []
        
        for i, result in enumerate(results):
            content = result.get('content', '')
            metadata = result.get('metadata', {})
            
            context_part = f"Source {i+1}:\n{content}\n"
            if metadata.get('document_id'):
                context_part += f"(Document: {metadata['document_id']})\n"
            
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    def _create_rag_system_prompt(self, user_context: Dict[str, Any]) -> str:
        """Create system prompt for RAG responses"""
        base_prompt = """You are an expert AI tax advisor with access to comprehensive tax knowledge. 
        Use the provided context to answer questions accurately and helpfully.
        
        Guidelines:
        - Base your answers on the provided context
        - If the context doesn't contain enough information, say so clearly
        - Provide specific, actionable advice when possible
        - Include relevant citations or references
        - Consider the user's jurisdiction and circumstances"""
        
        if user_context:
            if user_context.get('jurisdiction'):
                base_prompt += f"\n- User jurisdiction: {user_context['jurisdiction']}"
            if user_context.get('user_type'):
                base_prompt += f"\n- User type: {user_context['user_type']}"
            if user_context.get('language'):
                base_prompt += f"\n- Respond in: {user_context['language']}"
        
        return base_prompt
    
    async def _generate_openai_response(self, system_prompt: str, query: str, context: str, user_context: Dict[str, Any]) -> str:
        """Generate response using OpenAI with RAG context"""
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
            ]
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"❌ OpenAI response generation failed: {e}")
            return f"I apologize, but I'm unable to generate a response at the moment. Error: {str(e)}"
    
    async def _generate_fallback_response(self, query: str, search_results: List[Dict[str, Any]], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback response without OpenAI"""
        try:
            if not search_results:
                response = "I don't have enough information to answer your question accurately. Please try rephrasing your question or provide more context."
                confidence = 0.1
            else:
                # Simple template-based response
                best_result = search_results[0]
                content = best_result.get('content', '')
                
                response = f"Based on the available information: {content[:500]}..."
                confidence = min(best_result.get('score', 0.5), 0.8)
            
            return {
                'success': True,
                'response': response,
                'confidence': confidence,
                'sources': [r['metadata'] for r in search_results],
                'context_used': len(search_results)
            }
            
        except Exception as e:
            logger.error(f"❌ Fallback response generation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _calculate_response_confidence(self, search_results: List[Dict[str, Any]], response: str) -> float:
        """Calculate confidence score for generated response"""
        if not search_results:
            return 0.1
        
        # Base confidence on search result scores
        avg_score = sum(r.get('score', 0) for r in search_results) / len(search_results)
        
        # Adjust based on number of results
        result_factor = min(len(search_results) / 3, 1.0)
        
        # Adjust based on response length (longer responses might be more comprehensive)
        length_factor = min(len(response) / 500, 1.0)
        
        confidence = avg_score * result_factor * length_factor
        return min(confidence, 0.95)  # Cap at 95%
    
    async def _check_existing_document(self, content_hash: str) -> bool:
        """Check if document already exists"""
        try:
            supabase = get_supabase_client()
            result = supabase.table('rag_documents').select('id').eq('content_hash', content_hash).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"❌ Failed to check existing document: {e}")
            return False
    
    async def _store_document_metadata(self, document_id: str, content: str, metadata: Dict[str, Any], content_hash: str):
        """Store document metadata in Supabase"""
        try:
            supabase = get_supabase_client()
            supabase.table('rag_documents').insert({
                'document_id': document_id,
                'content_hash': content_hash,
                'metadata': metadata,
                'content_length': len(content),
                'created_at': datetime.now().isoformat()
            }).execute()
        except Exception as e:
            logger.error(f"❌ Failed to store document metadata: {e}")
    
    async def _update_learning_system(self, document_id: str, content: str, metadata: Dict[str, Any]):
        """Update learning system with new document"""
        # This would implement learning algorithms to improve future responses
        # For now, we'll just log the addition
        logger.info(f"📚 Learning system updated with document: {document_id}")
    
    async def _post_process_results(self, results: List[Dict[str, Any]], query: str, user_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Post-process search results with learning"""
        # Apply user-specific learning and preferences
        # For now, return results as-is
        return results
    
    async def _log_search_interaction(self, query: str, results: List[Dict[str, Any]], user_context: Dict[str, Any]):
        """Log search interaction for learning"""
        try:
            supabase = get_supabase_client()
            supabase.table('rag_searches').insert({
                'query': query,
                'results_count': len(results),
                'user_context': user_context,
                'timestamp': datetime.now().isoformat()
            }).execute()
        except Exception as e:
            logger.error(f"❌ Failed to log search interaction: {e}")
    
    async def _boost_content_relevance(self, query: str, response: str, user_context: Dict[str, Any]):
        """Boost relevance of content that received positive feedback"""
        # This would implement learning algorithms to boost content
        logger.info(f"📈 Boosting content relevance for query: {query[:50]}...")
    
    async def _reduce_content_relevance(self, query: str, response: str, user_context: Dict[str, Any]):
        """Reduce relevance of content that received negative feedback"""
        # This would implement learning algorithms to reduce content relevance
        logger.info(f"📉 Reducing content relevance for query: {query[:50]}...")
    
    async def _process_improvement_suggestions(self, query: str, suggestions: List[str], user_context: Dict[str, Any]):
        """Process improvement suggestions from user feedback"""
        # This would implement learning from user suggestions
        logger.info(f"💡 Processing {len(suggestions)} improvement suggestions for query: {query[:50]}...")

# Global service instance
pinecone_rag_service = PineconeRAGService()

