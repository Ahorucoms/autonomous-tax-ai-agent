"""
Malta Tax Form Generation Service
Generates and fills Malta tax forms including FS3, FS5, VAT returns
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Any, Optional
import json
import logging
from enum import Enum
import uuid

class FormType(Enum):
    FS3 = "fs3"
    FS5 = "fs5"
    VAT_RETURN = "vat_return"
    INCOME_TAX_RETURN = "income_tax_return"
    SOCIAL_SECURITY_RETURN = "social_security_return"

class FormStatus(Enum):
    DRAFT = "draft"
    COMPLETED = "completed"
    VALIDATED = "validated"
    SUBMITTED = "submitted"
    REJECTED = "rejected"

class MaltaFormGenerator:
    """Malta tax form generator and filler"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.forms = {}  # In production, this would be a database
        
        # Form templates
        self.form_templates = {
            FormType.FS3: self._get_fs3_template(),
            FormType.FS5: self._get_fs5_template(),
            FormType.VAT_RETURN: self._get_vat_return_template(),
            FormType.INCOME_TAX_RETURN: self._get_income_tax_return_template(),
            FormType.SOCIAL_SECURITY_RETURN: self._get_social_security_return_template()
        }
    
    def _get_fs3_template(self) -> Dict[str, Any]:
        """FS3 Certificate of Tax Deducted template"""
        return {
            "form_id": "FS3",
            "title": "Certificate of Tax Deducted",
            "description": "Certificate showing tax deducted at source from employment income",
            "sections": [
                {
                    "section_id": "employer_details",
                    "title": "Employer Details",
                    "fields": [
                        {"field_id": "employer_name", "label": "Employer Name", "type": "text", "required": True},
                        {"field_id": "employer_id", "label": "Employer ID Number", "type": "text", "required": True},
                        {"field_id": "employer_address", "label": "Employer Address", "type": "textarea", "required": True},
                        {"field_id": "employer_contact", "label": "Contact Details", "type": "text", "required": False}
                    ]
                },
                {
                    "section_id": "employee_details",
                    "title": "Employee Details",
                    "fields": [
                        {"field_id": "employee_name", "label": "Employee Name", "type": "text", "required": True},
                        {"field_id": "employee_id", "label": "ID Card Number", "type": "text", "required": True},
                        {"field_id": "employee_address", "label": "Employee Address", "type": "textarea", "required": True},
                        {"field_id": "employment_start", "label": "Employment Start Date", "type": "date", "required": True},
                        {"field_id": "employment_end", "label": "Employment End Date", "type": "date", "required": False}
                    ]
                },
                {
                    "section_id": "income_details",
                    "title": "Income and Tax Details",
                    "fields": [
                        {"field_id": "gross_income", "label": "Gross Income (EUR)", "type": "decimal", "required": True},
                        {"field_id": "tax_deducted", "label": "Tax Deducted (EUR)", "type": "decimal", "required": True},
                        {"field_id": "social_security_employee", "label": "Social Security - Employee (EUR)", "type": "decimal", "required": True},
                        {"field_id": "social_security_employer", "label": "Social Security - Employer (EUR)", "type": "decimal", "required": True},
                        {"field_id": "net_income", "label": "Net Income (EUR)", "type": "decimal", "required": True},
                        {"field_id": "tax_year", "label": "Tax Year", "type": "number", "required": True}
                    ]
                }
            ],
            "validation_rules": [
                {"rule": "net_income = gross_income - tax_deducted - social_security_employee", "type": "calculation"},
                {"rule": "tax_year >= 2020 AND tax_year <= current_year", "type": "range"},
                {"rule": "gross_income > 0", "type": "positive"}
            ]
        }
    
    def _get_fs5_template(self) -> Dict[str, Any]:
        """FS5 Final Settlement System template"""
        return {
            "form_id": "FS5",
            "title": "Final Settlement System",
            "description": "Final settlement of income tax for individuals",
            "sections": [
                {
                    "section_id": "taxpayer_details",
                    "title": "Taxpayer Details",
                    "fields": [
                        {"field_id": "taxpayer_name", "label": "Full Name", "type": "text", "required": True},
                        {"field_id": "taxpayer_id", "label": "ID Card Number", "type": "text", "required": True},
                        {"field_id": "taxpayer_address", "label": "Address", "type": "textarea", "required": True},
                        {"field_id": "marital_status", "label": "Marital Status", "type": "select", "options": ["single", "married", "widowed", "separated"], "required": True},
                        {"field_id": "tax_year", "label": "Tax Year", "type": "number", "required": True}
                    ]
                },
                {
                    "section_id": "income_sources",
                    "title": "Income Sources",
                    "fields": [
                        {"field_id": "employment_income", "label": "Employment Income (EUR)", "type": "decimal", "required": False},
                        {"field_id": "self_employment_income", "label": "Self-Employment Income (EUR)", "type": "decimal", "required": False},
                        {"field_id": "rental_income", "label": "Rental Income (EUR)", "type": "decimal", "required": False},
                        {"field_id": "investment_income", "label": "Investment Income (EUR)", "type": "decimal", "required": False},
                        {"field_id": "other_income", "label": "Other Income (EUR)", "type": "decimal", "required": False},
                        {"field_id": "total_income", "label": "Total Income (EUR)", "type": "decimal", "required": True, "calculated": True}
                    ]
                },
                {
                    "section_id": "deductions",
                    "title": "Allowable Deductions",
                    "fields": [
                        {"field_id": "business_expenses", "label": "Business Expenses (EUR)", "type": "decimal", "required": False},
                        {"field_id": "professional_expenses", "label": "Professional Expenses (EUR)", "type": "decimal", "required": False},
                        {"field_id": "charitable_donations", "label": "Charitable Donations (EUR)", "type": "decimal", "required": False},
                        {"field_id": "mortgage_interest", "label": "Mortgage Interest (EUR)", "type": "decimal", "required": False},
                        {"field_id": "other_deductions", "label": "Other Deductions (EUR)", "type": "decimal", "required": False},
                        {"field_id": "total_deductions", "label": "Total Deductions (EUR)", "type": "decimal", "required": True, "calculated": True}
                    ]
                },
                {
                    "section_id": "tax_calculation",
                    "title": "Tax Calculation",
                    "fields": [
                        {"field_id": "taxable_income", "label": "Taxable Income (EUR)", "type": "decimal", "required": True, "calculated": True},
                        {"field_id": "tax_due", "label": "Tax Due (EUR)", "type": "decimal", "required": True, "calculated": True},
                        {"field_id": "tax_paid", "label": "Tax Already Paid (EUR)", "type": "decimal", "required": True},
                        {"field_id": "tax_refund_due", "label": "Refund Due (EUR)", "type": "decimal", "required": False, "calculated": True},
                        {"field_id": "additional_tax_due", "label": "Additional Tax Due (EUR)", "type": "decimal", "required": False, "calculated": True}
                    ]
                }
            ],
            "validation_rules": [
                {"rule": "total_income = employment_income + self_employment_income + rental_income + investment_income + other_income", "type": "calculation"},
                {"rule": "total_deductions = business_expenses + professional_expenses + charitable_donations + mortgage_interest + other_deductions", "type": "calculation"},
                {"rule": "taxable_income = total_income - total_deductions", "type": "calculation"},
                {"rule": "taxable_income >= 0", "type": "positive"}
            ]
        }
    
    def _get_vat_return_template(self) -> Dict[str, Any]:
        """VAT Return template"""
        return {
            "form_id": "VAT_RETURN",
            "title": "VAT Return",
            "description": "Value Added Tax Return for Malta",
            "sections": [
                {
                    "section_id": "business_details",
                    "title": "Business Details",
                    "fields": [
                        {"field_id": "business_name", "label": "Business Name", "type": "text", "required": True},
                        {"field_id": "vat_number", "label": "VAT Registration Number", "type": "text", "required": True},
                        {"field_id": "business_address", "label": "Business Address", "type": "textarea", "required": True},
                        {"field_id": "return_period", "label": "Return Period", "type": "text", "required": True},
                        {"field_id": "return_frequency", "label": "Return Frequency", "type": "select", "options": ["monthly", "quarterly"], "required": True}
                    ]
                },
                {
                    "section_id": "sales_output",
                    "title": "Sales and Output VAT",
                    "fields": [
                        {"field_id": "standard_rate_sales", "label": "Standard Rate Sales (18%)", "type": "decimal", "required": False},
                        {"field_id": "standard_rate_vat", "label": "Standard Rate VAT", "type": "decimal", "required": False, "calculated": True},
                        {"field_id": "reduced_rate_sales", "label": "Reduced Rate Sales", "type": "decimal", "required": False},
                        {"field_id": "reduced_rate_vat", "label": "Reduced Rate VAT", "type": "decimal", "required": False, "calculated": True},
                        {"field_id": "zero_rate_sales", "label": "Zero Rate Sales", "type": "decimal", "required": False},
                        {"field_id": "exempt_sales", "label": "Exempt Sales", "type": "decimal", "required": False},
                        {"field_id": "total_output_vat", "label": "Total Output VAT", "type": "decimal", "required": True, "calculated": True}
                    ]
                },
                {
                    "section_id": "purchases_input",
                    "title": "Purchases and Input VAT",
                    "fields": [
                        {"field_id": "standard_rate_purchases", "label": "Standard Rate Purchases", "type": "decimal", "required": False},
                        {"field_id": "standard_rate_input_vat", "label": "Standard Rate Input VAT", "type": "decimal", "required": False, "calculated": True},
                        {"field_id": "reduced_rate_purchases", "label": "Reduced Rate Purchases", "type": "decimal", "required": False},
                        {"field_id": "reduced_rate_input_vat", "label": "Reduced Rate Input VAT", "type": "decimal", "required": False, "calculated": True},
                        {"field_id": "total_input_vat", "label": "Total Input VAT", "type": "decimal", "required": True, "calculated": True}
                    ]
                },
                {
                    "section_id": "vat_calculation",
                    "title": "VAT Calculation",
                    "fields": [
                        {"field_id": "net_vat_due", "label": "Net VAT Due", "type": "decimal", "required": True, "calculated": True},
                        {"field_id": "vat_refund_due", "label": "VAT Refund Due", "type": "decimal", "required": False, "calculated": True}
                    ]
                }
            ],
            "validation_rules": [
                {"rule": "standard_rate_vat = standard_rate_sales * 0.18", "type": "calculation"},
                {"rule": "standard_rate_input_vat = standard_rate_purchases * 0.18", "type": "calculation"},
                {"rule": "net_vat_due = total_output_vat - total_input_vat", "type": "calculation"}
            ]
        }
    
    def _get_income_tax_return_template(self) -> Dict[str, Any]:
        """Income Tax Return template"""
        return {
            "form_id": "INCOME_TAX_RETURN",
            "title": "Income Tax Return",
            "description": "Annual Income Tax Return for Malta",
            "sections": [
                {
                    "section_id": "personal_details",
                    "title": "Personal Details",
                    "fields": [
                        {"field_id": "full_name", "label": "Full Name", "type": "text", "required": True},
                        {"field_id": "id_number", "label": "ID Card Number", "type": "text", "required": True},
                        {"field_id": "address", "label": "Address", "type": "textarea", "required": True},
                        {"field_id": "marital_status", "label": "Marital Status", "type": "select", "options": ["single", "married", "widowed", "separated"], "required": True},
                        {"field_id": "spouse_name", "label": "Spouse Name", "type": "text", "required": False},
                        {"field_id": "tax_year", "label": "Tax Year", "type": "number", "required": True}
                    ]
                }
            ]
        }
    
    def _get_social_security_return_template(self) -> Dict[str, Any]:
        """Social Security Return template"""
        return {
            "form_id": "SOCIAL_SECURITY_RETURN",
            "title": "Social Security Return",
            "description": "Social Security Contributions Return",
            "sections": []
        }
    
    def create_form(self, form_type: FormType, user_id: str, data: Dict[str, Any] = None) -> str:
        """Create a new form instance"""
        try:
            form_id = str(uuid.uuid4())
            template = self.form_templates[form_type].copy()
            
            form_instance = {
                "form_id": form_id,
                "user_id": user_id,
                "form_type": form_type.value,
                "template": template,
                "data": data or {},
                "status": FormStatus.DRAFT.value,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "validation_errors": [],
                "submission_history": []
            }
            
            self.forms[form_id] = form_instance
            return form_id
            
        except Exception as e:
            self.logger.error(f"Error creating form: {str(e)}")
            raise ValueError(f"Form creation failed: {str(e)}")
    
    def get_form(self, form_id: str) -> Optional[Dict[str, Any]]:
        """Get form by ID"""
        return self.forms.get(form_id)
    
    def update_form_data(self, form_id: str, field_updates: Dict[str, Any]) -> bool:
        """Update form field data"""
        try:
            form = self.get_form(form_id)
            if not form:
                return False
            
            # Update field data
            form["data"].update(field_updates)
            form["updated_at"] = datetime.utcnow().isoformat()
            
            # Recalculate computed fields
            self._calculate_computed_fields(form)
            
            # Validate form
            self._validate_form(form)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating form data: {str(e)}")
            return False
    
    def _calculate_computed_fields(self, form: Dict[str, Any]):
        """Calculate computed/calculated fields"""
        try:
            form_type = FormType(form["form_type"])
            data = form["data"]
            
            if form_type == FormType.FS3:
                # Calculate net income
                gross_income = Decimal(str(data.get("gross_income", 0)))
                tax_deducted = Decimal(str(data.get("tax_deducted", 0)))
                social_security = Decimal(str(data.get("social_security_employee", 0)))
                data["net_income"] = float(gross_income - tax_deducted - social_security)
            
            elif form_type == FormType.FS5:
                # Calculate totals
                income_fields = ["employment_income", "self_employment_income", "rental_income", "investment_income", "other_income"]
                total_income = sum(Decimal(str(data.get(field, 0))) for field in income_fields)
                data["total_income"] = float(total_income)
                
                deduction_fields = ["business_expenses", "professional_expenses", "charitable_donations", "mortgage_interest", "other_deductions"]
                total_deductions = sum(Decimal(str(data.get(field, 0))) for field in deduction_fields)
                data["total_deductions"] = float(total_deductions)
                
                taxable_income = total_income - total_deductions
                data["taxable_income"] = float(max(taxable_income, Decimal('0')))
                
                # Calculate tax refund or additional tax due
                tax_due = Decimal(str(data.get("tax_due", 0)))
                tax_paid = Decimal(str(data.get("tax_paid", 0)))
                difference = tax_paid - tax_due
                
                if difference > 0:
                    data["tax_refund_due"] = float(difference)
                    data["additional_tax_due"] = 0
                else:
                    data["tax_refund_due"] = 0
                    data["additional_tax_due"] = float(abs(difference))
            
            elif form_type == FormType.VAT_RETURN:
                # Calculate VAT amounts
                standard_sales = Decimal(str(data.get("standard_rate_sales", 0)))
                data["standard_rate_vat"] = float(standard_sales * Decimal('0.18'))
                
                reduced_sales = Decimal(str(data.get("reduced_rate_sales", 0)))
                data["reduced_rate_vat"] = float(reduced_sales * Decimal('0.12'))  # Assuming 12% reduced rate
                
                total_output_vat = Decimal(str(data.get("standard_rate_vat", 0))) + Decimal(str(data.get("reduced_rate_vat", 0)))
                data["total_output_vat"] = float(total_output_vat)
                
                standard_purchases = Decimal(str(data.get("standard_rate_purchases", 0)))
                data["standard_rate_input_vat"] = float(standard_purchases * Decimal('0.18'))
                
                reduced_purchases = Decimal(str(data.get("reduced_rate_purchases", 0)))
                data["reduced_rate_input_vat"] = float(reduced_purchases * Decimal('0.12'))
                
                total_input_vat = Decimal(str(data.get("standard_rate_input_vat", 0))) + Decimal(str(data.get("reduced_rate_input_vat", 0)))
                data["total_input_vat"] = float(total_input_vat)
                
                net_vat = total_output_vat - total_input_vat
                if net_vat > 0:
                    data["net_vat_due"] = float(net_vat)
                    data["vat_refund_due"] = 0
                else:
                    data["net_vat_due"] = 0
                    data["vat_refund_due"] = float(abs(net_vat))
            
        except Exception as e:
            self.logger.error(f"Error calculating computed fields: {str(e)}")
    
    def _validate_form(self, form: Dict[str, Any]):
        """Validate form data against rules"""
        try:
            errors = []
            template = form["template"]
            data = form["data"]
            
            # Validate required fields
            for section in template["sections"]:
                for field in section["fields"]:
                    if field["required"] and field["field_id"] not in data:
                        errors.append(f"Required field '{field['label']}' is missing")
                    elif field["required"] and not data.get(field["field_id"]):
                        errors.append(f"Required field '{field['label']}' cannot be empty")
            
            # Validate field types and ranges
            for section in template["sections"]:
                for field in section["fields"]:
                    field_id = field["field_id"]
                    if field_id in data and data[field_id] is not None:
                        value = data[field_id]
                        
                        if field["type"] == "decimal" and not isinstance(value, (int, float, Decimal)):
                            try:
                                Decimal(str(value))
                            except:
                                errors.append(f"Field '{field['label']}' must be a valid number")
                        
                        elif field["type"] == "number" and not isinstance(value, (int, float)):
                            try:
                                float(value)
                            except:
                                errors.append(f"Field '{field['label']}' must be a valid number")
                        
                        elif field["type"] == "select" and "options" in field:
                            if value not in field["options"]:
                                errors.append(f"Field '{field['label']}' must be one of: {', '.join(field['options'])}")
            
            # Validate business rules
            if "validation_rules" in template:
                for rule in template["validation_rules"]:
                    if rule["type"] == "positive":
                        field_name = rule["rule"].split()[0]
                        if field_name in data and float(data[field_name]) < 0:
                            errors.append(f"Field '{field_name}' must be positive")
                    
                    elif rule["type"] == "range":
                        # Parse range rules (simplified)
                        if "tax_year" in rule["rule"] and "tax_year" in data:
                            tax_year = int(data["tax_year"])
                            current_year = datetime.now().year
                            if tax_year < 2020 or tax_year > current_year:
                                errors.append(f"Tax year must be between 2020 and {current_year}")
            
            form["validation_errors"] = errors
            
            # Update status based on validation
            if not errors:
                if form["status"] == FormStatus.DRAFT.value:
                    form["status"] = FormStatus.COMPLETED.value
            else:
                form["status"] = FormStatus.DRAFT.value
            
        except Exception as e:
            self.logger.error(f"Error validating form: {str(e)}")
            form["validation_errors"] = [f"Validation error: {str(e)}"]
    
    def auto_fill_form(self, form_id: str, extracted_data: Dict[str, Any]) -> bool:
        """Auto-fill form from extracted document data"""
        try:
            form = self.get_form(form_id)
            if not form:
                return False
            
            form_type = FormType(form["form_type"])
            
            # Map extracted data to form fields based on form type
            field_mapping = self._get_field_mapping(form_type)
            
            updates = {}
            for extracted_key, extracted_value in extracted_data.items():
                if extracted_key in field_mapping:
                    form_field = field_mapping[extracted_key]
                    updates[form_field] = extracted_value
            
            if updates:
                return self.update_form_data(form_id, updates)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error auto-filling form: {str(e)}")
            return False
    
    def _get_field_mapping(self, form_type: FormType) -> Dict[str, str]:
        """Get mapping from extracted data keys to form field IDs"""
        mappings = {
            FormType.FS3: {
                "employer_name": "employer_name",
                "employee_name": "employee_name",
                "gross_income": "gross_income",
                "tax_deducted": "tax_deducted",
                "social_security": "social_security_employee",
                "tax_year": "tax_year"
            },
            FormType.FS5: {
                "employment_income": "employment_income",
                "self_employment_income": "self_employment_income",
                "rental_income": "rental_income",
                "business_expenses": "business_expenses",
                "tax_year": "tax_year"
            },
            FormType.VAT_RETURN: {
                "standard_rate_sales": "standard_rate_sales",
                "reduced_rate_sales": "reduced_rate_sales",
                "standard_rate_purchases": "standard_rate_purchases",
                "vat_number": "vat_number"
            }
        }
        
        return mappings.get(form_type, {})
    
    def generate_pdf(self, form_id: str) -> Optional[str]:
        """Generate PDF from completed form"""
        try:
            form = self.get_form(form_id)
            if not form:
                return None
            
            if form["status"] not in [FormStatus.COMPLETED.value, FormStatus.VALIDATED.value]:
                raise ValueError("Form must be completed before generating PDF")
            
            # In a real implementation, this would use a PDF generation library
            # For now, return a placeholder path
            pdf_path = f"/tmp/forms/{form_id}.pdf"
            
            # Simulate PDF generation
            form["pdf_path"] = pdf_path
            form["pdf_generated_at"] = datetime.utcnow().isoformat()
            
            return pdf_path
            
        except Exception as e:
            self.logger.error(f"Error generating PDF: {str(e)}")
            return None
    
    def submit_form(self, form_id: str, submission_method: str = "electronic") -> bool:
        """Submit form to tax authorities"""
        try:
            form = self.get_form(form_id)
            if not form:
                return False
            
            if form["status"] != FormStatus.COMPLETED.value:
                raise ValueError("Form must be completed before submission")
            
            # Simulate submission
            submission_record = {
                "submission_id": str(uuid.uuid4()),
                "submission_method": submission_method,
                "submitted_at": datetime.utcnow().isoformat(),
                "status": "submitted",
                "acknowledgment_number": f"ACK-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
            }
            
            form["submission_history"].append(submission_record)
            form["status"] = FormStatus.SUBMITTED.value
            form["updated_at"] = datetime.utcnow().isoformat()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error submitting form: {str(e)}")
            return False
    
    def get_user_forms(self, user_id: str, form_type: Optional[FormType] = None) -> List[Dict[str, Any]]:
        """Get all forms for a user"""
        user_forms = [form for form in self.forms.values() if form["user_id"] == user_id]
        
        if form_type:
            user_forms = [form for form in user_forms if form["form_type"] == form_type.value]
        
        return sorted(user_forms, key=lambda f: f["created_at"], reverse=True)
    
    def get_form_templates(self) -> Dict[str, Any]:
        """Get all available form templates"""
        return {
            form_type.value: {
                "form_type": form_type.value,
                "title": template["title"],
                "description": template["description"],
                "sections": len(template["sections"]),
                "fields": sum(len(section["fields"]) for section in template["sections"])
            }
            for form_type, template in self.form_templates.items()
        }

