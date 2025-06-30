"""
OpenAI Agents SDK Implementation
Advanced autonomous agent with reasoning, planning, and tool orchestration
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

import openai
from openai import OpenAI
import instructor
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    ANALYZING = "analyzing"
    GATHERING_INFO = "gathering_info"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"

class ConfidenceLevel(Enum):
    """Agent confidence levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VERY_LOW = "very_low"

@dataclass
class AgentMemory:
    """Agent memory structure"""
    user_id: str
    conversation_history: List[Dict[str, Any]]
    user_context: Dict[str, Any]
    task_history: List[Dict[str, Any]]
    documents: List[Dict[str, Any]]
    preferences: Dict[str, Any]

class TaskRequirement(BaseModel):
    """Task requirement model"""
    name: str = Field(description="Name of the required information")
    description: str = Field(description="Description of what is needed")
    type: str = Field(description="Type of information (document, number, text, etc.)")
    required: bool = Field(description="Whether this is mandatory")
    current_value: Optional[Any] = Field(default=None, description="Current value if available")
    source: Optional[str] = Field(default=None, description="Source of the information")

class TaskAnalysis(BaseModel):
    """Task analysis result"""
    task_type: str = Field(description="Type of task identified")
    jurisdiction: str = Field(description="Relevant jurisdiction")
    complexity: str = Field(description="Task complexity level")
    requirements: List[TaskRequirement] = Field(description="List of requirements")
    missing_info: List[str] = Field(description="List of missing information")
    confidence: str = Field(description="Confidence level in analysis")
    estimated_duration: str = Field(description="Estimated completion time")
    next_steps: List[str] = Field(description="Recommended next steps")

class AgentResponse(BaseModel):
    """Agent response model"""
    message: str = Field(description="Response message to user")
    task_status: str = Field(description="Current task status")
    confidence: str = Field(description="Confidence level")
    requirements_met: bool = Field(description="Whether all requirements are met")
    missing_info: List[str] = Field(description="List of missing information")
    suggested_actions: List[str] = Field(description="Suggested user actions")
    generated_content: Optional[Dict[str, Any]] = Field(default=None, description="Generated content if any")

class TaxCalculationTool(BaseModel):
    """Tax calculation tool"""
    income: float = Field(description="Annual income amount")
    jurisdiction: str = Field(description="Tax jurisdiction code")
    filing_status: str = Field(description="Filing status (single, married, etc.)")
    deductions: Optional[float] = Field(default=0, description="Total deductions")
    
class DocumentAnalysisTool(BaseModel):
    """Document analysis tool"""
    document_path: str = Field(description="Path to document")
    analysis_type: str = Field(description="Type of analysis needed")
    extract_data: bool = Field(default=True, description="Whether to extract structured data")

class FormGenerationTool(BaseModel):
    """Form generation tool"""
    form_type: str = Field(description="Type of tax form")
    jurisdiction: str = Field(description="Jurisdiction for the form")
    user_data: Dict[str, Any] = Field(description="User data for form filling")

