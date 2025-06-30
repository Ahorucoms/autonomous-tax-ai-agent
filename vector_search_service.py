"""
Vector Search Service for Malta Tax AI
Provides semantic search capabilities using OpenAI embeddings and Pinecone vector database
"""

import os
import json
import asyncio
import logging
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import required packages
import openai
from pinecone import Pinecone, ServerlessSpec
import tiktoken

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Configure Pinecone
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))

# Configuration
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME', 'malta-tax-knowledge')
VECTOR_DIMENSION = int(os.getenv('VECTOR_DIMENSION', '3072'))
SIMILARITY_THRESHOLD = float(os.getenv('SIMILARITY_THRESHOLD', '0.7'))
MAX_SEARCH_RESULTS = int(os.getenv('MAX_SEARCH_RESULTS', '10'))
OPENAI_EMBEDDING_MODEL = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-large')


class DocumentType(Enum):
    """Types of documents in the knowledge base"""
    TAX_REGULATION = "tax_regulation"
    TAX_FORM = "tax_form"
    GUIDANCE_NOTE = "guidance_note"
    CASE_LAW = "case_law"
    FAQ = "faq"
    PROCEDURE = "procedure"
    CALCULATION_EXAMPLE = "calculation_example"
    TEMPLATE = "template"
    UNKNOWN = "unknown"


class SearchResultType(Enum):
    """Types of search results"""
    EXACT_MATCH = "exact_match"
    SEMANTIC_MATCH = "semantic_match"
    RELATED_CONTENT = "related_content"
    SUGGESTED_CONTENT = "suggested_content"


@dataclass
class VectorDocument:
    """Document stored in vector database"""
    id: str
    content: str
    title: str
    document_type: DocumentType
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()


@dataclass
class SearchResult:
    """Search result with relevance scoring"""
    document: VectorDocument
    score: float
    result_type: SearchResultType
    explanation: str
    highlights: List[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.document.id,
            'title': self.document.title,
            'content': self.document.content,
            'document_type': self.document.document_type.value,
            'metadata': self.document.metadata,
            'score': self.score,
            'result_type': self.result_type.value,
            'explanation': self.explanation,
            'highlights': self.highlights or [],
            'created_at': self.document.created_at.isoformat() if self.document.created_at else None,
            'updated_at': self.document.updated_at.isoformat() if self.document.updated_at else None
        }


@dataclass
class SearchQuery:
    """Search query with context and filters"""
    query: str
    filters: Dict[str, Any] = None
    max_results: int = MAX_SEARCH_RESULTS
    similarity_threshold: float = SIMILARITY_THRESHOLD
    include_metadata: bool = True
    user_context: Dict[str, Any] = None


