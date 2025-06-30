"""
Task Management Models for Malta Tax AI Agent
Handles task creation, tracking, and lifecycle management
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
import uuid
import json

class TaskStatus(Enum):
    DRAFT = "draft"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    WAITING_INFO = "waiting_info"
    REVIEW = "review"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TaskType(Enum):
    INCOME_TAX_RETURN = "income_tax_return"
    VAT_RETURN = "vat_return"
    CORPORATE_TAX = "corporate_tax"
    SOCIAL_SECURITY = "social_security"
    STAMP_DUTY = "stamp_duty"
    PROVISIONAL_TAX = "provisional_tax"
    TAX_CALCULATION = "tax_calculation"
    DOCUMENT_ANALYSIS = "document_analysis"
    COMPLIANCE_CHECK = "compliance_check"
    CUSTOM = "custom"

class Task:
    def __init__(self, 
                 title: str,
                 task_type: TaskType,
                 user_id: str,
                 description: str = "",
                 priority: TaskPriority = TaskPriority.MEDIUM,
                 due_date: Optional[datetime] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        
        self.id = str(uuid.uuid4())
        self.title = title
        self.task_type = task_type
        self.user_id = user_id
        self.description = description
        self.status = TaskStatus.DRAFT
        self.priority = priority
        self.progress = 0
        self.due_date = due_date
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.completed_at = None
        self.metadata = metadata or {}
        self.documents = []
        self.steps = []
        self.ai_recommendations = []
        self.compliance_status = None
        self.estimated_completion_time = None
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'task_type': self.task_type.value,
            'user_id': self.user_id,
            'description': self.description,
            'status': self.status.value,
            'priority': self.priority.value,
            'progress': self.progress,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'metadata': self.metadata,
            'documents': self.documents,
            'steps': [step.to_dict() for step in self.steps],
            'ai_recommendations': self.ai_recommendations,
            'compliance_status': self.compliance_status,
            'estimated_completion_time': self.estimated_completion_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create task from dictionary"""
        task = cls(
            title=data['title'],
            task_type=TaskType(data['task_type']),
            user_id=data['user_id'],
            description=data.get('description', ''),
            priority=TaskPriority(data.get('priority', 'medium')),
            due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None,
            metadata=data.get('metadata', {})
        )
        
        task.id = data['id']
        task.status = TaskStatus(data['status'])
        task.progress = data.get('progress', 0)
        task.created_at = datetime.fromisoformat(data['created_at'])
        task.updated_at = datetime.fromisoformat(data['updated_at'])
        task.completed_at = datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None
        task.documents = data.get('documents', [])
        task.steps = [TaskStep.from_dict(step_data) for step_data in data.get('steps', [])]
        task.ai_recommendations = data.get('ai_recommendations', [])
        task.compliance_status = data.get('compliance_status')
        task.estimated_completion_time = data.get('estimated_completion_time')
        
        return task
    
    def update_status(self, new_status: TaskStatus, notes: str = ""):
        """Update task status with timestamp and notes"""
        self.status = new_status
        self.updated_at = datetime.utcnow()
        
        if new_status == TaskStatus.COMPLETED:
            self.completed_at = datetime.utcnow()
            self.progress = 100
        
        # Add status change to metadata
        if 'status_history' not in self.metadata:
            self.metadata['status_history'] = []
        
        self.metadata['status_history'].append({
            'status': new_status.value,
            'timestamp': self.updated_at.isoformat(),
            'notes': notes
        })
    
    def update_progress(self, progress: int):
        """Update task progress (0-100)"""
        self.progress = max(0, min(100, progress))
        self.updated_at = datetime.utcnow()
        
        if self.progress == 100 and self.status != TaskStatus.COMPLETED:
            self.update_status(TaskStatus.COMPLETED, "Task automatically completed at 100% progress")
    
    def add_document(self, document_id: str, document_type: str, filename: str):
        """Add document reference to task"""
        document_ref = {
            'id': document_id,
            'type': document_type,
            'filename': filename,
            'added_at': datetime.utcnow().isoformat()
        }
        self.documents.append(document_ref)
        self.updated_at = datetime.utcnow()
    
    def add_step(self, step: 'TaskStep'):
        """Add a step to the task"""
        self.steps.append(step)
        self.updated_at = datetime.utcnow()
    
    def add_ai_recommendation(self, recommendation: str, confidence: float = 0.0):
        """Add AI recommendation to task"""
        rec = {
            'recommendation': recommendation,
            'confidence': confidence,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.ai_recommendations.append(rec)
        self.updated_at = datetime.utcnow()
    
    def is_overdue(self) -> bool:
        """Check if task is overdue"""
        if not self.due_date:
            return False
        return datetime.utcnow() > self.due_date and self.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]
    
    def days_until_due(self) -> Optional[int]:
        """Calculate days until due date"""
        if not self.due_date:
            return None
        delta = self.due_date - datetime.utcnow()
        return delta.days

class TaskStep:
    def __init__(self, 
                 title: str,
                 description: str = "",
                 required: bool = True,
                 order: int = 0):
        
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.required = required
        self.order = order
        self.completed = False
        self.completed_at = None
        self.notes = ""
        self.ai_assistance = None
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert step to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'required': self.required,
            'order': self.order,
            'completed': self.completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'notes': self.notes,
            'ai_assistance': self.ai_assistance
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskStep':
        """Create step from dictionary"""
        step = cls(
            title=data['title'],
            description=data.get('description', ''),
            required=data.get('required', True),
            order=data.get('order', 0)
        )
        
        step.id = data['id']
        step.completed = data.get('completed', False)
        step.completed_at = datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None
        step.notes = data.get('notes', '')
        step.ai_assistance = data.get('ai_assistance')
        
        return step
    
    def mark_completed(self, notes: str = ""):
        """Mark step as completed"""
        self.completed = True
        self.completed_at = datetime.utcnow()
        self.notes = notes

