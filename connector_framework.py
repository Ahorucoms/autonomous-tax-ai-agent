"""
Source Connectors Framework for Malta Tax AI Learning System
Provides pluggable architecture for automated data ingestion from various sources
"""

import os
import json
import asyncio
import logging
import hashlib
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import requests
import feedparser
import schedule
import time
from pathlib import Path
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import document processor
import sys
sys.path.append('/home/ubuntu/malta-tax-ai-learning')
from document_processor.processor import DocumentProcessor, DocumentType, ProcessingResult


class ConnectorType(Enum):
    """Types of source connectors"""
    WEB_SCRAPER = "web_scraper"
    RSS_FEED = "rss_feed"
    FILE_WATCHER = "file_watcher"
    API_CONNECTOR = "api_connector"
    DATABASE_CONNECTOR = "database_connector"
    WEBHOOK_RECEIVER = "webhook_receiver"


class ConnectorStatus(Enum):
    """Connector status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    SYNCING = "syncing"


@dataclass
class ConnectorConfig:
    """Configuration for a source connector"""
    connector_id: str
    name: str
    connector_type: ConnectorType
    config: Dict[str, Any]
    schedule: str  # Cron-like schedule
    enabled: bool = True
    last_sync: Optional[datetime] = None
    next_sync: Optional[datetime] = None
    status: ConnectorStatus = ConnectorStatus.INACTIVE
    error_message: Optional[str] = None
    sync_count: int = 0
    success_count: int = 0
    error_count: int = 0


@dataclass
class SyncResult:
    """Result of a connector sync operation"""
    connector_id: str
    success: bool
    items_processed: int
    items_added: int
    items_updated: int
    items_failed: int
    sync_time: float
    error_message: Optional[str] = None
    details: Dict[str, Any] = None


class BaseConnector(ABC):
    """Base class for all source connectors"""
    
    def __init__(self, config: ConnectorConfig):
        """
        Initialize connector with configuration
        
        Args:
            config: Connector configuration
        """
        self.config = config
        self.logger = logging.getLogger(f"connector.{config.connector_id}")
        self.document_processor = DocumentProcessor()
        
    @abstractmethod
    async def sync(self) -> SyncResult:
        """
        Perform sync operation to fetch and process data
        
        Returns:
            Sync result with statistics
        """
        pass
    
    @abstractmethod
    def validate_config(self) -> Tuple[bool, Optional[str]]:
        """
        Validate connector configuration
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        pass
    
    def generate_item_id(self, content: str) -> str:
        """Generate unique ID for content item"""
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    async def process_document(self, content: bytes, filename: str, 
                             document_type: Optional[DocumentType] = None) -> Optional[ProcessingResult]:
        """Process document content"""
        try:
            result = await self.document_processor.process_document(
                file_data=content,
                filename=filename,
                document_type=document_type
            )
            return result
        except Exception as e:
            self.logger.error(f"Document processing failed: {e}")
            return None


class MaltaTaxAuthorityConnector(BaseConnector):
    """Connector for Malta Tax Authority website"""
    
    def __init__(self, config: ConnectorConfig):
        super().__init__(config)
        self.base_url = config.config.get('base_url', 'https://cfr.gov.mt')
        self.sections = config.config.get('sections', ['tax-legislation', 'forms', 'guidance'])
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Malta Tax AI Learning Bot 1.0'
        })
    
    def validate_config(self) -> Tuple[bool, Optional[str]]:
        """Validate configuration"""
        required_fields = ['base_url']
        for field in required_fields:
            if field not in self.config.config:
                return False, f"Missing required field: {field}"
        return True, None
    
    async def sync(self) -> SyncResult:
        """Sync Malta Tax Authority content"""
        start_time = time.time()
        items_processed = 0
        items_added = 0
        items_failed = 0
        
        try:
            self.logger.info(f"Starting sync for Malta Tax Authority connector")
            
            for section in self.sections:
                try:
                    # Fetch section content
                    section_url = f"{self.base_url}/{section}"
                    response = self.session.get(section_url, timeout=30)
                    response.raise_for_status()
                    
                    # Parse content (simplified - would need proper HTML parsing)
                    content = response.text
                    items_processed += 1
                    
                    # Process as document
                    result = await self.process_document(
                        content=content.encode('utf-8'),
                        filename=f"malta_tax_{section}.html",
                        document_type=DocumentType.REGULATION
                    )
                    
                    if result and result.status.value == 'completed':
                        items_added += 1
                        self.logger.info(f"Successfully processed {section}")
                    else:
                        items_failed += 1
                        self.logger.warning(f"Failed to process {section}")
                        
                except Exception as e:
                    items_failed += 1
                    self.logger.error(f"Error processing section {section}: {e}")
            
            sync_time = time.time() - start_time
            
            return SyncResult(
                connector_id=self.config.connector_id,
                success=items_failed == 0,
                items_processed=items_processed,
                items_added=items_added,
                items_updated=0,
                items_failed=items_failed,
                sync_time=sync_time
            )
            
        except Exception as e:
            sync_time = time.time() - start_time
            self.logger.error(f"Malta Tax Authority sync failed: {e}")
            
            return SyncResult(
                connector_id=self.config.connector_id,
                success=False,
                items_processed=items_processed,
                items_added=items_added,
                items_updated=0,
                items_failed=items_failed,
                sync_time=sync_time,
                error_message=str(e)
            )


