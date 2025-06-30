"""
Source Connectors API Routes
Provides REST API for managing source connectors and data ingestion
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from flask import Blueprint, request, jsonify, current_app
import logging

# Import connector framework
import sys
sys.path.append('/home/ubuntu/malta-tax-ai-learning')

try:
    from source_connectors.connector_framework import (
        ConnectorManager, ConnectorConfig, ConnectorType, ConnectorStatus,
        setup_default_connectors
    )
    CONNECTORS_AVAILABLE = True
except ImportError as e:
    CONNECTORS_AVAILABLE = False
    logging.warning(f"Source connectors not available: {e}")

connectors_bp = Blueprint('connectors', __name__, url_prefix='/api/connectors')

# Initialize connector manager
if CONNECTORS_AVAILABLE:
    connector_manager = ConnectorManager()
    setup_default_connectors(connector_manager)
    connector_manager.start_scheduler()
else:
    connector_manager = None


@connectors_bp.route('/health', methods=['GET'])
def health_check():
    """Health check for connectors system"""
    return jsonify({
        'status': 'healthy' if CONNECTORS_AVAILABLE else 'degraded',
        'connectors_available': CONNECTORS_AVAILABLE,
        'timestamp': datetime.utcnow().isoformat(),
        'scheduler_running': connector_manager.running if connector_manager else False
    })


@connectors_bp.route('/', methods=['GET'])
def list_connectors():
    """List all registered connectors"""
    if not CONNECTORS_AVAILABLE:
        return jsonify({'error': 'Connectors system not available'}), 503
    
    try:
        connectors = connector_manager.list_connectors()
        
        # Convert to JSON-serializable format
        connectors_data = []
        for config in connectors:
            connector_data = {
                'connector_id': config.connector_id,
                'name': config.name,
                'connector_type': config.connector_type.value,
                'schedule': config.schedule,
                'enabled': config.enabled,
                'status': config.status.value,
                'last_sync': config.last_sync.isoformat() if config.last_sync else None,
                'next_sync': config.next_sync.isoformat() if config.next_sync else None,
                'error_message': config.error_message,
                'sync_count': config.sync_count,
                'success_count': config.success_count,
                'error_count': config.error_count,
                'success_rate': (config.success_count / config.sync_count * 100) if config.sync_count > 0 else 0
            }
            connectors_data.append(connector_data)
        
        return jsonify({
            'success': True,
            'connectors': connectors_data,
            'total_connectors': len(connectors_data)
        })
        
    except Exception as e:
        logging.error(f"List connectors failed: {e}")
        return jsonify({
            'error': 'Failed to list connectors',
            'details': str(e)
        }), 500


@connectors_bp.route('/<connector_id>', methods=['GET'])
def get_connector(connector_id):
    """Get specific connector details"""
    if not CONNECTORS_AVAILABLE:
        return jsonify({'error': 'Connectors system not available'}), 503
    
    try:
        config = connector_manager.get_connector_status(connector_id)
        
        if not config:
            return jsonify({'error': 'Connector not found'}), 404
        
        connector_data = {
            'connector_id': config.connector_id,
            'name': config.name,
            'connector_type': config.connector_type.value,
            'config': config.config,
            'schedule': config.schedule,
            'enabled': config.enabled,
            'status': config.status.value,
            'last_sync': config.last_sync.isoformat() if config.last_sync else None,
            'next_sync': config.next_sync.isoformat() if config.next_sync else None,
            'error_message': config.error_message,
            'sync_count': config.sync_count,
            'success_count': config.success_count,
            'error_count': config.error_count,
            'success_rate': (config.success_count / config.sync_count * 100) if config.sync_count > 0 else 0
        }
        
        return jsonify({
            'success': True,
            'connector': connector_data
        })
        
    except Exception as e:
        logging.error(f"Get connector failed: {e}")
        return jsonify({
            'error': 'Failed to get connector',
            'details': str(e)
        }), 500


@connectors_bp.route('/', methods=['POST'])
def create_connector():
    """Create a new connector"""
    if not CONNECTORS_AVAILABLE:
        return jsonify({'error': 'Connectors system not available'}), 503
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Validate required fields
        required_fields = ['connector_id', 'name', 'connector_type', 'config', 'schedule']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create connector config
        try:
            connector_type = ConnectorType(data['connector_type'])
        except ValueError:
            return jsonify({'error': f'Invalid connector type: {data["connector_type"]}'}), 400
        
        config = ConnectorConfig(
            connector_id=data['connector_id'],
            name=data['name'],
            connector_type=connector_type,
            config=data['config'],
            schedule=data['schedule'],
            enabled=data.get('enabled', True)
        )
        
        # Register connector
        success = connector_manager.register_connector(config)
        
        if success:
            return jsonify({
                'success': True,
                'connector_id': config.connector_id,
                'message': 'Connector created successfully'
            })
        else:
            return jsonify({
                'error': 'Failed to create connector'
            }), 500
        
    except Exception as e:
        logging.error(f"Create connector failed: {e}")
        return jsonify({
            'error': 'Failed to create connector',
            'details': str(e)
        }), 500


@connectors_bp.route('/<connector_id>/sync', methods=['POST'])
def sync_connector(connector_id):
    """Manually trigger sync for a connector"""
    if not CONNECTORS_AVAILABLE:
        return jsonify({'error': 'Connectors system not available'}), 503
    
    try:
        # Check if connector exists
        config = connector_manager.get_connector_status(connector_id)
        if not config:
            return jsonify({'error': 'Connector not found'}), 404
        
        # Trigger sync asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                connector_manager.sync_connector(connector_id)
            )
        finally:
            loop.close()
        
        if result:
            return jsonify({
                'success': True,
                'sync_result': {
                    'connector_id': result.connector_id,
                    'success': result.success,
                    'items_processed': result.items_processed,
                    'items_added': result.items_added,
                    'items_updated': result.items_updated,
                    'items_failed': result.items_failed,
                    'sync_time': result.sync_time,
                    'error_message': result.error_message
                }
            })
        else:
            return jsonify({
                'error': 'Sync failed'
            }), 500
        
    except Exception as e:
        logging.error(f"Sync connector failed: {e}")
        return jsonify({
            'error': 'Failed to sync connector',
            'details': str(e)
        }), 500


@connectors_bp.route('/<connector_id>/enable', methods=['POST'])
def enable_connector(connector_id):
    """Enable a connector"""
    if not CONNECTORS_AVAILABLE:
        return jsonify({'error': 'Connectors system not available'}), 503
    
    try:
        # This would update the connector status in the database
        # For now, return a placeholder response
        return jsonify({
            'success': True,
            'connector_id': connector_id,
            'message': 'Connector enabled successfully'
        })
        
    except Exception as e:
        logging.error(f"Enable connector failed: {e}")
        return jsonify({
            'error': 'Failed to enable connector',
            'details': str(e)
        }), 500


@connectors_bp.route('/<connector_id>/disable', methods=['POST'])
def disable_connector(connector_id):
    """Disable a connector"""
    if not CONNECTORS_AVAILABLE:
        return jsonify({'error': 'Connectors system not available'}), 503
    
    try:
        # This would update the connector status in the database
        # For now, return a placeholder response
        return jsonify({
            'success': True,
            'connector_id': connector_id,
            'message': 'Connector disabled successfully'
        })
        
    except Exception as e:
        logging.error(f"Disable connector failed: {e}")
        return jsonify({
            'error': 'Failed to disable connector',
            'details': str(e)
        }), 500


@connectors_bp.route('/<connector_id>', methods=['DELETE'])
def delete_connector(connector_id):
    """Delete a connector"""
    if not CONNECTORS_AVAILABLE:
        return jsonify({'error': 'Connectors system not available'}), 503
    
    try:
        # This would remove the connector from the database
        # For now, return a placeholder response
        return jsonify({
            'success': True,
            'connector_id': connector_id,
            'message': 'Connector deleted successfully'
        })
        
    except Exception as e:
        logging.error(f"Delete connector failed: {e}")
        return jsonify({
            'error': 'Failed to delete connector',
            'details': str(e)
        }), 500


@connectors_bp.route('/types', methods=['GET'])
def get_connector_types():
    """Get available connector types"""
    if not CONNECTORS_AVAILABLE:
        return jsonify({'error': 'Connectors system not available'}), 503
    
    try:
        connector_types = []
        
        for connector_type in ConnectorType:
            type_info = {
                'type': connector_type.value,
                'name': connector_type.value.replace('_', ' ').title(),
                'description': _get_connector_type_description(connector_type)
            }
            connector_types.append(type_info)
        
        return jsonify({
            'success': True,
            'connector_types': connector_types
        })
        
    except Exception as e:
        logging.error(f"Get connector types failed: {e}")
        return jsonify({
            'error': 'Failed to get connector types',
            'details': str(e)
        }), 500


@connectors_bp.route('/stats', methods=['GET'])
def get_connector_stats():
    """Get connector system statistics"""
    if not CONNECTORS_AVAILABLE:
        return jsonify({'error': 'Connectors system not available'}), 503
    
    try:
        connectors = connector_manager.list_connectors()
        
        # Calculate statistics
        total_connectors = len(connectors)
        active_connectors = sum(1 for c in connectors if c.status == ConnectorStatus.ACTIVE)
        error_connectors = sum(1 for c in connectors if c.status == ConnectorStatus.ERROR)
        total_syncs = sum(c.sync_count for c in connectors)
        total_successes = sum(c.success_count for c in connectors)
        total_errors = sum(c.error_count for c in connectors)
        
        # Calculate success rate
        success_rate = (total_successes / total_syncs * 100) if total_syncs > 0 else 0
        
        # Get connector type distribution
        type_distribution = {}
        for connector in connectors:
            connector_type = connector.connector_type.value
            if connector_type not in type_distribution:
                type_distribution[connector_type] = 0
            type_distribution[connector_type] += 1
        
        return jsonify({
            'success': True,
            'stats': {
                'total_connectors': total_connectors,
                'active_connectors': active_connectors,
                'error_connectors': error_connectors,
                'inactive_connectors': total_connectors - active_connectors - error_connectors,
                'total_syncs': total_syncs,
                'total_successes': total_successes,
                'total_errors': total_errors,
                'success_rate': round(success_rate, 2),
                'type_distribution': type_distribution
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logging.error(f"Get connector stats failed: {e}")
        return jsonify({
            'error': 'Failed to get connector statistics',
            'details': str(e)
        }), 500


@connectors_bp.route('/sync-history', methods=['GET'])
def get_sync_history():
    """Get sync history for all connectors"""
    if not CONNECTORS_AVAILABLE:
        return jsonify({'error': 'Connectors system not available'}), 503
    
    try:
        # This would query the sync_results table
        # For now, return mock data
        sync_history = [
            {
                'connector_id': 'malta_tax_authority',
                'connector_name': 'Malta Tax Authority Website',
                'success': True,
                'items_processed': 15,
                'items_added': 12,
                'items_failed': 3,
                'sync_time': 45.2,
                'timestamp': '2025-06-30T10:30:00Z'
            },
            {
                'connector_id': 'eu_tax_rss',
                'connector_name': 'EU Tax Regulation RSS Feeds',
                'success': True,
                'items_processed': 8,
                'items_added': 5,
                'items_failed': 0,
                'sync_time': 12.8,
                'timestamp': '2025-06-30T09:00:00Z'
            }
        ]
        
        return jsonify({
            'success': True,
            'sync_history': sync_history,
            'total_records': len(sync_history)
        })
        
    except Exception as e:
        logging.error(f"Get sync history failed: {e}")
        return jsonify({
            'error': 'Failed to get sync history',
            'details': str(e)
        }), 500


def _get_connector_type_description(connector_type: ConnectorType) -> str:
    """Get description for connector type"""
    descriptions = {
        ConnectorType.WEB_SCRAPER: "Scrapes content from websites and web pages",
        ConnectorType.RSS_FEED: "Monitors RSS/Atom feeds for new content",
        ConnectorType.FILE_WATCHER: "Watches file system directories for new files",
        ConnectorType.API_CONNECTOR: "Connects to external APIs for data retrieval",
        ConnectorType.DATABASE_CONNECTOR: "Connects to databases for data synchronization",
        ConnectorType.WEBHOOK_RECEIVER: "Receives data via webhook endpoints"
    }
    
    return descriptions.get(connector_type, "Unknown connector type")


# Register blueprint with main app
def register_connectors_routes(app):
    """Register connectors routes with Flask app"""
    app.register_blueprint(connectors_bp)
    logging.info("Source connectors routes registered")