class TaskTemplate:
    """Template for creating common tax tasks"""
    
    @staticmethod
    def create_income_tax_return(user_id: str, tax_year: int = None) -> Task:
        """Create income tax return task template"""
        if not tax_year:
            tax_year = datetime.now().year - 1
            
        task = Task(
            title=f"Income Tax Return {tax_year}",
            task_type=TaskType.INCOME_TAX_RETURN,
            user_id=user_id,
            description=f"Complete and file income tax return for tax year {tax_year}",
            priority=TaskPriority.HIGH,
            due_date=datetime(tax_year + 1, 7, 31),  # Malta deadline: 31 July
            metadata={'tax_year': tax_year}
        )
        
        # Add standard steps
        steps = [
            TaskStep("Gather income documents", "Collect FS3, FS5, bank statements", True, 1),
            TaskStep("Review deductions", "Identify allowable deductions and expenses", True, 2),
            TaskStep("Calculate tax liability", "Compute income tax and social security", True, 3),
            TaskStep("Complete tax return", "Fill out official tax return form", True, 4),
            TaskStep("Submit to CFR", "File return with Commissioner for Revenue", True, 5)
        ]
        
        for step in steps:
            task.add_step(step)
        
        return task
    
    @staticmethod
    def create_vat_return(user_id: str, quarter: str = None) -> Task:
        """Create VAT return task template"""
        if not quarter:
            now = datetime.now()
            quarter = f"Q{(now.month-1)//3 + 1} {now.year}"
            
        task = Task(
            title=f"VAT Return {quarter}",
            task_type=TaskType.VAT_RETURN,
            user_id=user_id,
            description=f"Complete and submit VAT return for {quarter}",
            priority=TaskPriority.MEDIUM,
            due_date=datetime.now() + timedelta(days=15),  # 15th of following month
            metadata={'quarter': quarter}
        )
        
        steps = [
            TaskStep("Collect sales records", "Gather all sales invoices and receipts", True, 1),
            TaskStep("Collect purchase records", "Gather all purchase invoices", True, 2),
            TaskStep("Calculate VAT liability", "Compute VAT due or refund", True, 3),
            TaskStep("Complete VAT return", "Fill out VAT return form", True, 4),
            TaskStep("Submit return", "File VAT return online", True, 5)
        ]
        
        for step in steps:
            task.add_step(step)
        
        return task
    
    @staticmethod
    def create_document_analysis(user_id: str, document_type: str) -> Task:
        """Create document analysis task"""
        task = Task(
            title=f"Analyze {document_type}",
            task_type=TaskType.DOCUMENT_ANALYSIS,
            user_id=user_id,
            description=f"AI analysis and data extraction from {document_type}",
            priority=TaskPriority.MEDIUM,
            metadata={'document_type': document_type}
        )
        
        steps = [
            TaskStep("Upload document", "Upload document for analysis", True, 1),
            TaskStep("AI processing", "Automated document analysis and data extraction", True, 2),
            TaskStep("Review results", "Review and verify extracted data", True, 3),
            TaskStep("Apply to tax calculation", "Use extracted data in tax calculations", False, 4)
        ]
        
        for step in steps:
            task.add_step(step)
        
        return task

class TaskManager:
    """Task management service"""
    
    def __init__(self):
        self.tasks = {}  # In production, this would be a database
    
    def create_task(self, task: Task) -> str:
        """Create a new task"""
        self.tasks[task.id] = task
        return task.id
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        return self.tasks.get(task_id)
    
    def get_user_tasks(self, user_id: str, status: Optional[TaskStatus] = None) -> List[Task]:
        """Get all tasks for a user, optionally filtered by status"""
        user_tasks = [task for task in self.tasks.values() if task.user_id == user_id]
        
        if status:
            user_tasks = [task for task in user_tasks if task.status == status]
        
        return sorted(user_tasks, key=lambda t: t.created_at, reverse=True)
    
    def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """Update task with new data"""
        task = self.get_task(task_id)
        if not task:
            return False
        
        for key, value in updates.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        task.updated_at = datetime.utcnow()
        return True
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            return True
        return False
    
    def get_overdue_tasks(self, user_id: Optional[str] = None) -> List[Task]:
        """Get all overdue tasks, optionally for a specific user"""
        overdue = [task for task in self.tasks.values() if task.is_overdue()]
        
        if user_id:
            overdue = [task for task in overdue if task.user_id == user_id]
        
        return overdue
    
    def get_upcoming_deadlines(self, user_id: str, days_ahead: int = 30) -> List[Task]:
        """Get tasks with deadlines in the next N days"""
        upcoming = []
        cutoff_date = datetime.utcnow() + timedelta(days=days_ahead)
        
        for task in self.tasks.values():
            if (task.user_id == user_id and 
                task.due_date and 
                task.due_date <= cutoff_date and 
                task.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]):
                upcoming.append(task)
        
        return sorted(upcoming, key=lambda t: t.due_date)