class VectorSearchService:
    """Vector search service using OpenAI embeddings and Pinecone"""
    
    def __init__(self):
        """Initialize vector search service"""
        self.logger = logging.getLogger(__name__)
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.pc = pc
        self.index = None
        self.encoding = tiktoken.encoding_for_model("gpt-4")
        
        try:
            # Initialize Pinecone index
            self._initialize_index()
            self.use_mock = False
        except Exception as e:
            self.logger.warning(f"Pinecone unavailable, using mock service: {e}")
            from vector_search_mock import mock_vector_search_service
            self.mock_service = mock_vector_search_service
            self.use_mock = True
    
    def _initialize_index(self):
        """Initialize or create Pinecone index"""
        try:
            # Check if index exists
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            if PINECONE_INDEX_NAME not in existing_indexes:
                self.logger.info(f"Creating Pinecone index: {PINECONE_INDEX_NAME}")
                
                # Create index with serverless spec
                self.pc.create_index(
                    name=PINECONE_INDEX_NAME,
                    dimension=VECTOR_DIMENSION,
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region='us-east-1'
                    )
                )
                
                self.logger.info(f"Created Pinecone index: {PINECONE_INDEX_NAME}")
            
            # Connect to index
            self.index = self.pc.Index(PINECONE_INDEX_NAME)
            self.logger.info(f"Connected to Pinecone index: {PINECONE_INDEX_NAME}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Pinecone index: {e}")
            raise
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using OpenAI
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            # Truncate text if too long
            tokens = self.encoding.encode(text)
            if len(tokens) > 8000:  # Leave room for other tokens
                tokens = tokens[:8000]
                text = self.encoding.decode(tokens)
            
            # Generate embedding
            response = self.client.embeddings.create(
                model=OPENAI_EMBEDDING_MODEL,
                input=text
            )
            
            embedding = response.data[0].embedding
            self.logger.debug(f"Generated embedding for text of length {len(text)}")
            
            return embedding
            
        except Exception as e:
            self.logger.error(f"Failed to generate embedding: {e}")
            raise
    
    async def add_document(self, document: VectorDocument) -> bool:
        """
        Add document to vector database
        
        Args:
            document: Document to add
            
        Returns:
            True if successful, False otherwise
        """
        if self.use_mock:
            return await self.mock_service.add_document(document)
        
        try:
            # Generate embedding if not provided
            if document.embedding is None:
                document.embedding = await self.generate_embedding(document.content)
            
            # Prepare metadata
            metadata = {
                'title': document.title,
                'document_type': document.document_type.value,
                'created_at': document.created_at.isoformat(),
                'updated_at': document.updated_at.isoformat(),
                **document.metadata
            }
            
            # Upsert to Pinecone
            self.index.upsert(
                vectors=[(
                    document.id,
                    document.embedding,
                    metadata
                )]
            )
            
            self.logger.info(f"Added document to vector database: {document.id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add document {document.id}: {e}")
            return False
    
    async def add_documents_batch(self, documents: List[VectorDocument]) -> Tuple[int, int]:
        """
        Add multiple documents in batch
        
        Args:
            documents: List of documents to add
            
        Returns:
            Tuple of (successful_count, failed_count)
        """
        successful = 0
        failed = 0
        
        try:
            # Generate embeddings for documents that don't have them
            for doc in documents:
                if doc.embedding is None:
                    try:
                        doc.embedding = await self.generate_embedding(doc.content)
                    except Exception as e:
                        self.logger.error(f"Failed to generate embedding for {doc.id}: {e}")
                        failed += 1
                        continue
            
            # Prepare vectors for batch upsert
            vectors = []
            for doc in documents:
                if doc.embedding is not None:
                    metadata = {
                        'title': doc.title,
                        'document_type': doc.document_type.value,
                        'created_at': doc.created_at.isoformat(),
                        'updated_at': doc.updated_at.isoformat(),
                        **doc.metadata
                    }
                    vectors.append((doc.id, doc.embedding, metadata))
            
            # Batch upsert to Pinecone
            if vectors:
                self.index.upsert(vectors=vectors)
                successful = len(vectors)
                self.logger.info(f"Added {successful} documents to vector database")
            
        except Exception as e:
            self.logger.error(f"Batch upsert failed: {e}")
            failed += len(documents) - successful
        
        return successful, failed
    
    async def search(self, query: SearchQuery) -> List[SearchResult]:
        """
        Search for documents using semantic similarity
        
        Args:
            query: Search query with parameters
            
        Returns:
            List of search results
        """
        if self.use_mock:
            return await self.mock_service.search(query)
        
        try:
            # Generate query embedding
            query_embedding = await self.generate_embedding(query.query)
            
            # Prepare filter
            filter_dict = {}
            if query.filters:
                for key, value in query.filters.items():
                    if key == 'document_type' and isinstance(value, list):
                        filter_dict[key] = {"$in": value}
                    else:
                        filter_dict[key] = value
            
            # Search in Pinecone
            search_response = self.index.query(
                vector=query_embedding,
                top_k=query.max_results,
                filter=filter_dict if filter_dict else None,
                include_metadata=query.include_metadata
            )
            
            # Process results
            results = []
            for match in search_response.matches:
                if match.score >= query.similarity_threshold:
                    # Create document from match
                    metadata = match.metadata or {}
                    document = VectorDocument(
                        id=match.id,
                        content=metadata.get('content', ''),
                        title=metadata.get('title', ''),
                        document_type=DocumentType(metadata.get('document_type', 'unknown')),
                        metadata={k: v for k, v in metadata.items() 
                                if k not in ['content', 'title', 'document_type', 'created_at', 'updated_at']},
                        created_at=datetime.fromisoformat(metadata.get('created_at', datetime.utcnow().isoformat())),
                        updated_at=datetime.fromisoformat(metadata.get('updated_at', datetime.utcnow().isoformat()))
                    )
                    
                    # Determine result type based on score
                    if match.score >= 0.95:
                        result_type = SearchResultType.EXACT_MATCH
                        explanation = "Exact match found"
                    elif match.score >= 0.8:
                        result_type = SearchResultType.SEMANTIC_MATCH
                        explanation = "High semantic similarity"
                    elif match.score >= 0.7:
                        result_type = SearchResultType.RELATED_CONTENT
                        explanation = "Related content found"
                    else:
                        result_type = SearchResultType.SUGGESTED_CONTENT
                        explanation = "Potentially relevant content"
                    
                    # Create search result
                    search_result = SearchResult(
                        document=document,
                        score=match.score,
                        result_type=result_type,
                        explanation=explanation,
                        highlights=self._extract_highlights(query.query, document.content)
                    )
                    
                    results.append(search_result)
            
            self.logger.info(f"Found {len(results)} results for query: {query.query[:50]}...")
            return results
            
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return []
    
    def _extract_highlights(self, query: str, content: str, max_highlights: int = 3) -> List[str]:
        """Extract relevant highlights from content"""
        try:
            # Simple keyword-based highlighting
            query_words = query.lower().split()
            content_lower = content.lower()
            sentences = content.split('.')
            
            highlights = []
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 20:  # Skip very short sentences
                    sentence_lower = sentence.lower()
                    # Check if sentence contains query words
                    word_matches = sum(1 for word in query_words if word in sentence_lower)
                    if word_matches > 0:
                        highlights.append(sentence)
                        if len(highlights) >= max_highlights:
                            break
            
            return highlights
            
        except Exception as e:
            self.logger.error(f"Failed to extract highlights: {e}")
            return []
    
    async def get_document(self, document_id: str) -> Optional[VectorDocument]:
        """
        Get document by ID
        
        Args:
            document_id: Document ID
            
        Returns:
            Document if found, None otherwise
        """
        try:
            # Fetch from Pinecone
            response = self.index.fetch(ids=[document_id])
            
            if document_id in response.vectors:
                vector_data = response.vectors[document_id]
                metadata = vector_data.metadata or {}
                
                document = VectorDocument(
                    id=document_id,
                    content=metadata.get('content', ''),
                    title=metadata.get('title', ''),
                    document_type=DocumentType(metadata.get('document_type', 'unknown')),
                    metadata={k: v for k, v in metadata.items() 
                            if k not in ['content', 'title', 'document_type', 'created_at', 'updated_at']},
                    embedding=vector_data.values,
                    created_at=datetime.fromisoformat(metadata.get('created_at', datetime.utcnow().isoformat())),
                    updated_at=datetime.fromisoformat(metadata.get('updated_at', datetime.utcnow().isoformat()))
                )
                
                return document
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get document {document_id}: {e}")
            return None
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Delete document from vector database
        
        Args:
            document_id: Document ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.index.delete(ids=[document_id])
            self.logger.info(f"Deleted document: {document_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete document {document_id}: {e}")
            return False
    
    async def update_document(self, document: VectorDocument) -> bool:
        """
        Update existing document
        
        Args:
            document: Updated document
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Update timestamp
            document.updated_at = datetime.utcnow()
            
            # Generate new embedding if content changed
            if document.embedding is None:
                document.embedding = await self.generate_embedding(document.content)
            
            # Update in Pinecone (upsert will overwrite)
            return await self.add_document(document)
            
        except Exception as e:
            self.logger.error(f"Failed to update document {document.id}: {e}")
            return False
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        if self.use_mock:
            return self.mock_service.get_index_stats()
        
        try:
            stats = self.index.describe_index_stats()
            return {
                'total_vectors': stats.total_vector_count,
                'dimension': stats.dimension,
                'index_fullness': stats.index_fullness,
                'namespaces': dict(stats.namespaces) if stats.namespaces else {}
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get index stats: {e}")
            return {}
    
    async def similarity_search_by_vector(self, vector: List[float], 
                                        max_results: int = MAX_SEARCH_RESULTS,
                                        filters: Dict[str, Any] = None) -> List[SearchResult]:
        """
        Search by vector directly
        
        Args:
            vector: Query vector
            max_results: Maximum number of results
            filters: Optional filters
            
        Returns:
            List of search results
        """
        try:
            # Prepare filter
            filter_dict = {}
            if filters:
                for key, value in filters.items():
                    if key == 'document_type' and isinstance(value, list):
                        filter_dict[key] = {"$in": value}
                    else:
                        filter_dict[key] = value
            
            # Search in Pinecone
            search_response = self.index.query(
                vector=vector,
                top_k=max_results,
                filter=filter_dict if filter_dict else None,
                include_metadata=True
            )
            
            # Process results
            results = []
            for match in search_response.matches:
                metadata = match.metadata or {}
                document = VectorDocument(
                    id=match.id,
                    content=metadata.get('content', ''),
                    title=metadata.get('title', ''),
                    document_type=DocumentType(metadata.get('document_type', 'unknown')),
                    metadata={k: v for k, v in metadata.items() 
                            if k not in ['content', 'title', 'document_type', 'created_at', 'updated_at']},
                    created_at=datetime.fromisoformat(metadata.get('created_at', datetime.utcnow().isoformat())),
                    updated_at=datetime.fromisoformat(metadata.get('updated_at', datetime.utcnow().isoformat()))
                )
                
                search_result = SearchResult(
                    document=document,
                    score=match.score,
                    result_type=SearchResultType.SEMANTIC_MATCH,
                    explanation="Vector similarity search"
                )
                
                results.append(search_result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Vector search failed: {e}")
            return []


# Global instance
vector_search_service = VectorSearchService()


# Helper functions for easy access
async def search_knowledge(query: str, 
                         document_types: List[str] = None,
                         max_results: int = MAX_SEARCH_RESULTS) -> List[Dict[str, Any]]:
    """
    Simple search function for knowledge base
    
    Args:
        query: Search query
        document_types: Optional list of document types to filter
        max_results: Maximum number of results
        
    Returns:
        List of search results as dictionaries
    """
    filters = {}
    if document_types:
        filters['document_type'] = document_types
    
    search_query = SearchQuery(
        query=query,
        filters=filters,
        max_results=max_results
    )
    
    results = await vector_search_service.search(search_query)
    return [result.to_dict() for result in results]


async def add_knowledge_document(title: str, content: str, 
                               document_type: str = "unknown",
                               metadata: Dict[str, Any] = None) -> bool:
    """
    Add document to knowledge base
    
    Args:
        title: Document title
        content: Document content
        document_type: Type of document
        metadata: Additional metadata
        
    Returns:
        True if successful, False otherwise
    """
    # Generate document ID
    doc_id = hashlib.sha256(f"{title}_{content[:100]}".encode()).hexdigest()[:16]
    
    document = VectorDocument(
        id=doc_id,
        title=title,
        content=content,
        document_type=DocumentType(document_type),
        metadata=metadata or {}
    )
    
    return await vector_search_service.add_document(document)