class AutonomousTaxAgent:
    """Autonomous Tax Agent with OpenAI Agents SDK"""
    
    def __init__(self):
        """Initialize the autonomous tax agent"""
        self.api_key = os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            raise ValueError("Missing OpenAI API key in environment variables")
        
        try:
            # Initialize OpenAI client with instructor for structured outputs
            self.client = instructor.from_openai(OpenAI(api_key=self.api_key))
            
            # Agent configuration
            self.model = "gpt-4o"
            self.max_tokens = 4000
            self.temperature = 0.1  # Low temperature for consistent reasoning
            
            # Tool registry
            self.tools = {
                "tax_calculation": self._tax_calculation_tool,
                "document_analysis": self._document_analysis_tool,
                "form_generation": self._form_generation_tool,
                "memory_search": self._memory_search_tool,
                "requirement_check": self._requirement_check_tool
            }
            
            # Memory storage
            self.memory_store = {}
            
            logger.info("✅ Autonomous Tax Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Autonomous Tax Agent: {e}")
            raise
    
    async def process_user_request(self, 
                                 user_id: str, 
                                 message: str, 
                                 context: Dict[str, Any] = None) -> AgentResponse:
        """
        Process user request with autonomous reasoning and planning
        
        Args:
            user_id: User identifier
            message: User message
            context: Additional context (jurisdiction, language, etc.)
            
        Returns:
            AgentResponse with reasoning and next steps
        """
        try:
            # Load user memory
            memory = self._load_user_memory(user_id)
            
            # Update context
            if context:
                memory.user_context.update(context)
            
            # Add message to conversation history
            memory.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "role": "user",
                "content": message,
                "context": context or {}
            })
            
            # Phase 1: Task Analysis and Requirement Detection
            task_analysis = await self._analyze_task(message, memory)
            
            # Phase 2: Pre-execution Reasoning
            reasoning_result = await self._pre_execution_reasoning(task_analysis, memory)
            
            # Phase 3: Information Gathering
            if reasoning_result["missing_info"]:
                response = await self._request_missing_information(reasoning_result, memory)
                response.task_status = TaskStatus.GATHERING_INFO.value
            else:
                # Phase 4: Task Execution
                response = await self._execute_task(task_analysis, memory)
                response.task_status = TaskStatus.COMPLETED.value
            
            # Phase 5: Memory Update
            await self._update_memory(user_id, memory, response)
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error processing user request: {e}")
            return AgentResponse(
                message=f"I encountered an error while processing your request: {str(e)}",
                task_status=TaskStatus.FAILED.value,
                confidence=ConfidenceLevel.VERY_LOW.value,
                requirements_met=False,
                missing_info=[],
                suggested_actions=["Please try rephrasing your request"]
            )
    
    async def _analyze_task(self, message: str, memory: AgentMemory) -> TaskAnalysis:
        """Analyze user task and identify requirements"""
        
        system_prompt = f"""
        You are an expert tax agent analyzing user requests. Based on the user's message and their context, 
        identify the task type, requirements, and missing information.
        
        User Context:
        - Jurisdiction: {memory.user_context.get('jurisdiction', 'Unknown')}
        - Language: {memory.user_context.get('language', 'en')}
        - User Type: {memory.user_context.get('user_type', 'individual')}
        
        Previous Conversations: {json.dumps(memory.conversation_history[-5:], indent=2)}
        
        Analyze the task comprehensively and identify all requirements.
        """
        
        try:
            analysis = self.client.chat.completions.create(
                model=self.model,
                response_model=TaskAnalysis,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Please analyze this request: {message}"}
                ],
                temperature=self.temperature
            )
            
            logger.info(f"✅ Task analysis completed: {analysis.task_type}")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Task analysis failed: {e}")
            # Return default analysis
            return TaskAnalysis(
                task_type="general_inquiry",
                jurisdiction=memory.user_context.get('jurisdiction', 'MT'),
                complexity="medium",
                requirements=[],
                missing_info=["Unable to analyze requirements"],
                confidence=ConfidenceLevel.LOW.value,
                estimated_duration="unknown",
                next_steps=["Please provide more specific information"]
            )
    
    async def _pre_execution_reasoning(self, 
                                     task_analysis: TaskAnalysis, 
                                     memory: AgentMemory) -> Dict[str, Any]:
        """Perform pre-execution reasoning to determine readiness"""
        
        # Check what information we have vs what we need
        available_info = {}
        missing_info = []
        
        # Check user context
        for req in task_analysis.requirements:
            if req.required:
                # Check if we have this information in memory
                value = self._search_memory_for_requirement(req, memory)
                if value:
                    available_info[req.name] = value
                    req.current_value = value
                    req.source = "memory"
                else:
                    missing_info.append(req.name)
        
        # Determine if we can proceed
        can_proceed = len(missing_info) == 0
        confidence = ConfidenceLevel.HIGH if can_proceed else ConfidenceLevel.MEDIUM
        
        return {
            "can_proceed": can_proceed,
            "available_info": available_info,
            "missing_info": missing_info,
            "confidence": confidence.value,
            "requirements": task_analysis.requirements
        }
    
    async def _request_missing_information(self, 
                                         reasoning_result: Dict[str, Any], 
                                         memory: AgentMemory) -> AgentResponse:
        """Generate intelligent questions for missing information"""
        
        missing_info = reasoning_result["missing_info"]
        language = memory.user_context.get('language', 'en')
        
        # Generate contextual questions
        questions = []
        for info in missing_info:
            question = self._generate_question_for_requirement(info, language, memory)
            questions.append(question)
        
        if language == 'fr':
            message = f"Pour continuer avec votre demande, j'ai besoin de quelques informations supplémentaires:\n\n"
            message += "\n".join([f"• {q}" for q in questions])
            message += "\n\nPouvez-vous me fournir ces détails?"
        else:
            message = f"To proceed with your request, I need some additional information:\n\n"
            message += "\n".join([f"• {q}" for q in questions])
            message += "\n\nCould you please provide these details?"
        
        return AgentResponse(
            message=message,
            task_status=TaskStatus.GATHERING_INFO.value,
            confidence=reasoning_result["confidence"],
            requirements_met=False,
            missing_info=missing_info,
            suggested_actions=["Provide the requested information", "Upload relevant documents"]
        )
    
    async def _execute_task(self, 
                          task_analysis: TaskAnalysis, 
                          memory: AgentMemory) -> AgentResponse:
        """Execute the identified task"""
        
        try:
            # Determine which tool to use based on task type
            if "tax" in task_analysis.task_type.lower() and "calculation" in task_analysis.task_type.lower():
                result = await self._tax_calculation_tool(task_analysis, memory)
            elif "document" in task_analysis.task_type.lower():
                result = await self._document_analysis_tool(task_analysis, memory)
            elif "form" in task_analysis.task_type.lower():
                result = await self._form_generation_tool(task_analysis, memory)
            else:
                result = await self._general_assistance_tool(task_analysis, memory)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Task execution failed: {e}")
            return AgentResponse(
                message=f"I encountered an error while executing your task: {str(e)}",
                task_status=TaskStatus.FAILED.value,
                confidence=ConfidenceLevel.LOW.value,
                requirements_met=False,
                missing_info=[],
                suggested_actions=["Please try again or contact support"]
            )
    
    async def _tax_calculation_tool(self, 
                                  task_analysis: TaskAnalysis, 
                                  memory: AgentMemory) -> AgentResponse:
        """Execute tax calculation"""
        
        # Extract required values from requirements
        income = None
        jurisdiction = task_analysis.jurisdiction
        filing_status = "single"
        
        for req in task_analysis.requirements:
            if "income" in req.name.lower() and req.current_value:
                income = float(req.current_value)
            elif "status" in req.name.lower() and req.current_value:
                filing_status = req.current_value
        
        if not income:
            return AgentResponse(
                message="I need your income amount to calculate taxes.",
                task_status=TaskStatus.GATHERING_INFO.value,
                confidence=ConfidenceLevel.LOW.value,
                requirements_met=False,
                missing_info=["income"],
                suggested_actions=["Provide your annual income amount"]
            )
        
        # Perform tax calculation (simplified Malta tax calculation)
        if jurisdiction == "MT":
            tax_result = self._calculate_malta_tax(income, filing_status)
        else:
            tax_result = {"error": "Jurisdiction not supported yet"}
        
        language = memory.user_context.get('language', 'en')
        
        if language == 'fr':
            message = f"Voici votre calcul d'impôt pour Malte:\n\n"
            message += f"• Revenu annuel: €{income:,.2f}\n"
            message += f"• Impôt dû: €{tax_result.get('tax_due', 0):,.2f}\n"
            message += f"• Taux effectif: {tax_result.get('effective_rate', 0):.2f}%\n"
        else:
            message = f"Here's your tax calculation for Malta:\n\n"
            message += f"• Annual Income: €{income:,.2f}\n"
            message += f"• Tax Due: €{tax_result.get('tax_due', 0):,.2f}\n"
            message += f"• Effective Rate: {tax_result.get('effective_rate', 0):.2f}%\n"
        
        return AgentResponse(
            message=message,
            task_status=TaskStatus.COMPLETED.value,
            confidence=ConfidenceLevel.HIGH.value,
            requirements_met=True,
            missing_info=[],
            suggested_actions=["Generate tax form", "Save calculation", "Ask follow-up questions"],
            generated_content={"tax_calculation": tax_result}
        )
    
    def _calculate_malta_tax(self, income: float, filing_status: str) -> Dict[str, Any]:
        """Calculate Malta income tax"""
        
        # Malta 2025 tax brackets (simplified)
        brackets = [
            (9100, 0.0),      # First €9,100 - 0%
            (14500, 0.15),    # €9,101 to €14,500 - 15%
            (19500, 0.25),    # €14,501 to €19,500 - 25%
            (60000, 0.25),    # €19,501 to €60,000 - 25%
            (float('inf'), 0.35)  # Over €60,000 - 35%
        ]
        
        tax_due = 0
        remaining_income = income
        
        for i, (bracket_limit, rate) in enumerate(brackets):
            if remaining_income <= 0:
                break
                
            if i == 0:
                taxable_in_bracket = min(remaining_income, bracket_limit)
            else:
                prev_limit = brackets[i-1][0]
                taxable_in_bracket = min(remaining_income, bracket_limit - prev_limit)
            
            tax_due += taxable_in_bracket * rate
            remaining_income -= taxable_in_bracket
        
        effective_rate = (tax_due / income * 100) if income > 0 else 0
        
        return {
            "income": income,
            "tax_due": round(tax_due, 2),
            "effective_rate": round(effective_rate, 2),
            "filing_status": filing_status,
            "jurisdiction": "MT",
            "calculation_date": datetime.now().isoformat()
        }
    
    async def _document_analysis_tool(self, 
                                    task_analysis: TaskAnalysis, 
                                    memory: AgentMemory) -> AgentResponse:
        """Analyze uploaded documents"""
        
        # This would integrate with document processing services
        # For now, return a placeholder response
        
        language = memory.user_context.get('language', 'en')
        
        if language == 'fr':
            message = "Analyse de document en cours. Cette fonctionnalité sera bientôt disponible."
        else:
            message = "Document analysis in progress. This feature will be available soon."
        
        return AgentResponse(
            message=message,
            task_status=TaskStatus.PENDING.value,
            confidence=ConfidenceLevel.MEDIUM.value,
            requirements_met=False,
            missing_info=["document_processing_service"],
            suggested_actions=["Upload document", "Provide document details"]
        )
    
    async def _form_generation_tool(self, 
                                  task_analysis: TaskAnalysis, 
                                  memory: AgentMemory) -> AgentResponse:
        """Generate tax forms"""
        
        # This would integrate with form generation services
        # For now, return a placeholder response
        
        language = memory.user_context.get('language', 'en')
        
        if language == 'fr':
            message = "Génération de formulaire en cours. Cette fonctionnalité sera bientôt disponible."
        else:
            message = "Form generation in progress. This feature will be available soon."
        
        return AgentResponse(
            message=message,
            task_status=TaskStatus.PENDING.value,
            confidence=ConfidenceLevel.MEDIUM.value,
            requirements_met=False,
            missing_info=["form_generation_service"],
            suggested_actions=["Provide form requirements", "Specify form type"]
        )
    
    async def _general_assistance_tool(self, 
                                     task_analysis: TaskAnalysis, 
                                     memory: AgentMemory) -> AgentResponse:
        """Provide general tax assistance"""
        
        # Generate helpful response based on task analysis
        language = memory.user_context.get('language', 'en')
        jurisdiction = task_analysis.jurisdiction
        
        # Use OpenAI to generate contextual response
        system_prompt = f"""
        You are a helpful tax assistant for {jurisdiction}. Provide accurate, helpful information 
        in {language}. Be specific and actionable.
        
        User context: {json.dumps(memory.user_context, indent=2)}
        Task analysis: {json.dumps(task_analysis.dict(), indent=2)}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Please help with: {task_analysis.task_type}"}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            message = response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"❌ General assistance failed: {e}")
            if language == 'fr':
                message = "Je peux vous aider avec vos questions fiscales. Pouvez-vous être plus spécifique?"
            else:
                message = "I can help you with your tax questions. Could you be more specific?"
        
        return AgentResponse(
            message=message,
            task_status=TaskStatus.COMPLETED.value,
            confidence=ConfidenceLevel.MEDIUM.value,
            requirements_met=True,
            missing_info=[],
            suggested_actions=["Ask follow-up questions", "Request specific calculations"]
        )
    
    def _load_user_memory(self, user_id: str) -> AgentMemory:
        """Load user memory from storage"""
        
        if user_id not in self.memory_store:
            self.memory_store[user_id] = AgentMemory(
                user_id=user_id,
                conversation_history=[],
                user_context={},
                task_history=[],
                documents=[],
                preferences={}
            )
        
        return self.memory_store[user_id]
    
    async def _update_memory(self, 
                           user_id: str, 
                           memory: AgentMemory, 
                           response: AgentResponse):
        """Update user memory with new information"""
        
        # Add agent response to conversation history
        memory.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "role": "assistant",
            "content": response.message,
            "task_status": response.task_status,
            "confidence": response.confidence
        })
        
        # Add to task history if completed
        if response.task_status == TaskStatus.COMPLETED.value:
            memory.task_history.append({
                "timestamp": datetime.now().isoformat(),
                "task_type": "tax_assistance",
                "status": response.task_status,
                "generated_content": response.generated_content
            })
        
        # Update memory store
        self.memory_store[user_id] = memory
        
        # TODO: Persist to database/vector store
        logger.info(f"✅ Memory updated for user {user_id}")
    
    def _search_memory_for_requirement(self, 
                                     requirement: TaskRequirement, 
                                     memory: AgentMemory) -> Optional[Any]:
        """Search memory for required information"""
        
        # Search in user context
        for key, value in memory.user_context.items():
            if requirement.name.lower() in key.lower():
                return value
        
        # Search in conversation history
        for conv in memory.conversation_history:
            if requirement.name.lower() in conv.get("content", "").lower():
                # Extract value using simple pattern matching
                # TODO: Implement more sophisticated extraction
                pass
        
        # Search in task history
        for task in memory.task_history:
            if task.get("generated_content"):
                content = task["generated_content"]
                if requirement.name.lower() in str(content).lower():
                    # Extract relevant value
                    # TODO: Implement extraction logic
                    pass
        
        return None
    
    def _generate_question_for_requirement(self, 
                                         requirement_name: str, 
                                         language: str, 
                                         memory: AgentMemory) -> str:
        """Generate contextual question for missing requirement"""
        
        # Simple question generation based on requirement name
        questions = {
            'en': {
                'income': "What is your annual income?",
                'filing_status': "What is your filing status (single, married, etc.)?",
                'deductions': "Do you have any deductions to claim?",
                'documents': "Do you have any relevant documents to upload?",
                'jurisdiction': "Which jurisdiction are you filing in?",
                'year': "Which tax year are you asking about?"
            },
            'fr': {
                'income': "Quel est votre revenu annuel?",
                'filing_status': "Quel est votre statut de déclaration (célibataire, marié, etc.)?",
                'deductions': "Avez-vous des déductions à réclamer?",
                'documents': "Avez-vous des documents pertinents à télécharger?",
                'jurisdiction': "Dans quelle juridiction déclarez-vous?",
                'year': "De quelle année fiscale parlez-vous?"
            }
        }
        
        lang_questions = questions.get(language, questions['en'])
        
        # Find best matching question
        for key, question in lang_questions.items():
            if key in requirement_name.lower():
                return question
        
        # Default question
        if language == 'fr':
            return f"Pouvez-vous fournir des informations sur: {requirement_name}?"
        else:
            return f"Could you provide information about: {requirement_name}?"
    
    # Tool implementations
    async def _tax_calculation_tool(self, *args, **kwargs):
        """Tax calculation tool implementation"""
        return await self._tax_calculation_tool(*args, **kwargs)
    
    async def _document_analysis_tool(self, *args, **kwargs):
        """Document analysis tool implementation"""
        return await self._document_analysis_tool(*args, **kwargs)
    
    async def _form_generation_tool(self, *args, **kwargs):
        """Form generation tool implementation"""
        return await self._form_generation_tool(*args, **kwargs)
    
    async def _memory_search_tool(self, query: str, user_id: str) -> Dict[str, Any]:
        """Search user memory for relevant information"""
        memory = self._load_user_memory(user_id)
        
        # Simple keyword search in memory
        results = []
        
        # Search conversation history
        for conv in memory.conversation_history:
            if query.lower() in conv.get("content", "").lower():
                results.append({
                    "type": "conversation",
                    "content": conv["content"],
                    "timestamp": conv["timestamp"]
                })
        
        # Search task history
        for task in memory.task_history:
            if query.lower() in str(task).lower():
                results.append({
                    "type": "task",
                    "content": task,
                    "timestamp": task["timestamp"]
                })
        
        return {"results": results, "count": len(results)}
    
    async def _requirement_check_tool(self, 
                                    requirements: List[TaskRequirement], 
                                    user_id: str) -> Dict[str, Any]:
        """Check if requirements are met"""
        memory = self._load_user_memory(user_id)
        
        met_requirements = []
        missing_requirements = []
        
        for req in requirements:
            value = self._search_memory_for_requirement(req, memory)
            if value:
                met_requirements.append(req.name)
            else:
                missing_requirements.append(req.name)
        
        return {
            "met": met_requirements,
            "missing": missing_requirements,
            "completion_rate": len(met_requirements) / len(requirements) if requirements else 1.0
        }

# Global agent instance
autonomous_agent = None

def get_autonomous_agent() -> AutonomousTaxAgent:
    """Get or create autonomous agent instance"""
    global autonomous_agent
    
    if autonomous_agent is None:
        autonomous_agent = AutonomousTaxAgent()
    
    return autonomous_agent

