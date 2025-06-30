"""
Enhanced Agent SDK for Malta Tax AI
Provides intelligent agent capabilities with vector search, reasoning, and context awareness
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import re

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import required packages
import openai
from vector_search_service import (
    vector_search_service, search_knowledge, VectorDocument, 
    SearchQuery, SearchResult, DocumentType
)

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Configuration
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o')
AGENT_MAX_TOKENS = int(os.getenv('AGENT_MAX_TOKENS', '4000'))
AGENT_TEMPERATURE = float(os.getenv('AGENT_TEMPERATURE', '0.1'))
REASONING_DEPTH = int(os.getenv('REASONING_DEPTH', '3'))


class QueryType(Enum):
    """Types of user queries"""
    TAX_CALCULATION = "tax_calculation"
    TAX_REGULATION = "tax_regulation"
    FORM_ASSISTANCE = "form_assistance"
    COMPLIANCE_CHECK = "compliance_check"
    GENERAL_QUESTION = "general_question"
    PROCEDURAL_GUIDANCE = "procedural_guidance"
    CASE_SPECIFIC = "case_specific"
    UNKNOWN = "unknown"


class ConfidenceLevel(Enum):
    """Confidence levels for agent responses"""
    HIGH = "high"          # 90-100%
    MEDIUM = "medium"      # 70-89%
    LOW = "low"           # 50-69%
    VERY_LOW = "very_low" # <50%


class ReasoningStep(Enum):
    """Steps in the reasoning process"""
    QUERY_ANALYSIS = "query_analysis"
    CONTEXT_GATHERING = "context_gathering"
    KNOWLEDGE_RETRIEVAL = "knowledge_retrieval"
    REASONING = "reasoning"
    RESPONSE_GENERATION = "response_generation"
    VALIDATION = "validation"


@dataclass
class UserContext:
    """User context for personalized responses"""
    user_id: str
    user_type: str  # individual, business, accountant, etc.
    jurisdiction: str = "malta"
    language: str = "en"
    tax_year: int = 2025
    previous_queries: List[str] = None
    preferences: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.previous_queries is None:
            self.previous_queries = []
        if self.preferences is None:
            self.preferences = {}


@dataclass
class QueryIntent:
    """Analyzed query intent"""
    query_type: QueryType
    entities: Dict[str, Any]
    keywords: List[str]
    confidence: float
    requires_calculation: bool = False
    requires_forms: bool = False
    requires_compliance_check: bool = False


@dataclass
class ReasoningTrace:
    """Trace of reasoning steps"""
    step: ReasoningStep
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    confidence: float
    duration_ms: float
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'step': self.step.value,
            'input_data': self.input_data,
            'output_data': self.output_data,
            'confidence': self.confidence,
            'duration_ms': self.duration_ms,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class AgentResponse:
    """Complete agent response with reasoning"""
    query: str
    response: str
    confidence: ConfidenceLevel
    sources: List[Dict[str, Any]]
    reasoning_trace: List[ReasoningTrace]
    suggestions: List[str]
    follow_up_questions: List[str]
    requires_human_review: bool = False
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'query': self.query,
            'response': self.response,
            'confidence': self.confidence.value,
            'sources': self.sources,
            'reasoning_trace': [trace.to_dict() for trace in self.reasoning_trace],
            'suggestions': self.suggestions,
            'follow_up_questions': self.follow_up_questions,
            'requires_human_review': self.requires_human_review,
            'metadata': self.metadata or {},
            'timestamp': datetime.utcnow().isoformat()
        }


class VectorSearchTool:
    """Tool for semantic search in knowledge base"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.VectorSearchTool")
    
    async def search(self, query: str, context: UserContext = None, 
                   max_results: int = 5) -> List[SearchResult]:
        """
        Search knowledge base with context awareness
        
        Args:
            query: Search query
            context: User context for filtering
            max_results: Maximum results to return
            
        Returns:
            List of search results
        """
        try:
            # Prepare filters based on context
            filters = {}
            if context:
                if context.jurisdiction != "malta":
                    # Add jurisdiction filter if not Malta
                    filters['jurisdiction'] = context.jurisdiction
                
                # Filter by user type if relevant
                if context.user_type in ['individual', 'business']:
                    filters['applicable_to'] = context.user_type
            
            # Create search query
            search_query = SearchQuery(
                query=query,
                filters=filters,
                max_results=max_results,
                user_context=asdict(context) if context else None
            )
            
            # Perform search
            results = await vector_search_service.search(search_query)
            
            self.logger.info(f"Vector search returned {len(results)} results for: {query[:50]}...")
            return results
            
        except Exception as e:
            self.logger.error(f"Vector search failed: {e}")
            return []
    
    async def find_similar_cases(self, case_description: str, 
                               max_results: int = 3) -> List[SearchResult]:
        """Find similar tax cases or scenarios"""
        try:
            # Search for case law and examples
            filters = {
                'document_type': ['case_law', 'calculation_example', 'procedure']
            }
            
            search_query = SearchQuery(
                query=case_description,
                filters=filters,
                max_results=max_results
            )
            
            results = await vector_search_service.search(search_query)
            return results
            
        except Exception as e:
            self.logger.error(f"Similar cases search failed: {e}")
            return []