class EUTaxRegulationRSSConnector(BaseConnector):
    """Connector for EU tax regulation RSS feeds"""
    
    def __init__(self, config: ConnectorConfig):
        super().__init__(config)
        self.feed_urls = config.config.get('feed_urls', [
            'https://ec.europa.eu/taxation_customs/rss/all_en.xml',
            'https://eur-lex.europa.eu/rss/latest-tax.xml'
        ])
        self.max_items = config.config.get('max_items', 50)
    
    def validate_config(self) -> Tuple[bool, Optional[str]]:
        """Validate configuration"""
        if not self.feed_urls:
            return False, "No feed URLs configured"
        return True, None
    
    async def sync(self) -> SyncResult:
        """Sync EU tax regulation RSS feeds"""
        start_time = time.time()
        items_processed = 0
        items_added = 0
        items_failed = 0
        
        try:
            self.logger.info(f"Starting sync for EU Tax Regulation RSS connector")
            
            for feed_url in self.feed_urls:
                try:
                    # Parse RSS feed
                    feed = feedparser.parse(feed_url)
                    
                    for entry in feed.entries[:self.max_items]:
                        try:
                            items_processed += 1
                            
                            # Create content from RSS entry
                            content = f"""
                            Title: {entry.title}
                            Link: {entry.link}
                            Published: {entry.published if hasattr(entry, 'published') else 'Unknown'}
                            Summary: {entry.summary if hasattr(entry, 'summary') else 'No summary'}
                            """
                            
                            # Process as regulation document
                            result = await self.process_document(
                                content=content.encode('utf-8'),
                                filename=f"eu_tax_rss_{self.generate_item_id(entry.link)}.txt",
                                document_type=DocumentType.REGULATION
                            )
                            
                            if result and result.status.value == 'completed':
                                items_added += 1
                                self.logger.debug(f"Successfully processed RSS item: {entry.title}")
                            else:
                                items_failed += 1
                                
                        except Exception as e:
                            items_failed += 1
                            self.logger.error(f"Error processing RSS entry: {e}")
                            
                except Exception as e:
                    self.logger.error(f"Error parsing RSS feed {feed_url}: {e}")
            
            sync_time = time.time() - start_time
            
            return SyncResult(
                connector_id=self.config.connector_id,
                success=items_failed < items_processed * 0.5,  # Allow 50% failure rate
                items_processed=items_processed,
                items_added=items_added,
                items_updated=0,
                items_failed=items_failed,
                sync_time=sync_time
            )
            
        except Exception as e:
            sync_time = time.time() - start_time
            self.logger.error(f"EU Tax Regulation RSS sync failed: {e}")
            
            return SyncResult(
                connector_id=self.config.connector_id,
                success=False,
                items_processed=items_processed,
                items_added=items_added,
                items_updated=0,
                items_failed=items_failed,
                sync_time=sync_time,
                error_message=str(e)
            )


