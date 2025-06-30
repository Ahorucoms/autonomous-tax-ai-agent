"""
AI Agent Service for Malta Tax AI
Implements the Pre-Execution Reasoning Loop and task orchestration
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

@dataclass
class TaskContext:
    """Context for task execution"""
    task_id: str
    user_id: str
    task_type: str
    jurisdiction: str
    required_fields: List[str]
    missing_fields: List[str]
    available_data: Dict[str, Any]
    execution_history: List[Dict[str, Any]]
    status: str
    created_at: datetime
    updated_at: datetime

@dataclass
class ReasoningStep:
    """Individual step in the reasoning process"""
    step_id: str
    step_type: str
    description: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    confidence: float
    timestamp: datetime

class PreExecutionReasoningLoop:
    """
    Implements the Pre-Execution Reasoning Loop as specified:
    1. Define end-state
    2. Inventory required data/docs
    3. Check existing memory & connected stores
    4. Ask only for true gaps
    5. Execute
    6. Store results & meta-learning
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.reasoning_history = []
    
    def execute_reasoning_loop(self, task_context: TaskContext) -> Dict[str, Any]:
        """Execute the complete reasoning loop for a task"""
        
        self.logger.info(f"Starting reasoning loop for task {task_context.task_id}")
        
        # Step 1: Define end-state
        end_state = self._define_end_state(task_context)
        
        # Step 2: Inventory required data/docs
        required_inventory = self._inventory_required_data(task_context)
        
        # Step 3: Check existing memory & connected stores
        available_data = self._check_existing_data(task_context)
        
        # Step 4: Identify true gaps
        gaps = self._identify_gaps(required_inventory, available_data)
        
        # Step 5: Generate execution plan
        execution_plan = self._generate_execution_plan(task_context, gaps)
        
        return {
            'end_state': end_state,
            'required_inventory': required_inventory,
            'available_data': available_data,
            'gaps': gaps,
            'execution_plan': execution_plan,
            'reasoning_steps': self.reasoning_history
        }
    
    def _define_end_state(self, task_context: TaskContext) -> Dict[str, Any]:
        """Define the desired end-state for the task"""
        
        end_states = {
            'income_tax_calculation': {
                'description': 'Complete income tax calculation with breakdown',
                'outputs': ['tax_due', 'effective_rate', 'marginal_rate', 'breakdown'],
                'format': 'structured_json',
                'validation_required': True
            },
            'vat_filing': {
                'description': 'VAT return filed with CFR and payment processed',
                'outputs': ['filing_receipt', 'payment_confirmation', 'compliance_status'],
                'format': 'official_documents',
                'validation_required': True
            },
            'document_processing': {
                'description': 'Documents processed, extracted, and stored',
                'outputs': ['extracted_data', 'document_metadata', 'storage_location'],
                'format': 'structured_data',
                'validation_required': False
            }
        }
        
        end_state = end_states.get(task_context.task_type, {
            'description': 'Generic task completion',
            'outputs': ['result'],
            'format': 'json',
            'validation_required': False
        })
        
        self._add_reasoning_step(
            'define_end_state',
            'Define the desired outcome for the task',
            {'task_type': task_context.task_type},
            end_state,
            0.95
        )
        
        return end_state
    
    def _inventory_required_data(self, task_context: TaskContext) -> Dict[str, Any]:
        """Inventory all required data and documents for the task"""
        
        requirements = {
            'income_tax_calculation': {
                'personal_info': ['name', 'id_number', 'tax_number', 'marital_status'],
                'income_data': ['salary', 'bonuses', 'other_income', 'deductions'],
                'documents': ['fs3_form', 'bank_statements', 'receipts'],
                'previous_data': ['previous_year_return', 'provisional_payments']
            },
            'vat_filing': {
                'business_info': ['vat_number', 'business_name', 'registration_details'],
                'transaction_data': ['sales', 'purchases', 'vat_collected', 'vat_paid'],
                'documents': ['invoices', 'receipts', 'bank_statements'],
                'previous_data': ['previous_vat_returns', 'carry_forward_credits']
            },
            'document_processing': {
                'document_info': ['document_type', 'file_format', 'language'],
                'processing_requirements': ['ocr_needed', 'extraction_fields', 'validation_rules'],
                'storage_requirements': ['retention_period', 'access_permissions', 'encryption_level']
            }
        }
        
        required = requirements.get(task_context.task_type, {
            'basic_info': ['user_id', 'task_description'],
            'documents': [],
            'data': []
        })
        
        self._add_reasoning_step(
            'inventory_required_data',
            'List all required data and documents',
            {'task_type': task_context.task_type},
            required,
            0.90
        )
        
        return required
    
    def _check_existing_data(self, task_context: TaskContext) -> Dict[str, Any]:
        """Check what data is already available in memory and connected stores"""
        
        # Simulate checking various data sources
        available_data = {
            'user_profile': task_context.available_data.get('user_profile', {}),
            'previous_tasks': task_context.available_data.get('previous_tasks', []),
            'uploaded_documents': task_context.available_data.get('documents', []),
            'connected_services': task_context.available_data.get('connected_services', {}),
            'cached_calculations': task_context.available_data.get('cached_calculations', {})
        }
        
        # Add jurisdiction-specific data
        if task_context.jurisdiction == 'malta':
            available_data['tax_rates'] = {
                'income_tax_bands': [
                    {'min': 0, 'max': 15000, 'rate': 0},
                    {'min': 15001, 'max': 23000, 'rate': 15},
                    {'min': 23001, 'max': 60000, 'rate': 25},
                    {'min': 60001, 'max': float('inf'), 'rate': 35}
                ],
                'vat_rates': {'standard': 18, 'reduced': [12, 7, 5], 'zero': 0},
                'social_security': {'class1': 10, 'class2': 15}
            }
        
        self._add_reasoning_step(
            'check_existing_data',
            'Inventory available data from all sources',
            {'jurisdiction': task_context.jurisdiction},
            available_data,
            0.85
        )
        
        return available_data
    
    def _identify_gaps(self, required: Dict[str, Any], available: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify gaps between required and available data"""
        
        gaps = []
        
        # Compare required vs available data
        for category, requirements in required.items():
            if isinstance(requirements, list):
                for item in requirements:
                    if not self._is_data_available(item, available):
                        gaps.append({
                            'category': category,
                            'item': item,
                            'type': 'missing_data',
                            'priority': self._get_priority(category, item),
                            'suggested_action': self._suggest_action(category, item)
                        })
        
        self._add_reasoning_step(
            'identify_gaps',
            'Find missing data that needs to be collected',
            {'required_categories': list(required.keys())},
            {'gaps_found': len(gaps), 'gaps': gaps},
            0.88
        )
        
        return gaps
    
    def _generate_execution_plan(self, task_context: TaskContext, gaps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a step-by-step execution plan"""
        
        plan = {
            'steps': [],
            'estimated_duration': 0,
            'confidence': 0.0,
            'requires_user_input': len(gaps) > 0
        }
        
        # Add data collection steps for gaps
        if gaps:
            plan['steps'].append({
                'step_id': 'collect_missing_data',
                'description': 'Collect missing information from user',
                'type': 'user_input',
                'inputs': gaps,
                'estimated_duration': len(gaps) * 30  # 30 seconds per gap
            })
        
        # Add task-specific execution steps
        if task_context.task_type == 'income_tax_calculation':
            plan['steps'].extend([
                {
                    'step_id': 'validate_income_data',
                    'description': 'Validate income and deduction data',
                    'type': 'validation',
                    'estimated_duration': 15
                },
                {
                    'step_id': 'calculate_tax',
                    'description': 'Calculate income tax using Malta tax bands',
                    'type': 'computation',
                    'estimated_duration': 10
                },
                {
                    'step_id': 'generate_breakdown',
                    'description': 'Generate detailed tax breakdown',
                    'type': 'formatting',
                    'estimated_duration': 5
                }
            ])
        
        plan['estimated_duration'] = sum(step['estimated_duration'] for step in plan['steps'])
        plan['confidence'] = 0.95 if len(gaps) == 0 else 0.75
        
        self._add_reasoning_step(
            'generate_execution_plan',
            'Create step-by-step execution plan',
            {'gaps_count': len(gaps), 'task_type': task_context.task_type},
            plan,
            plan['confidence']
        )
        
        return plan
    
    def _is_data_available(self, item: str, available_data: Dict[str, Any]) -> bool:
        """Check if a specific data item is available"""
        # Simple implementation - in reality this would be more sophisticated
        for category_data in available_data.values():
            if isinstance(category_data, dict) and item in category_data:
                return True
            elif isinstance(category_data, list):
                for list_item in category_data:
                    if isinstance(list_item, dict) and item in list_item:
                        return True
        return False
    
    def _get_priority(self, category: str, item: str) -> str:
        """Get priority level for missing data"""
        high_priority = ['id_number', 'tax_number', 'salary', 'vat_number']
        if item in high_priority:
            return 'high'
        elif category in ['personal_info', 'business_info']:
            return 'medium'
        else:
            return 'low'
    
    def _suggest_action(self, category: str, item: str) -> str:
        """Suggest how to collect missing data"""
        if 'document' in category.lower():
            return f'upload_{item}'
        elif item in ['salary', 'income', 'vat_number']:
            return f'input_{item}'
        else:
            return f'provide_{item}'
    
    def _add_reasoning_step(self, step_type: str, description: str, inputs: Dict[str, Any], 
                          outputs: Dict[str, Any], confidence: float):
        """Add a step to the reasoning history"""
        step = ReasoningStep(
            step_id=f"{step_type}_{len(self.reasoning_history)}",
            step_type=step_type,
            description=description,
            inputs=inputs,
            outputs=outputs,
            confidence=confidence,
            timestamp=datetime.now()
        )
        self.reasoning_history.append(asdict(step))

class AITaxAgent:
    """Main AI Tax Agent orchestrator"""
    
    def __init__(self):
        self.reasoning_loop = PreExecutionReasoningLoop()
        self.logger = logging.getLogger(__name__)
    
    def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task using the AI agent"""
        
        # Create task context
        task_context = TaskContext(
            task_id=task_data.get('task_id', f"task_{datetime.now().timestamp()}"),
            user_id=task_data.get('user_id', 'anonymous'),
            task_type=task_data.get('task_type', 'generic'),
            jurisdiction=task_data.get('jurisdiction', 'malta'),
            required_fields=task_data.get('required_fields', []),
            missing_fields=task_data.get('missing_fields', []),
            available_data=task_data.get('available_data', {}),
            execution_history=task_data.get('execution_history', []),
            status='processing',
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Execute reasoning loop
        reasoning_result = self.reasoning_loop.execute_reasoning_loop(task_context)
        
        # Return comprehensive response
        return {
            'task_id': task_context.task_id,
            'status': 'reasoning_complete',
            'reasoning_result': reasoning_result,
            'next_actions': self._determine_next_actions(reasoning_result),
            'user_message': self._generate_user_message(reasoning_result),
            'timestamp': datetime.now().isoformat()
        }
    
    def _determine_next_actions(self, reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Determine what actions the user needs to take"""
        actions = []
        
        gaps = reasoning_result.get('gaps', [])
        for gap in gaps:
            actions.append({
                'action_type': gap['suggested_action'],
                'description': f"Please provide {gap['item']}",
                'priority': gap['priority'],
                'category': gap['category']
            })
        
        return actions
    
    def _generate_user_message(self, reasoning_result: Dict[str, Any]) -> str:
        """Generate a user-friendly message about the reasoning result"""
        gaps = reasoning_result.get('gaps', [])
        
        if not gaps:
            return "I have all the information needed to complete your task. Let me proceed with the calculation."
        
        high_priority_gaps = [g for g in gaps if g['priority'] == 'high']
        
        if high_priority_gaps:
            items = [g['item'].replace('_', ' ').title() for g in high_priority_gaps]
            return f"To complete your tax calculation, I need the following essential information: {', '.join(items)}. Please provide these details."
        else:
            return f"I need {len(gaps)} additional pieces of information to complete your task. Let me guide you through providing them."

# Global agent instance
ai_agent = AITaxAgent()