class QueryAnalyzer:
    """Analyzes user queries to extract intent and entities"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.QueryAnalyzer")
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    async def analyze_query(self, query: str, context: UserContext = None) -> QueryIntent:
        """
        Analyze query to extract intent and entities
        
        Args:
            query: User query
            context: User context
            
        Returns:
            Query intent analysis
        """
        try:
            # Create analysis prompt
            analysis_prompt = self._create_analysis_prompt(query, context)
            
            # Call OpenAI for analysis
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert tax query analyzer for Malta tax system."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            # Parse response
            analysis_text = response.choices[0].message.content
            intent = self._parse_analysis_response(analysis_text)
            
            self.logger.info(f"Analyzed query type: {intent.query_type.value}")
            return intent
            
        except Exception as e:
            self.logger.error(f"Query analysis failed: {e}")
            # Return default intent
            return QueryIntent(
                query_type=QueryType.UNKNOWN,
                entities={},
                keywords=query.split(),
                confidence=0.0
            )
    
    def _create_analysis_prompt(self, query: str, context: UserContext = None) -> str:
        """Create prompt for query analysis"""
        prompt = f"""
        Analyze the following tax-related query and extract:
        1. Query type (tax_calculation, tax_regulation, form_assistance, compliance_check, general_question, procedural_guidance, case_specific)
        2. Key entities (amounts, dates, tax types, forms, etc.)
        3. Important keywords
        4. Whether it requires calculation, forms, or compliance checking
        5. Confidence level (0.0-1.0)
        
        Query: "{query}"
        """
        
        if context:
            prompt += f"""
            User Context:
            - User Type: {context.user_type}
            - Jurisdiction: {context.jurisdiction}
            - Tax Year: {context.tax_year}
            """
        
        prompt += """
        
        Respond in JSON format:
        {
            "query_type": "...",
            "entities": {"entity_type": "value", ...},
            "keywords": ["keyword1", "keyword2", ...],
            "requires_calculation": true/false,
            "requires_forms": true/false,
            "requires_compliance_check": true/false,
            "confidence": 0.0-1.0
        }
        """
        
        return prompt
    
    def _parse_analysis_response(self, response_text: str) -> QueryIntent:
        """Parse OpenAI response into QueryIntent"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                analysis_data = json.loads(json_match.group())
                
                return QueryIntent(
                    query_type=QueryType(analysis_data.get('query_type', 'unknown')),
                    entities=analysis_data.get('entities', {}),
                    keywords=analysis_data.get('keywords', []),
                    confidence=analysis_data.get('confidence', 0.0),
                    requires_calculation=analysis_data.get('requires_calculation', False),
                    requires_forms=analysis_data.get('requires_forms', False),
                    requires_compliance_check=analysis_data.get('requires_compliance_check', False)
                )
            
        except Exception as e:
            self.logger.error(f"Failed to parse analysis response: {e}")
        
        # Return default if parsing fails
        return QueryIntent(
            query_type=QueryType.UNKNOWN,
            entities={},
            keywords=[],
            confidence=0.0
        )


