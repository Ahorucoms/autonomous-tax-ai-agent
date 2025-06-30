"""
Pinecone Vector Database Service
Handles vector storage, retrieval, and semantic search for Malta Tax AI
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from datetime import datetime
import hashlib

try:
    import pinecone
    from pinecone import Pinecone, ServerlessSpec
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    logging.warning("Pinecone library not available. Using mock implementation.")

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI library not available. Using mock embeddings.")


class VectorService:
    """Service for managing vector embeddings and semantic search"""
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 environment: Optional[str] = None,
                 index_name: str = "malta-tax-ai",
                 dimension: int = 1536):
        """
        Initialize Pinecone vector service
        
        Args:
            api_key: Pinecone API key
            environment: Pinecone environment
            index_name: Name of the Pinecone index
            dimension: Vector dimension (1536 for OpenAI embeddings)
        """
        self.api_key = api_key or os.getenv('PINECONE_API_KEY')
        self.environment = environment or os.getenv('PINECONE_ENVIRONMENT')
        self.index_name = index_name
        self.dimension = dimension
        self.index = None
        
        # OpenAI configuration for embeddings
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if self.openai_api_key and OPENAI_AVAILABLE:
            openai.api_key = self.openai_api_key
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize Pinecone
        self._initialize_pinecone()
    
    def _initialize_pinecone(self):
        """Initialize Pinecone client and index"""
        if not PINECONE_AVAILABLE or not self.api_key:
            self.logger.warning("Pinecone not configured. Using mock implementation.")
            return
        
        try:
            # Initialize Pinecone
            pc = Pinecone(api_key=self.api_key)
            
            # Check if index exists, create if not
            existing_indexes = pc.list_indexes()
            index_names = [idx.name for idx in existing_indexes]
            
            if self.index_name not in index_names:
                self.logger.info(f"Creating Pinecone index: {self.index_name}")
                pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region='us-east-1'
                    )
                )
            
            # Connect to index
            self.index = pc.Index(self.index_name)
            self.logger.info(f"Connected to Pinecone index: {self.index_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Pinecone: {e}")
            self.index = None
    
    def generate_embeddings(self, text: str) -> List[float]:
        """
        Generate embeddings for text using OpenAI
        
        Args:
            text: Text to embed
            
        Returns:
            List of embedding values
        """
        if not text or not text.strip():
            return [0.0] * self.dimension
        
        if OPENAI_AVAILABLE and self.openai_api_key:
            try:
                response = openai.embeddings.create(
                    model="text-embedding-ada-002",
                    input=text.strip()
                )
                return response.data[0].embedding
            except Exception as e:
                self.logger.error(f"OpenAI embedding generation failed: {e}")
                return self._generate_mock_embedding(text)
        else:
            return self._generate_mock_embedding(text)
    
    def _generate_mock_embedding(self, text: str) -> List[float]:
        """Generate mock embedding for testing"""
        # Create deterministic embedding based on text hash
        text_hash = hashlib.md5(text.encode()).hexdigest()
        np.random.seed(int(text_hash[:8], 16))
        embedding = np.random.normal(0, 1, self.dimension).tolist()
        return embedding
    
    def upsert_document(self, 
                       document_id: str,
                       text: str,
                       metadata: Dict[str, Any]) -> bool:
        """
        Store document vector in Pinecone
        
        Args:
            document_id: Unique document identifier
            text: Document text content
            metadata: Document metadata
            
        Returns:
            Success status
        """
        try:
            # Generate embeddings
            embeddings = self.generate_embeddings(text)
            
            # Prepare metadata (Pinecone has limitations on metadata)
            clean_metadata = self._clean_metadata(metadata)
            clean_metadata['text_preview'] = text[:500]  # Store preview
            clean_metadata['created_at'] = datetime.utcnow().isoformat()
            
            if self.index:
                # Upsert to Pinecone
                self.index.upsert(vectors=[{
                    'id': document_id,
                    'values': embeddings,
                    'metadata': clean_metadata
                }])
                
                self.logger.info(f"Document {document_id} upserted to Pinecone")
                return True
            else:
                # Mock storage for testing
                self.logger.info(f"Mock: Document {document_id} would be stored in Pinecone")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to upsert document {document_id}: {e}")
            return False
    
    def search_similar(self, 
                      query: str,
                      top_k: int = 10,
                      filters: Optional[Dict[str, Any]] = None,
                      include_metadata: bool = True) -> List[Dict[str, Any]]:
        """
        Search for similar documents
        
        Args:
            query: Search query text
            top_k: Number of results to return
            filters: Metadata filters
            include_metadata: Whether to include metadata in results
            
        Returns:
            List of similar documents with scores
        """
        try:
            # Generate query embeddings
            query_embeddings = self.generate_embeddings(query)
            
            if self.index:
                # Query Pinecone
                results = self.index.query(
                    vector=query_embeddings,
                    top_k=top_k,
                    filter=filters,
                    include_metadata=include_metadata
                )
                
                # Format results
                formatted_results = []
                for match in results.matches:
                    result = {
                        'id': match.id,
                        'score': float(match.score),
                        'metadata': match.metadata if include_metadata else {}
                    }
                    formatted_results.append(result)
                
                self.logger.info(f"Found {len(formatted_results)} similar documents")
                return formatted_results
            else:
                # Mock search for testing
                mock_results = self._generate_mock_search_results(query, top_k)
                self.logger.info(f"Mock: Found {len(mock_results)} similar documents")
                return mock_results
                
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return []
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete document from vector database
        
        Args:
            document_id: Document identifier to delete
            
        Returns:
            Success status
        """
        try:
            if self.index:
                self.index.delete(ids=[document_id])
                self.logger.info(f"Document {document_id} deleted from Pinecone")
                return True
            else:
                self.logger.info(f"Mock: Document {document_id} would be deleted")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to delete document {document_id}: {e}")
            return False
    
    def get_index_stats(self) -> Dict[str, Any]:
        """
        Get index statistics
        
        Returns:
            Index statistics
        """
        try:
            if self.index:
                stats = self.index.describe_index_stats()
                return {
                    'total_vector_count': stats.total_vector_count,
                    'dimension': stats.dimension,
                    'index_fullness': stats.index_fullness,
                    'namespaces': dict(stats.namespaces) if stats.namespaces else {}
                }
            else:
                return {
                    'total_vector_count': 0,
                    'dimension': self.dimension,
                    'index_fullness': 0.0,
                    'namespaces': {}
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get index stats: {e}")
            return {}
    
    def batch_upsert(self, 
                    documents: List[Dict[str, Any]],
                    batch_size: int = 100) -> Dict[str, int]:
        """
        Batch upsert multiple documents
        
        Args:
            documents: List of documents with id, text, and metadata
            batch_size: Number of documents per batch
            
        Returns:
            Statistics about the operation
        """
        total_docs = len(documents)
        successful = 0
        failed = 0
        
        for i in range(0, total_docs, batch_size):
            batch = documents[i:i + batch_size]
            
            try:
                # Prepare batch vectors
                vectors = []
                for doc in batch:
                    embeddings = self.generate_embeddings(doc['text'])
                    clean_metadata = self._clean_metadata(doc.get('metadata', {}))
                    clean_metadata['text_preview'] = doc['text'][:500]
                    clean_metadata['created_at'] = datetime.utcnow().isoformat()
                    
                    vectors.append({
                        'id': doc['id'],
                        'values': embeddings,
                        'metadata': clean_metadata
                    })
                
                if self.index:
                    # Batch upsert to Pinecone
                    self.index.upsert(vectors=vectors)
                    successful += len(batch)
                    self.logger.info(f"Batch upserted {len(batch)} documents")
                else:
                    # Mock batch upsert
                    successful += len(batch)
                    self.logger.info(f"Mock: Batch upserted {len(batch)} documents")
                    
            except Exception as e:
                failed += len(batch)
                self.logger.error(f"Batch upsert failed for batch starting at {i}: {e}")
        
        return {
            'total': total_docs,
            'successful': successful,
            'failed': failed
        }
    
    def _clean_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean metadata for Pinecone storage
        
        Args:
            metadata: Original metadata
            
        Returns:
            Cleaned metadata
        """
        clean_metadata = {}
        
        for key, value in metadata.items():
            # Convert to string if necessary
            if isinstance(value, (str, int, float, bool)):
                clean_metadata[key] = value
            elif isinstance(value, list):
                # Convert list to string
                clean_metadata[key] = ', '.join(str(v) for v in value)
            elif isinstance(value, dict):
                # Convert dict to JSON string
                clean_metadata[key] = json.dumps(value)
            else:
                clean_metadata[key] = str(value)
        
        return clean_metadata
    
    def _generate_mock_search_results(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Generate mock search results for testing"""
        mock_results = []
        
        # Generate deterministic mock results based on query
        query_hash = hashlib.md5(query.encode()).hexdigest()
        np.random.seed(int(query_hash[:8], 16))
        
        for i in range(min(top_k, 5)):  # Return up to 5 mock results
            score = np.random.uniform(0.7, 0.95)  # High similarity scores
            doc_id = f"mock_doc_{query_hash[:8]}_{i}"
            
            mock_results.append({
                'id': doc_id,
                'score': float(score),
                'metadata': {
                    'document_type': 'regulation',
                    'jurisdiction': 'malta',
                    'category': 'income_tax',
                    'text_preview': f"Mock document content related to: {query}...",
                    'created_at': datetime.utcnow().isoformat()
                }
            })
        
        # Sort by score descending
        mock_results.sort(key=lambda x: x['score'], reverse=True)
        return mock_results


class KnowledgeBaseManager:
    """Manager for knowledge base operations with vector search"""
    
    def __init__(self, vector_service: VectorService):
        self.vector_service = vector_service
        self.logger = logging.getLogger(__name__)
    
    def add_knowledge_item(self, 
                          item_id: str,
                          title: str,
                          content: str,
                          category: str,
                          tags: List[str],
                          metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add knowledge item to vector database
        
        Args:
            item_id: Unique identifier
            title: Knowledge item title
            content: Full content
            category: Category classification
            tags: List of tags
            metadata: Additional metadata
            
        Returns:
            Success status
        """
        try:
            # Combine title and content for embedding
            full_text = f"{title}\n\n{content}"
            
            # Prepare metadata
            item_metadata = {
                'title': title,
                'category': category,
                'tags': tags,
                'content_type': 'knowledge_base',
                **(metadata or {})
            }
            
            # Store in vector database
            success = self.vector_service.upsert_document(
                document_id=item_id,
                text=full_text,
                metadata=item_metadata
            )
            
            if success:
                self.logger.info(f"Knowledge item {item_id} added successfully")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to add knowledge item {item_id}: {e}")
            return False
    
    def search_knowledge(self, 
                        query: str,
                        category: Optional[str] = None,
                        tags: Optional[List[str]] = None,
                        top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Search knowledge base
        
        Args:
            query: Search query
            category: Filter by category
            tags: Filter by tags
            top_k: Number of results
            
        Returns:
            Search results
        """
        try:
            # Build filters
            filters = {'content_type': 'knowledge_base'}
            
            if category:
                filters['category'] = category
            
            if tags:
                # For simplicity, filter by first tag
                filters['tags'] = tags[0]
            
            # Search vector database
            results = self.vector_service.search_similar(
                query=query,
                top_k=top_k,
                filters=filters,
                include_metadata=True
            )
            
            self.logger.info(f"Knowledge search returned {len(results)} results")
            return results
            
        except Exception as e:
            self.logger.error(f"Knowledge search failed: {e}")
            return []
    
    def get_related_knowledge(self, 
                            document_id: str,
                            top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Get knowledge items related to a document
        
        Args:
            document_id: Reference document ID
            top_k: Number of related items
            
        Returns:
            Related knowledge items
        """
        try:
            # This would require getting the document's embedding and searching
            # For now, return mock related items
            self.logger.info(f"Getting related knowledge for document {document_id}")
            return []
            
        except Exception as e:
            self.logger.error(f"Failed to get related knowledge: {e}")
            return []


# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize vector service
    vector_service = VectorService()
    
    # Test document upsert
    test_doc_id = "test_malta_income_tax_001"
    test_text = """
    Malta Income Tax Calculation Guide
    
    Malta operates a progressive income tax system with the following rates for 2025:
    - 0% on the first €9,100 of annual income
    - 15% on income from €9,101 to €14,500
    - 25% on income from €14,501 to €19,500
    - 25% on income from €19,501 to €60,000
    - 35% on income above €60,000
    
    Married couples can benefit from joint taxation, which may result in lower overall tax liability.
    """
    
    test_metadata = {
        'document_type': 'guide',
        'jurisdiction': 'malta',
        'category': 'income_tax',
        'tags': ['income_tax', 'rates', 'progressive', 'married'],
        'author': 'Malta Tax Authority',
        'year': 2025
    }
    
    # Upsert test document
    success = vector_service.upsert_document(test_doc_id, test_text, test_metadata)
    print(f"Document upsert success: {success}")
    
    # Test search
    search_results = vector_service.search_similar(
        query="What are the income tax rates for married couples in Malta?",
        top_k=5,
        filters={'jurisdiction': 'malta', 'category': 'income_tax'}
    )
    
    print(f"Search results: {len(search_results)}")
    for result in search_results:
        print(f"- ID: {result['id']}, Score: {result['score']:.3f}")
        if 'metadata' in result:
            print(f"  Title: {result['metadata'].get('title', 'N/A')}")
            print(f"  Preview: {result['metadata'].get('text_preview', 'N/A')[:100]}...")
    
    # Test knowledge base manager
    kb_manager = KnowledgeBaseManager(vector_service)
    
    # Add knowledge item
    kb_success = kb_manager.add_knowledge_item(
        item_id="malta_vat_rates_2025",
        title="Malta VAT Rates 2025",
        content="Malta VAT rates: Standard rate 18%, Reduced rates 12%, 7%, 5%, 0%",
        category="vat",
        tags=["vat", "rates", "2025"],
        metadata={"source": "Malta VAT Act", "effective_date": "2025-01-01"}
    )
    
    print(f"Knowledge base item added: {kb_success}")
    
    # Search knowledge base
    kb_results = kb_manager.search_knowledge(
        query="VAT rates in Malta",
        category="vat",
        top_k=3
    )
    
    print(f"Knowledge base search results: {len(kb_results)}")
    
    # Get index stats
    stats = vector_service.get_index_stats()
    print(f"Index stats: {stats}")

