"""
Advanced Document Processing Service
Enhanced OCR accuracy and intelligent data extraction for Malta-specific tax documents
"""

import os
import json
import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Any, Optional, Tuple
import uuid
import re
from enum import Enum

class DocumentType(Enum):
    FS3_CERTIFICATE = "fs3_certificate"
    FS5_RETURN = "fs5_return"
    VAT_RETURN = "vat_return"
    PAYSLIP = "payslip"
    BANK_STATEMENT = "bank_statement"
    INVOICE = "invoice"
    RECEIPT = "receipt"
    EMPLOYMENT_CONTRACT = "employment_contract"
    RENTAL_AGREEMENT = "rental_agreement"
    UNKNOWN = "unknown"

class ProcessingStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REQUIRES_REVIEW = "requires_review"

class AdvancedDocumentProcessor:
    """Advanced document processor for Malta tax documents"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Document processing results storage
        self.processing_results = {}
        
        # Malta-specific patterns and rules
        self.malta_patterns = self._initialize_malta_patterns()
        self.validation_rules = self._initialize_validation_rules()
        self.field_mappings = self._initialize_field_mappings()
    
    def _initialize_malta_patterns(self) -> Dict[str, Any]:
        """Initialize Malta-specific document patterns"""
        return {
            "id_card_number": r"\b\d{8}[A-Z]\b",
            "vat_number": r"\bMT\d{8}\b",
            "company_registration": r"\bC\d{5}\b",
            "euro_amount": r"€\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
            "percentage": r"(\d{1,2}(?:\.\d{1,2})?)\s*%",
            "date_patterns": [
                r"\b(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})\b",
                r"\b(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b",
                r"\b(\d{4})[\/\-](\d{1,2})[\/\-](\d{1,2})\b"
            ],
            "tax_year": r"\b(20\d{2})\b",
            "employment_income_keywords": ["gross salary", "basic salary", "employment income", "wages", "salary"],
            "tax_deduction_keywords": ["tax deducted", "withholding tax", "PAYE", "income tax"],
            "social_security_keywords": ["social security", "SSC", "national insurance", "contributions"]
        }
    
    def _initialize_validation_rules(self) -> Dict[str, Any]:
        """Initialize document validation rules"""
        return {
            "fs3_certificate": {
                "required_fields": ["employer_name", "employee_name", "gross_income", "tax_deducted"],
                "amount_fields": ["gross_income", "tax_deducted", "social_security_employee", "net_income"],
                "date_fields": ["employment_start", "employment_end"],
                "validation_rules": [
                    "net_income = gross_income - tax_deducted - social_security_employee",
                    "tax_deducted >= 0",
                    "gross_income > 0"
                ]
            },
            "payslip": {
                "required_fields": ["employee_name", "gross_pay", "net_pay"],
                "amount_fields": ["gross_pay", "net_pay", "tax_deducted", "social_security"],
                "date_fields": ["pay_period_start", "pay_period_end"],
                "validation_rules": [
                    "net_pay = gross_pay - tax_deducted - social_security",
                    "gross_pay > 0"
                ]
            },
            "vat_return": {
                "required_fields": ["vat_number", "return_period", "total_output_vat"],
                "amount_fields": ["total_output_vat", "total_input_vat", "net_vat_due"],
                "validation_rules": [
                    "net_vat_due = total_output_vat - total_input_vat"
                ]
            }
        }
    
    def _initialize_field_mappings(self) -> Dict[str, Dict[str, List[str]]]:
        """Initialize field mapping keywords for different document types"""
        return {
            "fs3_certificate": {
                "employer_name": ["employer", "company name", "organisation"],
                "employee_name": ["employee", "worker", "staff member", "name"],
                "employee_id": ["id card", "identity card", "id number"],
                "gross_income": ["gross income", "gross salary", "total income", "gross pay"],
                "tax_deducted": ["tax deducted", "income tax", "withholding tax", "PAYE"],
                "social_security_employee": ["social security", "SSC employee", "employee contribution"],
                "social_security_employer": ["SSC employer", "employer contribution"],
                "net_income": ["net income", "net salary", "take home", "net pay"],
                "tax_year": ["tax year", "year", "period"]
            },
            "payslip": {
                "employee_name": ["employee", "name", "worker"],
                "employee_id": ["employee id", "staff id", "id number"],
                "gross_pay": ["gross pay", "gross salary", "basic salary"],
                "tax_deducted": ["income tax", "tax", "PAYE", "withholding"],
                "social_security": ["social security", "SSC", "national insurance"],
                "net_pay": ["net pay", "take home", "net salary"],
                "pay_period": ["pay period", "period", "month"]
            },
            "vat_return": {
                "vat_number": ["vat number", "vat registration", "MT number"],
                "business_name": ["business name", "company", "trader"],
                "return_period": ["return period", "period", "quarter", "month"],
                "standard_rate_sales": ["standard rate sales", "18% sales"],
                "reduced_rate_sales": ["reduced rate sales", "12% sales", "7% sales"],
                "total_output_vat": ["output vat", "vat on sales", "total vat"],
                "total_input_vat": ["input vat", "vat on purchases"],
                "net_vat_due": ["net vat", "vat due", "amount due"]
            }
        }
    
    def classify_document(self, document_content: str, filename: str = "") -> DocumentType:
        """Classify document type based on content and filename"""
        try:
            content_lower = document_content.lower()
            filename_lower = filename.lower()
            
            # Check filename patterns first
            if any(pattern in filename_lower for pattern in ["fs3", "certificate"]):
                return DocumentType.FS3_CERTIFICATE
            elif any(pattern in filename_lower for pattern in ["fs5", "final settlement"]):
                return DocumentType.FS5_RETURN
            elif any(pattern in filename_lower for pattern in ["vat", "value added tax"]):
                return DocumentType.VAT_RETURN
            elif any(pattern in filename_lower for pattern in ["payslip", "salary slip", "pay stub"]):
                return DocumentType.PAYSLIP
            elif any(pattern in filename_lower for pattern in ["bank statement", "statement"]):
                return DocumentType.BANK_STATEMENT
            elif any(pattern in filename_lower for pattern in ["invoice", "bill"]):
                return DocumentType.INVOICE
            elif any(pattern in filename_lower for pattern in ["receipt", "voucher"]):
                return DocumentType.RECEIPT
            
            # Check content patterns
            if any(phrase in content_lower for phrase in ["certificate of tax deducted", "fs3", "employer details"]):
                return DocumentType.FS3_CERTIFICATE
            elif any(phrase in content_lower for phrase in ["final settlement", "fs5", "income tax return"]):
                return DocumentType.FS5_RETURN
            elif any(phrase in content_lower for phrase in ["vat return", "value added tax", "output vat"]):
                return DocumentType.VAT_RETURN
            elif any(phrase in content_lower for phrase in ["payslip", "salary slip", "gross pay", "net pay"]):
                return DocumentType.PAYSLIP
            elif any(phrase in content_lower for phrase in ["bank statement", "account statement", "balance"]):
                return DocumentType.BANK_STATEMENT
            elif any(phrase in content_lower for phrase in ["invoice", "bill to", "amount due"]):
                return DocumentType.INVOICE
            elif any(phrase in content_lower for phrase in ["receipt", "paid", "transaction"]):
                return DocumentType.RECEIPT
            elif any(phrase in content_lower for phrase in ["employment contract", "terms of employment"]):
                return DocumentType.EMPLOYMENT_CONTRACT
            elif any(phrase in content_lower for phrase in ["rental agreement", "lease agreement", "tenancy"]):
                return DocumentType.RENTAL_AGREEMENT
            
            return DocumentType.UNKNOWN
            
        except Exception as e:
            self.logger.error(f"Error classifying document: {str(e)}")
            return DocumentType.UNKNOWN
    
    def extract_structured_data(self, document_content: str, document_type: DocumentType) -> Dict[str, Any]:
        """Extract structured data from document based on type"""
        try:
            extracted_data = {
                "document_type": document_type.value,
                "extraction_timestamp": datetime.utcnow().isoformat(),
                "confidence_score": 0.0,
                "extracted_fields": {},
                "validation_errors": [],
                "raw_text": document_content
            }
            
            if document_type == DocumentType.FS3_CERTIFICATE:
                extracted_data = self._extract_fs3_data(document_content, extracted_data)
            elif document_type == DocumentType.PAYSLIP:
                extracted_data = self._extract_payslip_data(document_content, extracted_data)
            elif document_type == DocumentType.VAT_RETURN:
                extracted_data = self._extract_vat_return_data(document_content, extracted_data)
            elif document_type == DocumentType.BANK_STATEMENT:
                extracted_data = self._extract_bank_statement_data(document_content, extracted_data)
            elif document_type == DocumentType.INVOICE:
                extracted_data = self._extract_invoice_data(document_content, extracted_data)
            
            # Calculate overall confidence score
            extracted_data["confidence_score"] = self._calculate_confidence_score(extracted_data)
            
            # Validate extracted data
            self._validate_extracted_data(extracted_data, document_type)
            
            return extracted_data
            
        except Exception as e:
            self.logger.error(f"Error extracting structured data: {str(e)}")
            return {
                "document_type": document_type.value,
                "extraction_timestamp": datetime.utcnow().isoformat(),
                "confidence_score": 0.0,
                "extracted_fields": {},
                "validation_errors": [f"Extraction failed: {str(e)}"],
                "raw_text": document_content
            }
    
    def _extract_fs3_data(self, content: str, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data from FS3 Certificate of Tax Deducted"""
        fields = extracted_data["extracted_fields"]
        
        # Extract employer name
        employer_patterns = [
            r"employer[:\s]+([^\n\r]+)",
            r"company[:\s]+([^\n\r]+)",
            r"organisation[:\s]+([^\n\r]+)"
        ]
        for pattern in employer_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                fields["employer_name"] = match.group(1).strip()
                break
        
        # Extract employee name
        employee_patterns = [
            r"employee[:\s]+([^\n\r]+)",
            r"worker[:\s]+([^\n\r]+)",
            r"name[:\s]+([^\n\r]+)"
        ]
        for pattern in employee_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                fields["employee_name"] = match.group(1).strip()
                break
        
        # Extract ID card number
        id_match = re.search(self.malta_patterns["id_card_number"], content)
        if id_match:
            fields["employee_id"] = id_match.group(0)
        
        # Extract monetary amounts
        euro_amounts = re.findall(self.malta_patterns["euro_amount"], content)
        if euro_amounts:
            # Try to identify which amount is which based on context
            for i, amount_str in enumerate(euro_amounts):
                amount = float(amount_str.replace(",", ""))
                
                # Look for context around the amount
                amount_context = self._get_amount_context(content, amount_str)
                
                if any(keyword in amount_context.lower() for keyword in ["gross", "total income"]):
                    fields["gross_income"] = amount
                elif any(keyword in amount_context.lower() for keyword in ["tax deducted", "income tax"]):
                    fields["tax_deducted"] = amount
                elif any(keyword in amount_context.lower() for keyword in ["social security", "ssc"]):
                    if "employee" in amount_context.lower():
                        fields["social_security_employee"] = amount
                    elif "employer" in amount_context.lower():
                        fields["social_security_employer"] = amount
                elif any(keyword in amount_context.lower() for keyword in ["net", "take home"]):
                    fields["net_income"] = amount
        
        # Extract tax year
        tax_year_match = re.search(self.malta_patterns["tax_year"], content)
        if tax_year_match:
            fields["tax_year"] = int(tax_year_match.group(1))
        
        return extracted_data
    
    def _extract_payslip_data(self, content: str, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data from payslip"""
        fields = extracted_data["extracted_fields"]
        
        # Extract employee name
        name_patterns = [
            r"employee[:\s]+([^\n\r]+)",
            r"name[:\s]+([^\n\r]+)"
        ]
        for pattern in name_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                fields["employee_name"] = match.group(1).strip()
                break
        
        # Extract monetary amounts with better context matching
        euro_amounts = re.findall(self.malta_patterns["euro_amount"], content)
        if euro_amounts:
            for amount_str in euro_amounts:
                amount = float(amount_str.replace(",", ""))
                amount_context = self._get_amount_context(content, amount_str)
                
                if any(keyword in amount_context.lower() for keyword in ["gross pay", "gross salary", "basic"]):
                    fields["gross_pay"] = amount
                elif any(keyword in amount_context.lower() for keyword in ["net pay", "take home", "net salary"]):
                    fields["net_pay"] = amount
                elif any(keyword in amount_context.lower() for keyword in ["tax", "income tax", "paye"]):
                    fields["tax_deducted"] = amount
                elif any(keyword in amount_context.lower() for keyword in ["social security", "ssc"]):
                    fields["social_security"] = amount
        
        # Extract pay period
        date_patterns = self.malta_patterns["date_patterns"]
        dates_found = []
        for pattern in date_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            dates_found.extend(matches)
        
        if len(dates_found) >= 2:
            fields["pay_period_start"] = self._format_date(dates_found[0])
            fields["pay_period_end"] = self._format_date(dates_found[1])
        
        return extracted_data
    
    def _extract_vat_return_data(self, content: str, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data from VAT return"""
        fields = extracted_data["extracted_fields"]
        
        # Extract VAT number
        vat_match = re.search(self.malta_patterns["vat_number"], content)
        if vat_match:
            fields["vat_number"] = vat_match.group(0)
        
        # Extract business name
        business_patterns = [
            r"business[:\s]+([^\n\r]+)",
            r"company[:\s]+([^\n\r]+)",
            r"trader[:\s]+([^\n\r]+)"
        ]
        for pattern in business_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                fields["business_name"] = match.group(1).strip()
                break
        
        # Extract VAT amounts
        euro_amounts = re.findall(self.malta_patterns["euro_amount"], content)
        if euro_amounts:
            for amount_str in euro_amounts:
                amount = float(amount_str.replace(",", ""))
                amount_context = self._get_amount_context(content, amount_str)
                
                if any(keyword in amount_context.lower() for keyword in ["output vat", "vat on sales"]):
                    fields["total_output_vat"] = amount
                elif any(keyword in amount_context.lower() for keyword in ["input vat", "vat on purchases"]):
                    fields["total_input_vat"] = amount
                elif any(keyword in amount_context.lower() for keyword in ["net vat", "vat due"]):
                    fields["net_vat_due"] = amount
                elif any(keyword in amount_context.lower() for keyword in ["standard rate", "18%"]):
                    if "sales" in amount_context.lower():
                        fields["standard_rate_sales"] = amount
                elif any(keyword in amount_context.lower() for keyword in ["reduced rate", "12%", "7%"]):
                    if "sales" in amount_context.lower():
                        fields["reduced_rate_sales"] = amount
        
        return extracted_data
    
    def _extract_bank_statement_data(self, content: str, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data from bank statement"""
        fields = extracted_data["extracted_fields"]
        
        # Extract account holder name
        name_patterns = [
            r"account holder[:\s]+([^\n\r]+)",
            r"customer[:\s]+([^\n\r]+)"
        ]
        for pattern in name_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                fields["account_holder"] = match.group(1).strip()
                break
        
        # Extract account number
        account_patterns = [
            r"account[:\s]+(\d+)",
            r"a\/c[:\s]+(\d+)"
        ]
        for pattern in account_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                fields["account_number"] = match.group(1)
                break
        
        # Extract transactions (simplified)
        transactions = []
        transaction_pattern = r"(\d{1,2}\/\d{1,2}\/\d{4})\s+([^\d]+)\s+([\d,]+\.\d{2})"
        matches = re.findall(transaction_pattern, content)
        
        for match in matches:
            date, description, amount = match
            transactions.append({
                "date": date,
                "description": description.strip(),
                "amount": float(amount.replace(",", ""))
            })
        
        fields["transactions"] = transactions
        
        return extracted_data
    
    def _extract_invoice_data(self, content: str, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data from invoice"""
        fields = extracted_data["extracted_fields"]
        
        # Extract invoice number
        invoice_patterns = [
            r"invoice[:\s#]+(\w+)",
            r"inv[:\s#]+(\w+)",
            r"#(\w+)"
        ]
        for pattern in invoice_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                fields["invoice_number"] = match.group(1)
                break
        
        # Extract supplier/customer details
        supplier_patterns = [
            r"from[:\s]+([^\n\r]+)",
            r"supplier[:\s]+([^\n\r]+)"
        ]
        for pattern in supplier_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                fields["supplier_name"] = match.group(1).strip()
                break
        
        # Extract total amount
        total_patterns = [
            r"total[:\s]+€\s*([\d,]+\.\d{2})",
            r"amount due[:\s]+€\s*([\d,]+\.\d{2})"
        ]
        for pattern in total_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                fields["total_amount"] = float(match.group(1).replace(",", ""))
                break
        
        # Extract VAT amount
        vat_patterns = [
            r"vat[:\s]+€\s*([\d,]+\.\d{2})",
            r"18%[:\s]+€\s*([\d,]+\.\d{2})"
        ]
        for pattern in vat_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                fields["vat_amount"] = float(match.group(1).replace(",", ""))
                break
        
        return extracted_data
    
    def _get_amount_context(self, content: str, amount_str: str, context_length: int = 50) -> str:
        """Get context around an amount for better classification"""
        try:
            # Find the position of the amount in the content
            amount_pos = content.find(amount_str)
            if amount_pos == -1:
                return ""
            
            # Extract context before and after the amount
            start_pos = max(0, amount_pos - context_length)
            end_pos = min(len(content), amount_pos + len(amount_str) + context_length)
            
            return content[start_pos:end_pos]
            
        except Exception:
            return ""
    
    def _format_date(self, date_tuple: Tuple) -> str:
        """Format date tuple to ISO format"""
        try:
            if len(date_tuple) == 3:
                day, month, year = date_tuple
                if isinstance(month, str):
                    # Month name to number conversion
                    month_names = {
                        "january": "01", "february": "02", "march": "03", "april": "04",
                        "may": "05", "june": "06", "july": "07", "august": "08",
                        "september": "09", "october": "10", "november": "11", "december": "12"
                    }
                    month = month_names.get(month.lower(), "01")
                
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            
            return str(date_tuple)
            
        except Exception:
            return ""
    
    def _calculate_confidence_score(self, extracted_data: Dict[str, Any]) -> float:
        """Calculate confidence score for extracted data"""
        try:
            fields = extracted_data["extracted_fields"]
            document_type = extracted_data["document_type"]
            
            if document_type not in self.validation_rules:
                return 0.5  # Default confidence for unknown types
            
            required_fields = self.validation_rules[document_type]["required_fields"]
            found_fields = len([field for field in required_fields if field in fields])
            
            # Base confidence from required fields
            field_confidence = found_fields / len(required_fields) if required_fields else 0.5
            
            # Bonus for additional fields
            total_fields = len(fields)
            bonus = min(0.2, total_fields * 0.05)
            
            # Penalty for validation errors
            error_penalty = len(extracted_data.get("validation_errors", [])) * 0.1
            
            confidence = min(1.0, max(0.0, field_confidence + bonus - error_penalty))
            return round(confidence, 2)
            
        except Exception:
            return 0.0
    
    def _validate_extracted_data(self, extracted_data: Dict[str, Any], document_type: DocumentType):
        """Validate extracted data against business rules"""
        try:
            fields = extracted_data["extracted_fields"]
            errors = extracted_data["validation_errors"]
            
            if document_type.value not in self.validation_rules:
                return
            
            rules = self.validation_rules[document_type.value]
            
            # Check required fields
            for required_field in rules.get("required_fields", []):
                if required_field not in fields:
                    errors.append(f"Missing required field: {required_field}")
            
            # Validate amount fields
            for amount_field in rules.get("amount_fields", []):
                if amount_field in fields:
                    try:
                        amount = float(fields[amount_field])
                        if amount < 0:
                            errors.append(f"Amount field {amount_field} cannot be negative")
                    except (ValueError, TypeError):
                        errors.append(f"Invalid amount format for field: {amount_field}")
            
            # Validate business rules (simplified)
            if document_type == DocumentType.FS3_CERTIFICATE:
                if all(field in fields for field in ["gross_income", "tax_deducted", "social_security_employee", "net_income"]):
                    calculated_net = fields["gross_income"] - fields["tax_deducted"] - fields.get("social_security_employee", 0)
                    actual_net = fields["net_income"]
                    if abs(calculated_net - actual_net) > 0.01:  # Allow for rounding
                        errors.append("Net income calculation doesn't match: calculated vs actual")
            
        except Exception as e:
            extracted_data["validation_errors"].append(f"Validation error: {str(e)}")
    
    def process_document_batch(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process multiple documents in batch"""
        try:
            batch_id = str(uuid.uuid4())
            batch_results = {
                "batch_id": batch_id,
                "started_at": datetime.utcnow().isoformat(),
                "total_documents": len(documents),
                "processed_documents": 0,
                "failed_documents": 0,
                "results": []
            }
            
            for doc in documents:
                try:
                    doc_id = doc.get("document_id", str(uuid.uuid4()))
                    content = doc.get("content", "")
                    filename = doc.get("filename", "")
                    
                    # Classify and extract
                    doc_type = self.classify_document(content, filename)
                    extracted_data = self.extract_structured_data(content, doc_type)
                    
                    result = {
                        "document_id": doc_id,
                        "filename": filename,
                        "status": ProcessingStatus.COMPLETED.value,
                        "extracted_data": extracted_data
                    }
                    
                    batch_results["results"].append(result)
                    batch_results["processed_documents"] += 1
                    
                except Exception as e:
                    self.logger.error(f"Error processing document {doc.get('document_id', 'unknown')}: {str(e)}")
                    
                    result = {
                        "document_id": doc.get("document_id", str(uuid.uuid4())),
                        "filename": doc.get("filename", ""),
                        "status": ProcessingStatus.FAILED.value,
                        "error": str(e)
                    }
                    
                    batch_results["results"].append(result)
                    batch_results["failed_documents"] += 1
            
            batch_results["completed_at"] = datetime.utcnow().isoformat()
            self.processing_results[batch_id] = batch_results
            
            return batch_results
            
        except Exception as e:
            self.logger.error(f"Error processing document batch: {str(e)}")
            raise ValueError(f"Batch processing failed: {str(e)}")
    
    def reconcile_documents(self, document_ids: List[str]) -> Dict[str, Any]:
        """Reconcile data across multiple documents"""
        try:
            reconciliation_id = str(uuid.uuid4())
            
            # Get extracted data for all documents
            documents_data = []
            for doc_id in document_ids:
                # In a real implementation, this would fetch from database
                # For now, simulate document data
                documents_data.append({
                    "document_id": doc_id,
                    "extracted_data": {"extracted_fields": {}}
                })
            
            reconciliation_result = {
                "reconciliation_id": reconciliation_id,
                "document_ids": document_ids,
                "reconciled_at": datetime.utcnow().isoformat(),
                "discrepancies": [],
                "consolidated_data": {},
                "confidence_score": 0.0
            }
            
            # Perform reconciliation logic here
            # This would compare amounts, dates, and other fields across documents
            # and identify discrepancies
            
            return reconciliation_result
            
        except Exception as e:
            self.logger.error(f"Error reconciling documents: {str(e)}")
            raise ValueError(f"Document reconciliation failed: {str(e)}")
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get document processing statistics"""
        try:
            all_results = list(self.processing_results.values())
            
            stats = {
                "total_batches": len(all_results),
                "total_documents_processed": sum(r.get("processed_documents", 0) for r in all_results),
                "total_documents_failed": sum(r.get("failed_documents", 0) for r in all_results),
                "success_rate": 0.0,
                "document_type_breakdown": {},
                "average_confidence_score": 0.0
            }
            
            total_processed = stats["total_documents_processed"]
            total_failed = stats["total_documents_failed"]
            total_documents = total_processed + total_failed
            
            if total_documents > 0:
                stats["success_rate"] = round((total_processed / total_documents) * 100, 2)
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting processing statistics: {str(e)}")
            return {}