class ReasoningEngine:
    """Pre-execution reasoning engine for intelligent responses"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.ReasoningEngine")
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.vector_search = VectorSearchTool()
        self.query_analyzer = QueryAnalyzer()
    
    async def process_query(self, query: str, context: UserContext = None) -> AgentResponse:
        """
        Process query with full reasoning pipeline
        
        Args:
            query: User query
            context: User context
            
        Returns:
            Complete agent response
        """
        reasoning_trace = []
        start_time = datetime.utcnow()
        
        try:
            # Step 1: Query Analysis
            step_start = datetime.utcnow()
            intent = await self.query_analyzer.analyze_query(query, context)
            step_duration = (datetime.utcnow() - step_start).total_seconds() * 1000
            
            reasoning_trace.append(ReasoningTrace(
                step=ReasoningStep.QUERY_ANALYSIS,
                input_data={'query': query, 'context': asdict(context) if context else None},
                output_data={'intent': asdict(intent)},
                confidence=intent.confidence,
                duration_ms=step_duration,
                timestamp=step_start
            ))
            
            # Step 2: Context Gathering
            step_start = datetime.utcnow()
            enhanced_context = await self._gather_context(query, intent, context)
            step_duration = (datetime.utcnow() - step_start).total_seconds() * 1000
            
            reasoning_trace.append(ReasoningTrace(
                step=ReasoningStep.CONTEXT_GATHERING,
                input_data={'intent': asdict(intent)},
                output_data={'enhanced_context': enhanced_context},
                confidence=0.9,
                duration_ms=step_duration,
                timestamp=step_start
            ))
            
            # Step 3: Knowledge Retrieval
            step_start = datetime.utcnow()
            knowledge_results = await self._retrieve_knowledge(query, intent, context)
            step_duration = (datetime.utcnow() - step_start).total_seconds() * 1000
            
            reasoning_trace.append(ReasoningTrace(
                step=ReasoningStep.KNOWLEDGE_RETRIEVAL,
                input_data={'query': query, 'intent': asdict(intent)},
                output_data={'results_count': len(knowledge_results)},
                confidence=0.8 if knowledge_results else 0.3,
                duration_ms=step_duration,
                timestamp=step_start
            ))
            
            # Step 4: Reasoning and Response Generation
            step_start = datetime.utcnow()
            response_data = await self._generate_response(
                query, intent, knowledge_results, enhanced_context, context
            )
            step_duration = (datetime.utcnow() - step_start).total_seconds() * 1000
            
            reasoning_trace.append(ReasoningTrace(
                step=ReasoningStep.RESPONSE_GENERATION,
                input_data={'knowledge_count': len(knowledge_results)},
                output_data={'response_length': len(response_data['response'])},
                confidence=response_data['confidence'],
                duration_ms=step_duration,
                timestamp=step_start
            ))
            
            # Step 5: Validation
            step_start = datetime.utcnow()
            validation_result = await self._validate_response(response_data, intent)
            step_duration = (datetime.utcnow() - step_start).total_seconds() * 1000
            
            reasoning_trace.append(ReasoningTrace(
                step=ReasoningStep.VALIDATION,
                input_data={'response_data': response_data},
                output_data={'validation_result': validation_result},
                confidence=validation_result.get('confidence', 0.5),
                duration_ms=step_duration,
                timestamp=step_start
            ))
            
            # Create final response
            agent_response = AgentResponse(
                query=query,
                response=response_data['response'],
                confidence=self._calculate_overall_confidence(reasoning_trace),
                sources=response_data['sources'],
                reasoning_trace=reasoning_trace,
                suggestions=response_data.get('suggestions', []),
                follow_up_questions=response_data.get('follow_up_questions', []),
                requires_human_review=validation_result.get('requires_human_review', False),
                metadata={
                    'intent': asdict(intent),
                    'processing_time_ms': (datetime.utcnow() - start_time).total_seconds() * 1000
                }
            )
            
            self.logger.info(f"Processed query with confidence: {agent_response.confidence.value}")
            return agent_response
            
        except Exception as e:
            self.logger.error(f"Query processing failed: {e}")
            
            # Return error response
            return AgentResponse(
                query=query,
                response="I apologize, but I encountered an error processing your query. Please try rephrasing your question or contact support.",
                confidence=ConfidenceLevel.VERY_LOW,
                sources=[],
                reasoning_trace=reasoning_trace,
                suggestions=["Try rephrasing your question", "Contact support for assistance"],
                follow_up_questions=[],
                requires_human_review=True,
                metadata={'error': str(e)}
            )
    
    async def _gather_context(self, query: str, intent: QueryIntent, 
                            context: UserContext = None) -> Dict[str, Any]:
        """Gather additional context for the query"""
        enhanced_context = {
            'query_complexity': self._assess_query_complexity(query),
            'domain_specific': self._is_domain_specific(intent),
            'requires_calculation': intent.requires_calculation,
            'user_expertise_level': self._assess_user_expertise(context) if context else 'unknown'
        }
        
        return enhanced_context
    
    async def _retrieve_knowledge(self, query: str, intent: QueryIntent, 
                                context: UserContext = None) -> List[SearchResult]:
        """Retrieve relevant knowledge from vector database"""
        try:
            # Determine search strategy based on intent
            if intent.query_type == QueryType.TAX_CALCULATION:
                # Search for calculation examples and procedures
                results = await self.vector_search.search(
                    query + " calculation example procedure",
                    context,
                    max_results=5
                )
            elif intent.query_type == QueryType.TAX_REGULATION:
                # Search for regulations and legal documents
                results = await self.vector_search.search(
                    query + " regulation law",
                    context,
                    max_results=5
                )
            elif intent.query_type == QueryType.FORM_ASSISTANCE:
                # Search for form guidance and templates
                results = await self.vector_search.search(
                    query + " form guidance template",
                    context,
                    max_results=3
                )
            else:
                # General search
                results = await self.vector_search.search(query, context, max_results=5)
            
            # Also search for similar cases if relevant
            if intent.query_type in [QueryType.CASE_SPECIFIC, QueryType.COMPLIANCE_CHECK]:
                similar_cases = await self.vector_search.find_similar_cases(query, max_results=2)
                results.extend(similar_cases)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Knowledge retrieval failed: {e}")
            return []
    
    async def _generate_response(self, query: str, intent: QueryIntent, 
                               knowledge_results: List[SearchResult],
                               enhanced_context: Dict[str, Any],
                               user_context: UserContext = None) -> Dict[str, Any]:
        """Generate response using retrieved knowledge"""
        try:
            # Prepare knowledge context
            knowledge_context = ""
            sources = []
            
            for result in knowledge_results[:5]:  # Use top 5 results
                knowledge_context += f"\n\nSource: {result.document.title}\n"
                knowledge_context += f"Content: {result.document.content[:500]}...\n"
                knowledge_context += f"Relevance: {result.score:.2f}\n"
                
                sources.append({
                    'id': result.document.id,
                    'title': result.document.title,
                    'type': result.document.document_type.value,
                    'relevance_score': result.score,
                    'url': result.document.metadata.get('url', ''),
                    'excerpt': result.document.content[:200] + "..."
                })
            
            # Create response prompt
            response_prompt = self._create_response_prompt(
                query, intent, knowledge_context, enhanced_context, user_context
            )
            
            # Generate response
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert Malta tax advisor AI assistant."},
                    {"role": "user", "content": response_prompt}
                ],
                temperature=AGENT_TEMPERATURE,
                max_tokens=AGENT_MAX_TOKENS
            )
            
            response_text = response.choices[0].message.content
            
            # Extract structured response
            response_data = self._parse_response(response_text)
            response_data['sources'] = sources
            
            return response_data
            
        except Exception as e:
            self.logger.error(f"Response generation failed: {e}")
            return {
                'response': "I apologize, but I'm unable to provide a complete answer at this time.",
                'confidence': 0.1,
                'sources': [],
                'suggestions': [],
                'follow_up_questions': []
            }
    
    def _create_response_prompt(self, query: str, intent: QueryIntent,
                              knowledge_context: str, enhanced_context: Dict[str, Any],
                              user_context: UserContext = None) -> str:
        """Create prompt for response generation"""
        prompt = f"""
        You are an expert Malta tax advisor. Answer the following query using the provided knowledge context.
        
        User Query: "{query}"
        
        Query Analysis:
        - Type: {intent.query_type.value}
        - Entities: {intent.entities}
        - Keywords: {intent.keywords}
        - Requires Calculation: {intent.requires_calculation}
        - Requires Forms: {intent.requires_forms}
        
        Knowledge Context:
        {knowledge_context}
        
        Enhanced Context:
        {enhanced_context}
        """
        
        if user_context:
            prompt += f"""
            User Context:
            - User Type: {user_context.user_type}
            - Jurisdiction: {user_context.jurisdiction}
            - Tax Year: {user_context.tax_year}
            """
        
        prompt += """
        
        Instructions:
        1. Provide a clear, accurate, and helpful response
        2. Use the knowledge context to support your answer
        3. Include specific references to Malta tax law when relevant
        4. If calculations are needed, show step-by-step workings
        5. Suggest next steps or related actions
        6. Provide follow-up questions to help the user
        7. Indicate confidence level in your response
        
        Format your response as:
        RESPONSE: [Your detailed response]
        CONFIDENCE: [high/medium/low/very_low]
        SUGGESTIONS: [Bullet points of suggestions]
        FOLLOW_UP: [Relevant follow-up questions]
        """
        
        return prompt
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse structured response from OpenAI"""
        try:
            # Extract sections
            response_match = re.search(r'RESPONSE:\s*(.*?)(?=CONFIDENCE:|$)', response_text, re.DOTALL)
            confidence_match = re.search(r'CONFIDENCE:\s*(.*?)(?=SUGGESTIONS:|$)', response_text, re.DOTALL)
            suggestions_match = re.search(r'SUGGESTIONS:\s*(.*?)(?=FOLLOW_UP:|$)', response_text, re.DOTALL)
            followup_match = re.search(r'FOLLOW_UP:\s*(.*?)$', response_text, re.DOTALL)
            
            response = response_match.group(1).strip() if response_match else response_text
            confidence_text = confidence_match.group(1).strip().lower() if confidence_match else "medium"
            suggestions_text = suggestions_match.group(1).strip() if suggestions_match else ""
            followup_text = followup_match.group(1).strip() if followup_match else ""
            
            # Parse confidence
            confidence_map = {
                'high': 0.9,
                'medium': 0.7,
                'low': 0.5,
                'very_low': 0.3
            }
            confidence = confidence_map.get(confidence_text, 0.7)
            
            # Parse suggestions
            suggestions = []
            if suggestions_text:
                for line in suggestions_text.split('\n'):
                    line = line.strip()
                    if line and (line.startswith('-') or line.startswith('•')):
                        suggestions.append(line[1:].strip())
            
            # Parse follow-up questions
            follow_up_questions = []
            if followup_text:
                for line in followup_text.split('\n'):
                    line = line.strip()
                    if line and (line.startswith('-') or line.startswith('•') or line.endswith('?')):
                        follow_up_questions.append(line.lstrip('-•').strip())
            
            return {
                'response': response,
                'confidence': confidence,
                'suggestions': suggestions,
                'follow_up_questions': follow_up_questions
            }
            
        except Exception as e:
            self.logger.error(f"Failed to parse response: {e}")
            return {
                'response': response_text,
                'confidence': 0.5,
                'suggestions': [],
                'follow_up_questions': []
            }
    
    async def _validate_response(self, response_data: Dict[str, Any], 
                               intent: QueryIntent) -> Dict[str, Any]:
        """Validate response quality and accuracy"""
        validation_result = {
            'confidence': response_data['confidence'],
            'requires_human_review': False,
            'validation_notes': []
        }
        
        # Check response length
        if len(response_data['response']) < 50:
            validation_result['confidence'] *= 0.8
            validation_result['validation_notes'].append("Response may be too brief")
        
        # Check if response addresses the query type
        response_lower = response_data['response'].lower()
        if intent.requires_calculation and 'calculat' not in response_lower:
            validation_result['confidence'] *= 0.7
            validation_result['validation_notes'].append("May need calculation details")
        
        # Flag for human review if confidence is very low
        if validation_result['confidence'] < 0.5:
            validation_result['requires_human_review'] = True
        
        return validation_result
    
    def _calculate_overall_confidence(self, reasoning_trace: List[ReasoningTrace]) -> ConfidenceLevel:
        """Calculate overall confidence from reasoning trace"""
        if not reasoning_trace:
            return ConfidenceLevel.VERY_LOW
        
        # Weight different steps
        weights = {
            ReasoningStep.QUERY_ANALYSIS: 0.2,
            ReasoningStep.CONTEXT_GATHERING: 0.1,
            ReasoningStep.KNOWLEDGE_RETRIEVAL: 0.3,
            ReasoningStep.RESPONSE_GENERATION: 0.3,
            ReasoningStep.VALIDATION: 0.1
        }
        
        weighted_confidence = 0.0
        total_weight = 0.0
        
        for trace in reasoning_trace:
            weight = weights.get(trace.step, 0.1)
            weighted_confidence += trace.confidence * weight
            total_weight += weight
        
        if total_weight > 0:
            overall_confidence = weighted_confidence / total_weight
        else:
            overall_confidence = 0.5
        
        # Map to confidence levels
        if overall_confidence >= 0.9:
            return ConfidenceLevel.HIGH
        elif overall_confidence >= 0.7:
            return ConfidenceLevel.MEDIUM
        elif overall_confidence >= 0.5:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW
    
    def _assess_query_complexity(self, query: str) -> str:
        """Assess complexity of the query"""
        word_count = len(query.split())
        if word_count > 30:
            return "high"
        elif word_count > 15:
            return "medium"
        else:
            return "low"
    
    def _is_domain_specific(self, intent: QueryIntent) -> bool:
        """Check if query is domain-specific"""
        domain_types = [
            QueryType.TAX_CALCULATION,
            QueryType.TAX_REGULATION,
            QueryType.COMPLIANCE_CHECK,
            QueryType.FORM_ASSISTANCE
        ]
        return intent.query_type in domain_types
    
    def _assess_user_expertise(self, context: UserContext) -> str:
        """Assess user expertise level"""
        if context.user_type == "accountant":
            return "expert"
        elif context.user_type == "business":
            return "intermediate"
        else:
            return "beginner"


# Global instance
reasoning_engine = ReasoningEngine()


# Helper functions for easy access
async def process_tax_query(query: str, user_id: str = None, 
                          user_type: str = "individual") -> Dict[str, Any]:
    """
    Simple function to process tax queries
    
    Args:
        query: User query
        user_id: Optional user ID
        user_type: Type of user (individual, business, accountant)
        
    Returns:
        Agent response as dictionary
    """
    context = UserContext(
        user_id=user_id or "anonymous",
        user_type=user_type
    )
    
    response = await reasoning_engine.process_query(query, context)
    return response.to_dict()


async def get_tax_guidance(topic: str, user_type: str = "individual") -> Dict[str, Any]:
    """
    Get guidance on specific tax topic
    
    Args:
        topic: Tax topic to get guidance on
        user_type: Type of user
        
    Returns:
        Guidance response
    """
    query = f"Please provide guidance on {topic} for Malta tax purposes"
    return await process_tax_query(query, user_type=user_type)