class FileWatcherConnector(BaseConnector):
    """Connector for watching file system directories"""
    
    def __init__(self, config: ConnectorConfig):
        super().__init__(config)
        self.watch_directories = config.config.get('watch_directories', [])
        self.file_patterns = config.config.get('file_patterns', ['*.pdf', '*.docx', '*.txt'])
        self.processed_files = set()
        
    def validate_config(self) -> Tuple[bool, Optional[str]]:
        """Validate configuration"""
        if not self.watch_directories:
            return False, "No watch directories configured"
        
        for directory in self.watch_directories:
            if not os.path.exists(directory):
                return False, f"Watch directory does not exist: {directory}"
                
        return True, None
    
    async def sync(self) -> SyncResult:
        """Sync files from watched directories"""
        start_time = time.time()
        items_processed = 0
        items_added = 0
        items_failed = 0
        
        try:
            self.logger.info(f"Starting sync for File Watcher connector")
            
            for watch_dir in self.watch_directories:
                watch_path = Path(watch_dir)
                
                # Find new files
                for pattern in self.file_patterns:
                    for file_path in watch_path.glob(pattern):
                        if file_path.is_file() and str(file_path) not in self.processed_files:
                            try:
                                items_processed += 1
                                
                                # Read file content
                                with open(file_path, 'rb') as f:
                                    content = f.read()
                                
                                # Determine document type from filename
                                document_type = self._detect_document_type(file_path.name)
                                
                                # Process document
                                result = await self.process_document(
                                    content=content,
                                    filename=file_path.name,
                                    document_type=document_type
                                )
                                
                                if result and result.status.value == 'completed':
                                    items_added += 1
                                    self.processed_files.add(str(file_path))
                                    self.logger.info(f"Successfully processed file: {file_path.name}")
                                else:
                                    items_failed += 1
                                    
                            except Exception as e:
                                items_failed += 1
                                self.logger.error(f"Error processing file {file_path}: {e}")
            
            sync_time = time.time() - start_time
            
            return SyncResult(
                connector_id=self.config.connector_id,
                success=True,
                items_processed=items_processed,
                items_added=items_added,
                items_updated=0,
                items_failed=items_failed,
                sync_time=sync_time
            )
            
        except Exception as e:
            sync_time = time.time() - start_time
            self.logger.error(f"File Watcher sync failed: {e}")
            
            return SyncResult(
                connector_id=self.config.connector_id,
                success=False,
                items_processed=items_processed,
                items_added=items_added,
                items_updated=0,
                items_failed=items_failed,
                sync_time=sync_time,
                error_message=str(e)
            )
    
    def _detect_document_type(self, filename: str) -> DocumentType:
        """Detect document type from filename"""
        filename_lower = filename.lower()
        
        if 'fs3' in filename_lower:
            return DocumentType.FS3
        elif 'fs5' in filename_lower:
            return DocumentType.FS5
        elif 'vat' in filename_lower:
            return DocumentType.VAT_RETURN
        elif 'payslip' in filename_lower:
            return DocumentType.PAYSLIP
        elif 'invoice' in filename_lower:
            return DocumentType.INVOICE
        else:
            return DocumentType.UNKNOWN


