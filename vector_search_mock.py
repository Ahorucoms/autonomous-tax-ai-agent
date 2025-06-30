"""
Mock Vector Search Service for Malta Tax AI
Provides fallback functionality when Pinecone is unavailable or quota exceeded
"""

import os
import json
import logging
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import required packages
import openai

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Configuration
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


class MockVectorSearchService:
    """Mock vector search service using SQLite and TF-IDF"""
    
    def __init__(self, db_path: str = "/tmp/mock_vector_db.sqlite"):
        """Initialize mock vector search service"""
        self.logger = logging.getLogger(__name__)
        self.db_path = db_path
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.document_vectors = {}
        self.documents = {}
        
        # Initialize database
        self._initialize_database()
        
        # Load existing documents
        self._load_documents()
        
        # Add sample Malta tax knowledge
        self._add_sample_knowledge()
    
    def _initialize_database(self):
        """Initialize SQLite database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    document_type TEXT NOT NULL,
                    metadata TEXT,
                    embedding TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    def _load_documents(self):
        """Load documents from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT * FROM documents")
                
                documents_text = []
                for row in cursor.fetchall():
                    doc = VectorDocument(
                        id=row['id'],
                        title=row['title'],
                        content=row['content'],
                        document_type=DocumentType(row['document_type']),
                        metadata=json.loads(row['metadata']) if row['metadata'] else {},
                        embedding=json.loads(row['embedding']) if row['embedding'] else None,
                        created_at=datetime.fromisoformat(row['created_at']),
                        updated_at=datetime.fromisoformat(row['updated_at'])
                    )
                    
                    self.documents[doc.id] = doc
                    documents_text.append(doc.content)
                
                # Fit vectorizer if we have documents
                if documents_text:
                    self.vectorizer.fit(documents_text)
                    
                    # Generate TF-IDF vectors for all documents
                    vectors = self.vectorizer.transform(documents_text)
                    for i, doc_id in enumerate(self.documents.keys()):
                        self.document_vectors[doc_id] = vectors[i].toarray()[0]
                
                self.logger.info(f"Loaded {len(self.documents)} documents from database")
                
        except Exception as e:
            self.logger.error(f"Failed to load documents: {e}")
    
    def _add_sample_knowledge(self):
        """Add sample Malta tax knowledge if database is empty"""
        if len(self.documents) > 0:
            return
        
        sample_documents = [
            {
                'title': 'Malta Income Tax Rates 2025',
                'content': 'Malta income tax rates for 2025: 0% on first €9,100, 15% on next €5,100 (€9,101-€14,200), 25% on next €5,800 (€14,201-€20,000), 25% on next €40,000 (€20,001-€60,000), 35% on income above €60,000. Married couples can elect for separate or joint assessment.',
                'document_type': 'tax_regulation',
                'metadata': {'year': 2025, 'jurisdiction': 'malta', 'category': 'income_tax'}
            },
            {
                'title': 'Malta VAT Rates and Registration',
                'content': 'Malta VAT standard rate is 18%. Reduced rates: 12% for accommodation, 7% for books and medicines, 5% for food and utilities. VAT registration required if annual turnover exceeds €35,000. Zero-rated supplies include exports and international transport.',
                'document_type': 'tax_regulation',
                'metadata': {'year': 2025, 'jurisdiction': 'malta', 'category': 'vat'}
            },
            {
                'title': 'Malta Corporate Tax System',
                'content': 'Malta corporate income tax rate is 35% on all profits. However, shareholders may claim refunds of 6/7ths (85.7%) or 5/7ths (71.4%) of tax paid, depending on the nature of income. This results in effective rates of 5% or 10% for shareholders.',
                'document_type': 'tax_regulation',
                'metadata': {'year': 2025, 'jurisdiction': 'malta', 'category': 'corporate_tax'}
            },
            {
                'title': 'Malta Social Security Contributions',
                'content': 'Malta social security contributions: Class 1 (employees) - 10% employee, 10% employer on weekly earnings €166.68-€817.51. Class 2 (self-employed) - 15% on annual income €3,400-€42,508. Maximum annual contribution €6,376.',
                'document_type': 'tax_regulation',
                'metadata': {'year': 2025, 'jurisdiction': 'malta', 'category': 'social_security'}
            },
            {
                'title': 'Malta Stamp Duty on Property',
                'content': 'Malta stamp duty on property transfers: 5% on first €150,000, 8% on excess. First-time buyers: 3.5% on first €150,000, 5% on excess. Commercial property: 8% flat rate. Additional 8% duty for non-residents acquiring property.',
                'document_type': 'tax_regulation',
                'metadata': {'year': 2025, 'jurisdiction': 'malta', 'category': 'stamp_duty'}
            },
            {
                'title': 'How to Calculate Malta Income Tax',
                'content': 'Step 1: Determine gross income. Step 2: Deduct allowable expenses. Step 3: Apply personal allowances (€9,100 for single, €12,700 for married). Step 4: Apply tax rates progressively. Step 5: Deduct tax credits if applicable. Example: €30,000 income = €2,475 tax for single person.',
                'document_type': 'calculation_example',
                'metadata': {'year': 2025, 'jurisdiction': 'malta', 'category': 'income_tax'}
            },
            {
                'title': 'Malta FS3 Form Filing Requirements',
                'content': 'FS3 form must be filed by 30th June for previous tax year. Required for all individuals with income above €9,100 or those claiming deductions. Include all income sources: employment, business, rental, investment. Attach supporting documents: P60, receipts, bank statements.',
                'document_type': 'procedure',
                'metadata': {'year': 2025, 'jurisdiction': 'malta', 'category': 'filing'}
            },
            {
                'title': 'Malta Tax Residency Rules',
                'content': 'Malta tax residency determined by: 1) Domicile in Malta, 2) Ordinary residence in Malta, 3) Physical presence for 183+ days. Residents taxed on worldwide income. Non-residents taxed only on Malta-source income. Special rules for non-domiciled residents.',
                'document_type': 'guidance_note',
                'metadata': {'year': 2025, 'jurisdiction': 'malta', 'category': 'residency'}
            }
        ]
        
        for doc_data in sample_documents:
            doc_id = hashlib.sha256(f"{doc_data['title']}_{doc_data['content'][:100]}".encode()).hexdigest()[:16]
            
            document = VectorDocument(
                id=doc_id,
                title=doc_data['title'],
                content=doc_data['content'],
                document_type=DocumentType(doc_data['document_type']),
                metadata=doc_data['metadata']
            )
            
            # Add to database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO documents 
                    (id, title, content, document_type, metadata, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    document.id,
                    document.title,
                    document.content,
                    document.document_type.value,
                    json.dumps(document.metadata),
                    document.created_at.isoformat(),
                    document.updated_at.isoformat()
                ))
            
            self.documents[doc_id] = document
        
        # Refit vectorizer with new documents
        documents_text = [doc.content for doc in self.documents.values()]
        if documents_text:
            self.vectorizer.fit(documents_text)
            vectors = self.vectorizer.transform(documents_text)
            for i, doc_id in enumerate(self.documents.keys()):
                self.document_vectors[doc_id] = vectors[i].toarray()[0]
        
        self.logger.info(f"Added {len(sample_documents)} sample documents")
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI (fallback to TF-IDF if unavailable)"""
        try:
            # Try OpenAI first
            response = self.client.embeddings.create(
                model=OPENAI_EMBEDDING_MODEL,
                input=text
            )
            return response.data[0].embedding
            
        except Exception as e:
            self.logger.warning(f"OpenAI embedding failed, using TF-IDF: {e}")
            
            # Fallback to TF-IDF
            try:
                vector = self.vectorizer.transform([text])
                return vector.toarray()[0].tolist()
            except Exception as e2:
                self.logger.error(f"TF-IDF embedding failed: {e2}")
                # Return zero vector as last resort
                return [0.0] * 1000
    
    async def add_document(self, document: VectorDocument) -> bool:
        """Add document to mock vector database"""
        try:
            # Generate embedding if not provided
            if document.embedding is None:
                document.embedding = await self.generate_embedding(document.content)
            
            # Add to database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO documents 
                    (id, title, content, document_type, metadata, embedding, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    document.id,
                    document.title,
                    document.content,
                    document.document_type.value,
                    json.dumps(document.metadata),
                    json.dumps(document.embedding),
                    document.created_at.isoformat(),
                    document.updated_at.isoformat()
                ))
            
            # Add to memory
            self.documents[document.id] = document
            
            # Update TF-IDF vectors
            documents_text = [doc.content for doc in self.documents.values()]
            self.vectorizer.fit(documents_text)
            vectors = self.vectorizer.transform(documents_text)
            for i, doc_id in enumerate(self.documents.keys()):
                self.document_vectors[doc_id] = vectors[i].toarray()[0]
            
            self.logger.info(f"Added document to mock vector database: {document.id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add document {document.id}: {e}")
            return False
    
    async def add_documents_batch(self, documents: List[VectorDocument]) -> Tuple[int, int]:
        """Add multiple documents in batch"""
        successful = 0
        failed = 0
        
        for doc in documents:
            if await self.add_document(doc):
                successful += 1
            else:
                failed += 1
        
        return successful, failed
    
    async def search(self, query: SearchQuery) -> List[SearchResult]:
        """Search for documents using TF-IDF similarity"""
        try:
            if not self.documents:
                return []
            
            # Generate query vector
            query_vector = self.vectorizer.transform([query.query]).toarray()[0]
            
            # Calculate similarities
            results = []
            for doc_id, doc in self.documents.items():
                if doc_id in self.document_vectors:
                    doc_vector = self.document_vectors[doc_id]
                    
                    # Calculate cosine similarity
                    similarity = cosine_similarity([query_vector], [doc_vector])[0][0]
                    
                    # Apply filters
                    if query.filters:
                        skip_doc = False
                        for key, value in query.filters.items():
                            if key == 'document_type':
                                if isinstance(value, list):
                                    if doc.document_type.value not in value:
                                        skip_doc = True
                                        break
                                else:
                                    if doc.document_type.value != value:
                                        skip_doc = True
                                        break
                            elif key in doc.metadata:
                                if doc.metadata[key] != value:
                                    skip_doc = True
                                    break
                        
                        if skip_doc:
                            continue
                    
                    # Check similarity threshold
                    if similarity >= query.similarity_threshold:
                        # Determine result type
                        if similarity >= 0.9:
                            result_type = SearchResultType.EXACT_MATCH
                            explanation = "High similarity match"
                        elif similarity >= 0.7:
                            result_type = SearchResultType.SEMANTIC_MATCH
                            explanation = "Good semantic match"
                        elif similarity >= 0.5:
                            result_type = SearchResultType.RELATED_CONTENT
                            explanation = "Related content"
                        else:
                            result_type = SearchResultType.SUGGESTED_CONTENT
                            explanation = "Potentially relevant"
                        
                        search_result = SearchResult(
                            document=doc,
                            score=similarity,
                            result_type=result_type,
                            explanation=explanation,
                            highlights=self._extract_highlights(query.query, doc.content)
                        )
                        
                        results.append(search_result)
            
            # Sort by score and limit results
            results.sort(key=lambda x: x.score, reverse=True)
            results = results[:query.max_results]
            
            self.logger.info(f"Mock search found {len(results)} results for: {query.query[:50]}...")
            return results
            
        except Exception as e:
            self.logger.error(f"Mock search failed: {e}")
            return []
    
    def _extract_highlights(self, query: str, content: str, max_highlights: int = 3) -> List[str]:
        """Extract relevant highlights from content"""
        try:
            query_words = query.lower().split()
            sentences = content.split('.')
            
            highlights = []
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 20:
                    sentence_lower = sentence.lower()
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
        """Get document by ID"""
        return self.documents.get(document_id)
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete document from mock database"""
        try:
            # Remove from database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM documents WHERE id = ?", (document_id,))
            
            # Remove from memory
            if document_id in self.documents:
                del self.documents[document_id]
            
            if document_id in self.document_vectors:
                del self.document_vectors[document_id]
            
            self.logger.info(f"Deleted document: {document_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete document {document_id}: {e}")
            return False
    
    async def update_document(self, document: VectorDocument) -> bool:
        """Update existing document"""
        document.updated_at = datetime.utcnow()
        return await self.add_document(document)
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get mock index statistics"""
        return {
            'total_vectors': len(self.documents),
            'dimension': 1000,  # TF-IDF dimension
            'index_fullness': 0.1,
            'namespaces': {'default': len(self.documents)},
            'backend': 'mock_tfidf'
        }
    
    async def similarity_search_by_vector(self, vector: List[float], 
                                        max_results: int = MAX_SEARCH_RESULTS,
                                        filters: Dict[str, Any] = None) -> List[SearchResult]:
        """Search by vector directly"""
        # For mock implementation, convert back to text search
        # In a real implementation, this would use the vector directly
        return await self.search(SearchQuery(
            query="vector search",
            filters=filters,
            max_results=max_results
        ))


# Global mock instance
mock_vector_search_service = MockVectorSearchService()


# Helper functions for easy access
async def search_knowledge(query: str, 
                         document_types: List[str] = None,
                         max_results: int = MAX_SEARCH_RESULTS) -> List[Dict[str, Any]]:
    """Simple search function for knowledge base"""
    filters = {}
    if document_types:
        filters['document_type'] = document_types
    
    search_query = SearchQuery(
        query=query,
        filters=filters,
        max_results=max_results
    )
    
    results = await mock_vector_search_service.search(search_query)
    return [result.to_dict() for result in results]


async def add_knowledge_document(title: str, content: str, 
                               document_type: str = "unknown",
                               metadata: Dict[str, Any] = None) -> bool:
    """Add document to knowledge base"""
    doc_id = hashlib.sha256(f"{title}_{content[:100]}".encode()).hexdigest()[:16]
    
    document = VectorDocument(
        id=doc_id,
        title=title,
        content=content,
        document_type=DocumentType(document_type),
        metadata=metadata or {}
    )
    
    return await mock_vector_search_service.add_document(document)

