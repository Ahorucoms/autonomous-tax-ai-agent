"""
Document Management Models for Malta Tax AI Agent
Handles document upload, processing, and metadata management
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import uuid
import os
import hashlib
import mimetypes

class DocumentType(Enum):
    INCOME_STATEMENT = "income_statement"
    BANK_STATEMENT = "bank_statement"
    INVOICE = "invoice"
    RECEIPT = "receipt"
    TAX_RETURN = "tax_return"
    FS3_FORM = "fs3_form"
    FS5_FORM = "fs5_form"
    VAT_RETURN = "vat_return"
    PAYROLL = "payroll"
    CONTRACT = "contract"
    CERTIFICATE = "certificate"
    OTHER = "other"

class DocumentStatus(Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    ARCHIVED = "archived"

class ProcessingStage(Enum):
    UPLOAD = "upload"
    VIRUS_SCAN = "virus_scan"
    OCR = "ocr"
    DATA_EXTRACTION = "data_extraction"
    VALIDATION = "validation"
    CLASSIFICATION = "classification"
    COMPLETED = "completed"

class Document:
    def __init__(self, 
                 filename: str,
                 user_id: str,
                 file_path: str,
                 file_size: int,
                 mime_type: str,
                 document_type: DocumentType = DocumentType.OTHER):
        
        self.id = str(uuid.uuid4())
        self.filename = filename
        self.user_id = user_id
        self.file_path = file_path
        self.file_size = file_size
        self.mime_type = mime_type
        self.document_type = document_type
        self.status = DocumentStatus.UPLOADED
        self.processing_stage = ProcessingStage.UPLOAD
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.processed_at = None
        
        # File metadata
        self.file_hash = None
        self.page_count = None
        self.text_content = ""
        self.extracted_data = {}
        self.confidence_score = 0.0
        
        # Processing metadata
        self.processing_log = []
        self.error_messages = []
        self.ai_analysis = {}
        self.tags = []
        
        # Tax-specific metadata
        self.tax_year = None
        self.tax_period = None
        self.entity_name = ""
        self.entity_id = ""
        self.amounts = {}
        self.dates = {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'filename': self.filename,
            'user_id': self.user_id,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'document_type': self.document_type.value,
            'status': self.status.value,
            'processing_stage': self.processing_stage.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'file_hash': self.file_hash,
            'page_count': self.page_count,
            'text_content': self.text_content,
            'extracted_data': self.extracted_data,
            'confidence_score': self.confidence_score,
            'processing_log': self.processing_log,
            'error_messages': self.error_messages,
            'ai_analysis': self.ai_analysis,
            'tags': self.tags,
            'tax_year': self.tax_year,
            'tax_period': self.tax_period,
            'entity_name': self.entity_name,
            'entity_id': self.entity_id,
            'amounts': self.amounts,
            'dates': self.dates
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Document':
        """Create document from dictionary"""
        doc = cls(
            filename=data['filename'],
            user_id=data['user_id'],
            file_path=data['file_path'],
            file_size=data['file_size'],
            mime_type=data['mime_type'],
            document_type=DocumentType(data.get('document_type', 'other'))
        )
        
        doc.id = data['id']
        doc.status = DocumentStatus(data['status'])
        doc.processing_stage = ProcessingStage(data['processing_stage'])
        doc.created_at = datetime.fromisoformat(data['created_at'])
        doc.updated_at = datetime.fromisoformat(data['updated_at'])
        doc.processed_at = datetime.fromisoformat(data['processed_at']) if data.get('processed_at') else None
        
        doc.file_hash = data.get('file_hash')
        doc.page_count = data.get('page_count')
        doc.text_content = data.get('text_content', '')
        doc.extracted_data = data.get('extracted_data', {})
        doc.confidence_score = data.get('confidence_score', 0.0)
        doc.processing_log = data.get('processing_log', [])
        doc.error_messages = data.get('error_messages', [])
        doc.ai_analysis = data.get('ai_analysis', {})
        doc.tags = data.get('tags', [])
        doc.tax_year = data.get('tax_year')
        doc.tax_period = data.get('tax_period')
        doc.entity_name = data.get('entity_name', '')
        doc.entity_id = data.get('entity_id', '')
        doc.amounts = data.get('amounts', {})
        doc.dates = data.get('dates', {})
        
        return doc
    
    def update_status(self, new_status: DocumentStatus, stage: ProcessingStage = None, message: str = ""):
        """Update document status and processing stage"""
        self.status = new_status
        if stage:
            self.processing_stage = stage
        self.updated_at = datetime.utcnow()
        
        if new_status == DocumentStatus.PROCESSED:
            self.processed_at = datetime.utcnow()
        
        # Add to processing log
        log_entry = {
            'timestamp': self.updated_at.isoformat(),
            'status': new_status.value,
            'stage': stage.value if stage else self.processing_stage.value,
            'message': message
        }
        self.processing_log.append(log_entry)
    
    def add_error(self, error_message: str, stage: ProcessingStage = None):
        """Add error message and update status to failed"""
        self.error_messages.append({
            'timestamp': datetime.utcnow().isoformat(),
            'stage': stage.value if stage else self.processing_stage.value,
            'message': error_message
        })
        self.update_status(DocumentStatus.FAILED, stage, f"Error: {error_message}")
    
    def calculate_file_hash(self) -> str:
        """Calculate MD5 hash of the file"""
        if not os.path.exists(self.file_path):
            return None
        
        hash_md5 = hashlib.md5()
        with open(self.file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        
        self.file_hash = hash_md5.hexdigest()
        return self.file_hash
    
    def add_extracted_data(self, key: str, value: Any, confidence: float = 0.0):
        """Add extracted data with confidence score"""
        self.extracted_data[key] = {
            'value': value,
            'confidence': confidence,
            'extracted_at': datetime.utcnow().isoformat()
        }
        self.updated_at = datetime.utcnow()
    
    def add_ai_analysis(self, analysis_type: str, result: Dict[str, Any]):
        """Add AI analysis result"""
        self.ai_analysis[analysis_type] = {
            'result': result,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.updated_at = datetime.utcnow()
    
    def add_tag(self, tag: str):
        """Add a tag to the document"""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.utcnow()
    
    def is_image(self) -> bool:
        """Check if document is an image"""
        return self.mime_type.startswith('image/')
    
    def is_pdf(self) -> bool:
        """Check if document is a PDF"""
        return self.mime_type == 'application/pdf'
    
    def is_spreadsheet(self) -> bool:
        """Check if document is a spreadsheet"""
        return self.mime_type in [
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'text/csv'
        ]
    
    def get_file_extension(self) -> str:
        """Get file extension from filename"""
        return os.path.splitext(self.filename)[1].lower()

class DocumentManager:
    """Document management service"""
    
    def __init__(self, upload_directory: str = "/tmp/uploads"):
        self.upload_directory = upload_directory
        self.documents = {}  # In production, this would be a database
        
        # Ensure upload directory exists
        os.makedirs(upload_directory, exist_ok=True)
    
    def create_document(self, document: Document) -> str:
        """Create a new document record"""
        self.documents[document.id] = document
        return document.id
    
    def get_document(self, document_id: str) -> Optional[Document]:
        """Get document by ID"""
        return self.documents.get(document_id)
    
    def get_user_documents(self, user_id: str, document_type: Optional[DocumentType] = None) -> List[Document]:
        """Get all documents for a user, optionally filtered by type"""
        user_docs = [doc for doc in self.documents.values() if doc.user_id == user_id]
        
        if document_type:
            user_docs = [doc for doc in user_docs if doc.document_type == document_type]
        
        return sorted(user_docs, key=lambda d: d.created_at, reverse=True)
    
    def update_document(self, document_id: str, updates: Dict[str, Any]) -> bool:
        """Update document with new data"""
        document = self.get_document(document_id)
        if not document:
            return False
        
        for key, value in updates.items():
            if hasattr(document, key):
                setattr(document, key, value)
        
        document.updated_at = datetime.utcnow()
        return True
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document and its file"""
        document = self.get_document(document_id)
        if not document:
            return False
        
        # Delete file if it exists
        if os.path.exists(document.file_path):
            try:
                os.remove(document.file_path)
            except OSError:
                pass  # File might be in use or already deleted
        
        # Remove from documents
        del self.documents[document_id]
        return True
    
    def save_uploaded_file(self, file_data: bytes, filename: str, user_id: str) -> str:
        """Save uploaded file and return file path"""
        # Generate unique filename
        file_ext = os.path.splitext(filename)[1]
        unique_filename = f"{user_id}_{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(self.upload_directory, unique_filename)
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        return file_path
    
    def get_documents_by_status(self, status: DocumentStatus) -> List[Document]:
        """Get all documents with a specific status"""
        return [doc for doc in self.documents.values() if doc.status == status]
    
    def get_processing_queue(self) -> List[Document]:
        """Get documents that need processing"""
        return [doc for doc in self.documents.values() 
                if doc.status in [DocumentStatus.UPLOADED, DocumentStatus.PROCESSING]]
    
    def classify_document_type(self, filename: str, text_content: str = "") -> DocumentType:
        """Classify document type based on filename and content"""
        filename_lower = filename.lower()
        content_lower = text_content.lower()
        
        # Classification rules based on filename
        if 'fs3' in filename_lower:
            return DocumentType.FS3_FORM
        elif 'fs5' in filename_lower:
            return DocumentType.FS5_FORM
        elif 'vat' in filename_lower and 'return' in filename_lower:
            return DocumentType.VAT_RETURN
        elif 'bank' in filename_lower and 'statement' in filename_lower:
            return DocumentType.BANK_STATEMENT
        elif 'invoice' in filename_lower:
            return DocumentType.INVOICE
        elif 'receipt' in filename_lower:
            return DocumentType.RECEIPT
        elif 'payroll' in filename_lower or 'salary' in filename_lower:
            return DocumentType.PAYROLL
        elif 'tax' in filename_lower and 'return' in filename_lower:
            return DocumentType.TAX_RETURN
        
        # Classification rules based on content
        if content_lower:
            if 'fs3' in content_lower or 'certificate of tax deducted' in content_lower:
                return DocumentType.FS3_FORM
            elif 'fs5' in content_lower or 'final settlement system' in content_lower:
                return DocumentType.FS5_FORM
            elif 'vat return' in content_lower or 'value added tax' in content_lower:
                return DocumentType.VAT_RETURN
            elif 'bank statement' in content_lower or 'account statement' in content_lower:
                return DocumentType.BANK_STATEMENT
            elif 'invoice' in content_lower and ('total' in content_lower or 'amount' in content_lower):
                return DocumentType.INVOICE
        
        return DocumentType.OTHER