class ConnectorManager:
    """Manages all source connectors and their scheduling"""
    
    def __init__(self, db_path: str = "/tmp/connectors.db"):
        """
        Initialize connector manager
        
        Args:
            db_path: Path to SQLite database for storing connector state
        """
        self.db_path = db_path
        self.connectors: Dict[str, BaseConnector] = {}
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.running = False
        self.scheduler_thread = None
        self.logger = logging.getLogger(__name__)
        
        # Initialize database
        self._init_database()
        
        # Register connector types
        self.connector_classes = {
            ConnectorType.WEB_SCRAPER: MaltaTaxAuthorityConnector,
            ConnectorType.RSS_FEED: EUTaxRegulationRSSConnector,
            ConnectorType.FILE_WATCHER: FileWatcherConnector,
        }
    
    def _init_database(self):
        """Initialize SQLite database for connector state"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS connectors (
                    connector_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    connector_type TEXT NOT NULL,
                    config TEXT NOT NULL,
                    schedule TEXT NOT NULL,
                    enabled BOOLEAN DEFAULT 1,
                    last_sync TIMESTAMP,
                    next_sync TIMESTAMP,
                    status TEXT DEFAULT 'inactive',
                    error_message TEXT,
                    sync_count INTEGER DEFAULT 0,
                    success_count INTEGER DEFAULT 0,
                    error_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sync_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    connector_id TEXT NOT NULL,
                    success BOOLEAN NOT NULL,
                    items_processed INTEGER DEFAULT 0,
                    items_added INTEGER DEFAULT 0,
                    items_updated INTEGER DEFAULT 0,
                    items_failed INTEGER DEFAULT 0,
                    sync_time REAL DEFAULT 0,
                    error_message TEXT,
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (connector_id) REFERENCES connectors (connector_id)
                )
            """)
    
    def register_connector(self, config: ConnectorConfig) -> bool:
        """
        Register a new connector
        
        Args:
            config: Connector configuration
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate connector type
            if config.connector_type not in self.connector_classes:
                self.logger.error(f"Unknown connector type: {config.connector_type}")
                return False
            
            # Create connector instance
            connector_class = self.connector_classes[config.connector_type]
            connector = connector_class(config)
            
            # Validate configuration
            is_valid, error_msg = connector.validate_config()
            if not is_valid:
                self.logger.error(f"Invalid connector config: {error_msg}")
                return False
            
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO connectors 
                    (connector_id, name, connector_type, config, schedule, enabled)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    config.connector_id,
                    config.name,
                    config.connector_type.value,
                    json.dumps(config.config),
                    config.schedule,
                    config.enabled
                ))
            
            # Add to active connectors
            self.connectors[config.connector_id] = connector
            
            self.logger.info(f"Registered connector: {config.connector_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register connector: {e}")
            return False
    
    def get_connector_status(self, connector_id: str) -> Optional[ConnectorConfig]:
        """Get connector status"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT * FROM connectors WHERE connector_id = ?",
                    (connector_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    return ConnectorConfig(
                        connector_id=row['connector_id'],
                        name=row['name'],
                        connector_type=ConnectorType(row['connector_type']),
                        config=json.loads(row['config']),
                        schedule=row['schedule'],
                        enabled=bool(row['enabled']),
                        last_sync=datetime.fromisoformat(row['last_sync']) if row['last_sync'] else None,
                        next_sync=datetime.fromisoformat(row['next_sync']) if row['next_sync'] else None,
                        status=ConnectorStatus(row['status']),
                        error_message=row['error_message'],
                        sync_count=row['sync_count'],
                        success_count=row['success_count'],
                        error_count=row['error_count']
                    )
                    
        except Exception as e:
            self.logger.error(f"Failed to get connector status: {e}")
            
        return None
    
    def list_connectors(self) -> List[ConnectorConfig]:
        """List all registered connectors"""
        connectors = []
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT * FROM connectors ORDER BY name")
                
                for row in cursor.fetchall():
                    config = ConnectorConfig(
                        connector_id=row['connector_id'],
                        name=row['name'],
                        connector_type=ConnectorType(row['connector_type']),
                        config=json.loads(row['config']),
                        schedule=row['schedule'],
                        enabled=bool(row['enabled']),
                        last_sync=datetime.fromisoformat(row['last_sync']) if row['last_sync'] else None,
                        next_sync=datetime.fromisoformat(row['next_sync']) if row['next_sync'] else None,
                        status=ConnectorStatus(row['status']),
                        error_message=row['error_message'],
                        sync_count=row['sync_count'],
                        success_count=row['success_count'],
                        error_count=row['error_count']
                    )
                    connectors.append(config)
                    
        except Exception as e:
            self.logger.error(f"Failed to list connectors: {e}")
            
        return connectors
    
    async def sync_connector(self, connector_id: str) -> Optional[SyncResult]:
        """
        Manually trigger sync for a specific connector
        
        Args:
            connector_id: ID of connector to sync
            
        Returns:
            Sync result or None if failed
        """
        if connector_id not in self.connectors:
            self.logger.error(f"Connector not found: {connector_id}")
            return None
        
        try:
            # Update status to syncing
            self._update_connector_status(connector_id, ConnectorStatus.SYNCING)
            
            # Perform sync
            connector = self.connectors[connector_id]
            result = await connector.sync()
            
            # Update database with result
            self._store_sync_result(result)
            
            # Update connector status
            status = ConnectorStatus.ACTIVE if result.success else ConnectorStatus.ERROR
            self._update_connector_status(
                connector_id, 
                status, 
                error_message=result.error_message if not result.success else None
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Sync failed for connector {connector_id}: {e}")
            self._update_connector_status(connector_id, ConnectorStatus.ERROR, str(e))
            return None
    
    def _update_connector_status(self, connector_id: str, status: ConnectorStatus, 
                               error_message: Optional[str] = None):
        """Update connector status in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                if status == ConnectorStatus.SYNCING:
                    conn.execute("""
                        UPDATE connectors 
                        SET status = ?, sync_count = sync_count + 1, updated_at = CURRENT_TIMESTAMP
                        WHERE connector_id = ?
                    """, (status.value, connector_id))
                elif status == ConnectorStatus.ACTIVE:
                    conn.execute("""
                        UPDATE connectors 
                        SET status = ?, last_sync = CURRENT_TIMESTAMP, 
                            success_count = success_count + 1, error_message = NULL,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE connector_id = ?
                    """, (status.value, connector_id))
                elif status == ConnectorStatus.ERROR:
                    conn.execute("""
                        UPDATE connectors 
                        SET status = ?, error_message = ?, error_count = error_count + 1,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE connector_id = ?
                    """, (status.value, error_message, connector_id))
                    
        except Exception as e:
            self.logger.error(f"Failed to update connector status: {e}")
    
    def _store_sync_result(self, result: SyncResult):
        """Store sync result in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO sync_results 
                    (connector_id, success, items_processed, items_added, items_updated, 
                     items_failed, sync_time, error_message, details)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    result.connector_id,
                    result.success,
                    result.items_processed,
                    result.items_added,
                    result.items_updated,
                    result.items_failed,
                    result.sync_time,
                    result.error_message,
                    json.dumps(result.details) if result.details else None
                ))
                
        except Exception as e:
            self.logger.error(f"Failed to store sync result: {e}")
    
    def start_scheduler(self):
        """Start the connector scheduler"""
        if self.running:
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        self.logger.info("Connector scheduler started")
    
    def stop_scheduler(self):
        """Stop the connector scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        self.logger.info("Connector scheduler stopped")
    
    def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.running:
            try:
                # Check for connectors that need to run
                connectors = self.list_connectors()
                
                for config in connectors:
                    if config.enabled and self._should_run_connector(config):
                        # Run connector asynchronously
                        asyncio.create_task(self.sync_connector(config.connector_id))
                
                # Sleep for 60 seconds before next check
                time.sleep(60)
                
            except Exception as e:
                self.logger.error(f"Scheduler error: {e}")
                time.sleep(60)
    
    def _should_run_connector(self, config: ConnectorConfig) -> bool:
        """Check if connector should run based on schedule"""
        # Simplified scheduling - in production would use proper cron parsing
        if config.last_sync is None:
            return True
        
        # Parse simple schedule formats
        if config.schedule == "hourly":
            return datetime.utcnow() - config.last_sync > timedelta(hours=1)
        elif config.schedule == "daily":
            return datetime.utcnow() - config.last_sync > timedelta(days=1)
        elif config.schedule == "weekly":
            return datetime.utcnow() - config.last_sync > timedelta(weeks=1)
        
        return False


# Example usage and setup
def setup_default_connectors(manager: ConnectorManager):
    """Set up default connectors for Malta Tax AI"""
    
    # Malta Tax Authority connector
    malta_config = ConnectorConfig(
        connector_id="malta_tax_authority",
        name="Malta Tax Authority Website",
        connector_type=ConnectorType.WEB_SCRAPER,
        config={
            "base_url": "https://cfr.gov.mt",
            "sections": ["tax-legislation", "forms", "guidance"]
        },
        schedule="daily",
        enabled=True
    )
    manager.register_connector(malta_config)
    
    # EU Tax Regulation RSS connector
    eu_rss_config = ConnectorConfig(
        connector_id="eu_tax_rss",
        name="EU Tax Regulation RSS Feeds",
        connector_type=ConnectorType.RSS_FEED,
        config={
            "feed_urls": [
                "https://ec.europa.eu/taxation_customs/rss/all_en.xml"
            ],
            "max_items": 20
        },
        schedule="hourly",
        enabled=True
    )
    manager.register_connector(eu_rss_config)
    
    # File watcher connector
    file_watcher_config = ConnectorConfig(
        connector_id="document_watcher",
        name="Document Folder Watcher",
        connector_type=ConnectorType.FILE_WATCHER,
        config={
            "watch_directories": ["/tmp/tax_documents"],
            "file_patterns": ["*.pdf", "*.docx", "*.txt"]
        },
        schedule="hourly",
        enabled=True
    )
    manager.register_connector(file_watcher_config)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Create connector manager
    manager = ConnectorManager()
    
    # Set up default connectors
    setup_default_connectors(manager)
    
    # Start scheduler
    manager.start_scheduler()
    
    # Keep running
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        manager.stop_scheduler()
        print("Connector manager stopped")

