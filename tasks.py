"""
Task Management API Routes
Handles CRUD operations for tasks and task management
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

from ..models.task import Task, TaskStatus, TaskPriority, TaskType, TaskTemplate, TaskManager

# Initialize task manager (in production, this would use a database)
task_manager = TaskManager()

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'task_management',
        'timestamp': datetime.utcnow().isoformat()
    })

@tasks_bp.route('/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'task_type', 'user_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create task from template if specified
        if data.get('use_template'):
            template_type = data.get('template_type')
            user_id = data['user_id']
            
            if template_type == 'income_tax_return':
                task = TaskTemplate.create_income_tax_return(
                    user_id=user_id,
                    tax_year=data.get('tax_year')
                )
            elif template_type == 'vat_return':
                task = TaskTemplate.create_vat_return(
                    user_id=user_id,
                    quarter=data.get('quarter')
                )
            elif template_type == 'document_analysis':
                task = TaskTemplate.create_document_analysis(
                    user_id=user_id,
                    document_type=data.get('document_type', 'Unknown')
                )
            else:
                return jsonify({'error': f'Unknown template type: {template_type}'}), 400
        else:
            # Create custom task
            task = Task(
                title=data['title'],
                task_type=TaskType(data['task_type']),
                user_id=data['user_id'],
                description=data.get('description', ''),
                priority=TaskPriority(data.get('priority', 'medium')),
                due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None,
                metadata=data.get('metadata', {})
            )
        
        # Save task
        task_id = task_manager.create_task(task)
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'task': task.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({'error': f'Invalid data: {str(e)}'}), 400
    except Exception as e:
        logging.error(f"Error creating task: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@tasks_bp.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    """Get a specific task by ID"""
    try:
        task = task_manager.get_task(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        return jsonify({
            'success': True,
            'task': task.to_dict()
        })
        
    except Exception as e:
        logging.error(f"Error getting task {task_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@tasks_bp.route('/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """Update a task"""
    try:
        data = request.get_json()
        
        task = task_manager.get_task(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # Update task fields
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'priority' in data:
            task.priority = TaskPriority(data['priority'])
        if 'due_date' in data:
            task.due_date = datetime.fromisoformat(data['due_date']) if data['due_date'] else None
        if 'metadata' in data:
            task.metadata.update(data['metadata'])
        
        # Update status if provided
        if 'status' in data:
            new_status = TaskStatus(data['status'])
            notes = data.get('status_notes', '')
            task.update_status(new_status, notes)
        
        # Update progress if provided
        if 'progress' in data:
            task.update_progress(data['progress'])
        
        task.updated_at = datetime.utcnow()
        
        return jsonify({
            'success': True,
            'task': task.to_dict()
        })
        
    except ValueError as e:
        return jsonify({'error': f'Invalid data: {str(e)}'}), 400
    except Exception as e:
        logging.error(f"Error updating task {task_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@tasks_bp.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    try:
        success = task_manager.delete_task(task_id)
        if not success:
            return jsonify({'error': 'Task not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Task deleted successfully'
        })
        
    except Exception as e:
        logging.error(f"Error deleting task {task_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@tasks_bp.route('/users/<user_id>/tasks', methods=['GET'])
def get_user_tasks(user_id):
    """Get all tasks for a user"""
    try:
        status_filter = request.args.get('status')
        status = TaskStatus(status_filter) if status_filter else None
        
        tasks = task_manager.get_user_tasks(user_id, status)
        
        return jsonify({
            'success': True,
            'tasks': [task.to_dict() for task in tasks],
            'count': len(tasks)
        })
        
    except ValueError as e:
        return jsonify({'error': f'Invalid status filter: {str(e)}'}), 400
    except Exception as e:
        logging.error(f"Error getting tasks for user {user_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@tasks_bp.route('/users/<user_id>/tasks/overdue', methods=['GET'])
def get_overdue_tasks(user_id):
    """Get overdue tasks for a user"""
    try:
        overdue_tasks = task_manager.get_overdue_tasks(user_id)
        
        return jsonify({
            'success': True,
            'tasks': [task.to_dict() for task in overdue_tasks],
            'count': len(overdue_tasks)
        })
        
    except Exception as e:
        logging.error(f"Error getting overdue tasks for user {user_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@tasks_bp.route('/users/<user_id>/tasks/upcoming', methods=['GET'])
def get_upcoming_deadlines(user_id):
    """Get upcoming task deadlines for a user"""
    try:
        days_ahead = int(request.args.get('days', 30))
        upcoming_tasks = task_manager.get_upcoming_deadlines(user_id, days_ahead)
        
        return jsonify({
            'success': True,
            'tasks': [task.to_dict() for task in upcoming_tasks],
            'count': len(upcoming_tasks),
            'days_ahead': days_ahead
        })
        
    except ValueError as e:
        return jsonify({'error': f'Invalid days parameter: {str(e)}'}), 400
    except Exception as e:
        logging.error(f"Error getting upcoming tasks for user {user_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@tasks_bp.route('/tasks/<task_id>/documents', methods=['POST'])
def add_document_to_task(task_id):
    """Add a document reference to a task"""
    try:
        data = request.get_json()
        
        required_fields = ['document_id', 'document_type', 'filename']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        task = task_manager.get_task(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        task.add_document(
            document_id=data['document_id'],
            document_type=data['document_type'],
            filename=data['filename']
        )
        
        return jsonify({
            'success': True,
            'task': task.to_dict()
        })
        
    except Exception as e:
        logging.error(f"Error adding document to task {task_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@tasks_bp.route('/tasks/<task_id>/steps/<step_id>/complete', methods=['POST'])
def complete_task_step(task_id, step_id):
    """Mark a task step as completed"""
    try:
        data = request.get_json() or {}
        notes = data.get('notes', '')
        
        task = task_manager.get_task(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # Find and complete the step
        step_found = False
        for step in task.steps:
            if step.id == step_id:
                step.mark_completed(notes)
                step_found = True
                break
        
        if not step_found:
            return jsonify({'error': 'Step not found'}), 404
        
        # Update task progress based on completed steps
        total_steps = len(task.steps)
        completed_steps = sum(1 for step in task.steps if step.completed)
        
        if total_steps > 0:
            progress = int((completed_steps / total_steps) * 100)
            task.update_progress(progress)
        
        return jsonify({
            'success': True,
            'task': task.to_dict()
        })
        
    except Exception as e:
        logging.error(f"Error completing step {step_id} for task {task_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@tasks_bp.route('/tasks/<task_id>/ai-recommendation', methods=['POST'])
def add_ai_recommendation(task_id):
    """Add an AI recommendation to a task"""
    try:
        data = request.get_json()
        
        if 'recommendation' not in data:
            return jsonify({'error': 'Missing required field: recommendation'}), 400
        
        task = task_manager.get_task(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        task.add_ai_recommendation(
            recommendation=data['recommendation'],
            confidence=data.get('confidence', 0.0)
        )
        
        return jsonify({
            'success': True,
            'task': task.to_dict()
        })
        
    except Exception as e:
        logging.error(f"Error adding AI recommendation to task {task_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@tasks_bp.route('/templates', methods=['GET'])
def get_task_templates():
    """Get available task templates"""
    try:
        templates = [
            {
                'id': 'income_tax_return',
                'name': 'Income Tax Return',
                'description': 'Complete annual income tax return filing',
                'type': 'income_tax_return',
                'estimated_time': '2-4 hours',
                'required_documents': ['FS3', 'FS5', 'Bank statements', 'Expense receipts']
            },
            {
                'id': 'vat_return',
                'name': 'VAT Return',
                'description': 'Quarterly or monthly VAT return submission',
                'type': 'vat_return',
                'estimated_time': '1-2 hours',
                'required_documents': ['Sales invoices', 'Purchase invoices', 'VAT records']
            },
            {
                'id': 'document_analysis',
                'name': 'Document Analysis',
                'description': 'AI-powered analysis and data extraction from tax documents',
                'type': 'document_analysis',
                'estimated_time': '5-10 minutes',
                'required_documents': ['Document to analyze']
            }
        ]
        
        return jsonify({
            'success': True,
            'templates': templates
        })
        
    except Exception as e:
        logging.error(f"Error getting task templates: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@tasks_bp.route('/stats/<user_id>', methods=['GET'])
def get_task_stats(user_id):
    """Get task statistics for a user"""
    try:
        all_tasks = task_manager.get_user_tasks(user_id)
        
        stats = {
            'total_tasks': len(all_tasks),
            'completed_tasks': len([t for t in all_tasks if t.status == TaskStatus.COMPLETED]),
            'in_progress_tasks': len([t for t in all_tasks if t.status == TaskStatus.IN_PROGRESS]),
            'overdue_tasks': len([t for t in all_tasks if t.is_overdue()]),
            'upcoming_deadlines': len(task_manager.get_upcoming_deadlines(user_id, 7)),
            'avg_completion_time': None,  # Would calculate from completed tasks
            'task_types': {}
        }
        
        # Count tasks by type
        for task in all_tasks:
            task_type = task.task_type.value
            if task_type not in stats['task_types']:
                stats['task_types'][task_type] = 0
            stats['task_types'][task_type] += 1
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logging.error(f"Error getting task stats for user {user_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

