"""
Vector Search Service
Handles semantic search using Pinecone or fallback TF-IDF similarity
"""

import os
import json
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class VectorSearchService:
    """Vector search service with Pinecone and fallback support"""
    
    def __init__(self):
        """Initialize vector search service"""
        self.openai_client = None
        self.pinecone_client = None
        self.use_pinecone = False
        self.use_mock = True
        
        # Initialize OpenAI for embeddings
        self._init_openai()
        
        # Try to initialize Pinecone
        self._init_pinecone()
        
        # Initialize fallback TF-IDF system
        self._init_fallback_system()
        
        # Sample knowledge base for testing
        self.sample_knowledge = self._load_sample_knowledge()
    
    def _init_openai(self):
        """Initialize OpenAI client for embeddings"""
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.openai_client = openai.OpenAI(api_key=api_key)
                logger.info("✅ OpenAI client initialized for embeddings")
            else:
                logger.warning("⚠️ OpenAI API key not found, embeddings will use fallback")
        except Exception as e:
            logger.error(f"❌ Failed to initialize OpenAI client: {e}")
    
    def _init_pinecone(self):
        """Initialize Pinecone client"""
        try:
            # Try to import and initialize Pinecone
            from pinecone import Pinecone
            
            api_key = os.getenv('PINECONE_API_KEY')
            if api_key:
                self.pinecone_client = Pinecone(api_key=api_key)
                self.use_pinecone = True
                self.use_mock = False
                logger.info("✅ Pinecone client initialized successfully")
            else:
                logger.warning("⚠️ Pinecone API key not found, using fallback")
        except Exception as e:
            logger.warning(f"⚠️ Pinecone initialization failed, using fallback: {e}")
    
    def _init_fallback_system(self):
        """Initialize fallback TF-IDF system"""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            self.document_vectors = None
            self.documents = []
            
            logger.info("✅ Fallback TF-IDF system initialized")
            
        except ImportError:
            logger.error("❌ scikit-learn not available for fallback system")
            raise
    
    def _load_sample_knowledge(self) -> List[Dict[str, Any]]:
        """Load sample knowledge base for testing"""
        return [
            {
                'id': 'mt_income_tax_2025',
                'title': 'Malta Income Tax Rates 2025',
                'content': '''Malta operates a progressive income tax system with the following rates for 2025:
                
                Tax-free threshold: €9,100
                15% on income from €9,101 to €14,500
                25% on income from €14,501 to €19,500
                25% on income from €19,501 to €60,000
                35% on income above €60,000
                
                Married couples filing jointly receive an additional deduction of €600 on top of the standard €1,200 personal allowance.
                
                Self-employed individuals can deduct business expenses including home office expenses, professional development, business equipment, travel expenses, and professional insurance premiums.''',
                'jurisdiction': 'MT',
                'language': 'en',
                'document_type': 'regulation',
                'tags': ['income_tax', 'rates', 'deductions', 'self_employed'],
                'source_authority': 'Inland Revenue Department'
            },
            {
                'id': 'mt_vat_2025',
                'title': 'Malta VAT Rates and Registration',
                'content': '''Value Added Tax (VAT) in Malta for 2025:
                
                Standard Rate: 18%
                Reduced Rate: 5% (applies to accommodation, books, newspapers, certain food items)
                Super Reduced Rate: 7% (applies to certain medical equipment, cultural events)
                Zero Rate: 0% (applies to exports, international transport)
                
                VAT Registration Requirements:
                - Mandatory registration if annual turnover exceeds €35,000
                - Voluntary registration available for lower turnovers
                - Registration must be completed within 10 days of exceeding threshold
                
                VAT Returns:
                - Monthly returns for businesses with turnover > €700,000
                - Quarterly returns for smaller businesses
                - Annual returns for very small businesses (turnover < €56,000)''',
                'jurisdiction': 'MT',
                'language': 'en',
                'document_type': 'regulation',
                'tags': ['vat', 'registration', 'rates', 'returns'],
                'source_authority': 'Inland Revenue Department'
            },
            {
                'id': 'mt_corporate_tax_2025',
                'title': 'Malta Corporate Tax and Business Registration',
                'content': '''Corporate Income Tax in Malta:
                
                Standard Corporate Tax Rate: 35%
                
                Tax Refund System:
                - Shareholders may claim refunds of tax paid by the company
                - Full imputation system reduces effective tax rate
                - Refunds available for: 6/7ths for trading income, 5/7ths for passive income
                
                Business Registration Requirements:
                - All companies must register with Malta Business Registry
                - Minimum share capital: €1,165 for private companies
                - At least one director must be resident in Malta or EU
                - Annual returns must be filed by March 31st
                
                Allowable Business Deductions:
                - Salaries and wages, Rent and utilities, Professional fees
                - Depreciation on business assets, Research and development expenses''',
                'jurisdiction': 'MT',
                'language': 'en',
                'document_type': 'regulation',
                'tags': ['corporate_tax', 'business_registration', 'deductions', 'refunds'],
                'source_authority': 'Inland Revenue Department'
            },
            {
                'id': 'fr_income_tax_2025',
                'title': 'Barème de l\'impôt sur le revenu France 2025',
                'content': '''Le barème progressif de l'impôt sur le revenu en France pour 2025 :
                
                Tranche exonérée : jusqu'à 10 777 €
                Taux de 11% : de 10 778 € à 27 478 €
                Taux de 30% : de 27 479 € à 78 570 €
                Taux de 41% : de 78 571 € à 168 994 €
                Taux de 45% : au-delà de 168 995 €
                
                Abattements et déductions :
                - Abattement de 10% sur les salaires (minimum 448 €, maximum 13 522 €)
                - Frais réels déductibles sur justificatifs
                - Quotient familial selon le nombre de parts
                
                Dates importantes :
                - Déclaration en ligne : avant mi-mai à fin mai selon le département
                - Paiement : septembre pour l'acompte, octobre pour le solde''',
                'jurisdiction': 'FR',
                'language': 'fr',
                'document_type': 'regulation',
                'tags': ['impot_revenu', 'bareme', 'abattements', 'declaration'],
                'source_authority': 'Direction générale des Finances publiques'
            },
            {
                'id': 'fr_tva_2025',
                'title': 'TVA en France - Taux et obligations 2025',
                'content': '''Taux de TVA applicables en France en 2025 :
                
                Taux normal : 20%
                Taux réduit : 5,5% (produits alimentaires, livres, médicaments)
                Taux super réduit : 2,1% (médicaments remboursés, presse)
                Taux particulier : 10% (restauration, travaux de rénovation)
                
                Obligations des assujettis :
                - Seuil de franchise : 36 800 € (services) / 91 900 € (ventes)
                - Déclaration mensuelle si CA > 4 000 000 €
                - Déclaration trimestrielle pour les autres
                - Facturation obligatoire avec mention de la TVA
                
                Déductions possibles :
                - TVA sur achats professionnels, TVA sur immobilisations, TVA sur frais généraux''',
                'jurisdiction': 'FR',
                'language': 'fr',
                'document_type': 'regulation',
                'tags': ['tva', 'taux', 'obligations', 'franchise'],
                'source_authority': 'Direction générale des Finances publiques'
            }
        ]
    
    async def initialize_knowledge_base(self, documents: List[Dict[str, Any]] = None):
        """Initialize knowledge base with documents"""
        try:
            # Use provided documents or sample knowledge
            docs = documents or self.sample_knowledge
            
            if self.use_pinecone and self.pinecone_client:
                await self._initialize_pinecone_index(docs)
            else:
                await self._initialize_fallback_index(docs)
            
            logger.info(f"✅ Knowledge base initialized with {len(docs)} documents")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize knowledge base: {e}")
            raise
    
    async def _initialize_pinecone_index(self, documents: List[Dict[str, Any]]):
        """Initialize Pinecone index with documents"""
        try:
            # Create or connect to index
            index_name = os.getenv('PINECONE_INDEX_NAME', 'tax-agent-knowledge')
            
            # Check if index exists
            existing_indexes = self.pinecone_client.list_indexes()
            
            if index_name not in [idx.name for idx in existing_indexes]:
                # Create new index
                self.pinecone_client.create_index(
                    name=index_name,
                    dimension=1536,  # OpenAI embedding dimension
                    metric='cosine'
                )
                logger.info(f"Created new Pinecone index: {index_name}")
            
            # Connect to index
            self.index = self.pinecone_client.Index(index_name)
            
            # Generate embeddings and upsert documents
            for doc in documents:
                embedding = await self._generate_embedding(doc['content'])
                
                self.index.upsert([(
                    doc['id'],
                    embedding,
                    {
                        'title': doc['title'],
                        'content': doc['content'][:1000],  # Limit metadata size
                        'jurisdiction': doc['jurisdiction'],
                        'language': doc['language'],
                        'document_type': doc['document_type'],
                        'source_authority': doc.get('source_authority', ''),
                        'tags': ','.join(doc.get('tags', []))
                    }
                )])
            
            logger.info("✅ Pinecone index initialized with documents")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Pinecone index: {e}")
            # Fall back to TF-IDF
            self.use_pinecone = False
            self.use_mock = True
            await self._initialize_fallback_index(documents)
    
    async def _initialize_fallback_index(self, documents: List[Dict[str, Any]]):
        """Initialize fallback TF-IDF index"""
        try:
            self.documents = documents
            
            # Extract text content for TF-IDF
            texts = [doc['content'] for doc in documents]
            
            # Fit TF-IDF vectorizer
            self.document_vectors = self.tfidf_vectorizer.fit_transform(texts)
            
            logger.info("✅ Fallback TF-IDF index initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize fallback index: {e}")
            raise
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI"""
        try:
            if not self.openai_client:
                raise ValueError("OpenAI client not initialized")
            
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=text[:8000]  # Limit input length
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            # Return random embedding as fallback
            return np.random.rand(1536).tolist()
    
    async def search(self, query: str, jurisdiction: str = None, language: str = None,
                    limit: int = 5) -> List[Dict[str, Any]]:
        """Search knowledge base"""
        try:
            if self.use_pinecone and self.index:
                return await self._search_pinecone(query, jurisdiction, language, limit)
            else:
                return await self._search_fallback(query, jurisdiction, language, limit)
                
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    async def _search_pinecone(self, query: str, jurisdiction: str = None,
                             language: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Search using Pinecone"""
        try:
            # Generate query embedding
            query_embedding = await self._generate_embedding(query)
            
            # Build filter
            filter_dict = {}
            if jurisdiction:
                filter_dict['jurisdiction'] = jurisdiction
            if language:
                filter_dict['language'] = language
            
            # Search
            results = self.index.query(
                vector=query_embedding,
                top_k=limit,
                include_metadata=True,
                filter=filter_dict if filter_dict else None
            )
            
            # Format results
            formatted_results = []
            for match in results.matches:
                formatted_results.append({
                    'id': match.id,
                    'score': float(match.score),
                    'title': match.metadata.get('title', ''),
                    'content': match.metadata.get('content', ''),
                    'jurisdiction': match.metadata.get('jurisdiction', ''),
                    'language': match.metadata.get('language', ''),
                    'document_type': match.metadata.get('document_type', ''),
                    'source_authority': match.metadata.get('source_authority', ''),
                    'tags': match.metadata.get('tags', '').split(',') if match.metadata.get('tags') else []
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Pinecone search failed: {e}")
            return []
    
    async def _search_fallback(self, query: str, jurisdiction: str = None,
                             language: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Search using TF-IDF fallback"""
        try:
            if not self.document_vectors or not self.documents:
                await self.initialize_knowledge_base()
            
            # Transform query
            query_vector = self.tfidf_vectorizer.transform([query])
            
            # Calculate similarities
            from sklearn.metrics.pairwise import cosine_similarity
            similarities = cosine_similarity(query_vector, self.document_vectors).flatten()
            
            # Get top results
            top_indices = similarities.argsort()[-limit:][::-1]
            
            results = []
            for idx in top_indices:
                if similarities[idx] > 0.1:  # Minimum similarity threshold
                    doc = self.documents[idx]
                    
                    # Apply filters
                    if jurisdiction and doc.get('jurisdiction') != jurisdiction:
                        continue
                    if language and doc.get('language') != language:
                        continue
                    
                    results.append({
                        'id': doc['id'],
                        'score': float(similarities[idx]),
                        'title': doc['title'],
                        'content': doc['content'],
                        'jurisdiction': doc['jurisdiction'],
                        'language': doc['language'],
                        'document_type': doc['document_type'],
                        'source_authority': doc.get('source_authority', ''),
                        'tags': doc.get('tags', [])
                    })
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Fallback search failed: {e}")
            return []
    
    async def add_document(self, document: Dict[str, Any]) -> bool:
        """Add document to knowledge base"""
        try:
            if self.use_pinecone and self.index:
                return await self._add_document_pinecone(document)
            else:
                return await self._add_document_fallback(document)
                
        except Exception as e:
            logger.error(f"Failed to add document: {e}")
            return False
    
    async def _add_document_pinecone(self, document: Dict[str, Any]) -> bool:
        """Add document to Pinecone index"""
        try:
            embedding = await self._generate_embedding(document['content'])
            
            self.index.upsert([(
                document['id'],
                embedding,
                {
                    'title': document['title'],
                    'content': document['content'][:1000],
                    'jurisdiction': document['jurisdiction'],
                    'language': document['language'],
                    'document_type': document['document_type'],
                    'source_authority': document.get('source_authority', ''),
                    'tags': ','.join(document.get('tags', []))
                }
            )])
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add document to Pinecone: {e}")
            return False
    
    async def _add_document_fallback(self, document: Dict[str, Any]) -> bool:
        """Add document to fallback index"""
        try:
            # Add to documents list
            self.documents.append(document)
            
            # Rebuild TF-IDF index
            texts = [doc['content'] for doc in self.documents]
            self.document_vectors = self.tfidf_vectorizer.fit_transform(texts)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add document to fallback: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector search statistics"""
        try:
            stats = {
                'service_type': 'pinecone' if self.use_pinecone else 'tfidf_fallback',
                'openai_available': self.openai_client is not None,
                'pinecone_available': self.use_pinecone,
                'documents_count': len(self.documents) if self.documents else 0,
                'status': 'operational'
            }
            
            if self.use_pinecone and hasattr(self, 'index'):
                try:
                    index_stats = self.index.describe_index_stats()
                    stats['pinecone_stats'] = {
                        'total_vectors': index_stats.total_vector_count,
                        'dimension': index_stats.dimension
                    }
                except:
                    stats['pinecone_stats'] = 'unavailable'
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {'status': 'error', 'error': str(e)}

# Global instance
vector_search_service = VectorSearchService()

