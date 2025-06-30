"""
PDF Form Generator Service
Autonomous tax form generation and completion
"""

import os
import logging
from typing import Dict, Any, List, Optional, Tuple
import json
from datetime import datetime
import tempfile
import base64

# PDF generation
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# PDF form filling
try:
    from PyPDF2 import PdfReader, PdfWriter
    from PyPDF2.generic import BooleanObject, NameObject, IndirectObject
except ImportError:
    PdfReader = PdfWriter = None
    logging.warning("PyPDF2 not available - PDF form filling disabled")

# Database
from services.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

class PDFFormGenerator:
    """Autonomous PDF tax form generator"""
    
    def __init__(self):
        self.form_templates = {}
        self.jurisdiction_forms = {
            'MT': [
                'income_tax_return',
                'vat_return',
                'corporate_tax_return',
                'provisional_tax_form',
                'final_settlement_form'
            ],
            'FR': [
                'declaration_revenus',
                'tva_declaration',
                'impot_societes',
                'declaration_professionnelle'
            ],
            'DE': [
                'einkommensteuererklarung',
                'umsatzsteuervoranmeldung',
                'korperschaftsteuererklarung',
                'gewerbesteuererklarung'
            ],
            'CA': [
                'personal_income_tax',
                'gst_hst_return',
                'corporate_income_tax',
                'payroll_deductions'
            ],
            'AU': [
                'individual_tax_return',
                'business_activity_statement',
                'company_tax_return',
                'fringe_benefits_tax'
            ]
        }
        
        # Initialize form templates
        self._initialize_form_templates()
    
    async def generate_form(self, 
                          form_type: str, 
                          jurisdiction: str, 
                          user_data: Dict[str, Any],
                          tax_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate a tax form based on user and tax data"""
        try:
            # Validate form type and jurisdiction
            if jurisdiction not in self.jurisdiction_forms:
                return {'success': False, 'error': f'Unsupported jurisdiction: {jurisdiction}'}
            
            if form_type not in self.jurisdiction_forms[jurisdiction]:
                return {'success': False, 'error': f'Form type {form_type} not available for {jurisdiction}'}
            
            # Get form template
            template = self._get_form_template(form_type, jurisdiction)
            if not template:
                return {'success': False, 'error': f'Template not found for {form_type}'}
            
            # Generate PDF
            pdf_path = await self._generate_pdf_form(template, user_data, tax_data, jurisdiction)
            
            if pdf_path:
                # Store form metadata
                form_metadata = await self._store_form_metadata(
                    form_type, jurisdiction, user_data, pdf_path
                )
                
                # Convert to base64 for API response
                with open(pdf_path, 'rb') as pdf_file:
                    pdf_base64 = base64.b64encode(pdf_file.read()).decode('utf-8')
                
                return {
                    'success': True,
                    'form_type': form_type,
                    'jurisdiction': jurisdiction,
                    'pdf_path': pdf_path,
                    'pdf_base64': pdf_base64,
                    'metadata': form_metadata,
                    'generated_at': datetime.now().isoformat()
                }
            else:
                return {'success': False, 'error': 'Failed to generate PDF'}
                
        except Exception as e:
            logger.error(f"Form generation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def fill_existing_form(self, 
                               form_path: str, 
                               field_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fill an existing PDF form with data"""
        try:
            if not PdfReader or not PdfWriter:
                return {'success': False, 'error': 'PDF form filling not available'}
            
            # Read the existing PDF
            reader = PdfReader(form_path)
            writer = PdfWriter()
            
            # Fill form fields
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                
                # Update form fields if they exist
                if '/Annots' in page:
                    for annotation in page['/Annots']:
                        annotation_obj = annotation.get_object()
                        if annotation_obj.get('/Subtype') == '/Widget':
                            field_name = annotation_obj.get('/T')
                            if field_name and field_name in field_data:
                                annotation_obj.update({
                                    NameObject('/V'): field_data[field_name]
                                })
                
                writer.add_page(page)
            
            # Save filled form
            output_path = tempfile.mktemp(suffix='.pdf')
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            # Convert to base64
            with open(output_path, 'rb') as pdf_file:
                pdf_base64 = base64.b64encode(pdf_file.read()).decode('utf-8')
            
            return {
                'success': True,
                'filled_form_path': output_path,
                'pdf_base64': pdf_base64,
                'fields_filled': len(field_data)
            }
            
        except Exception as e:
            logger.error(f"Form filling failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_available_forms(self, jurisdiction: str = None) -> Dict[str, Any]:
        """Get list of available forms"""
        try:
            if jurisdiction:
                if jurisdiction in self.jurisdiction_forms:
                    forms = self.jurisdiction_forms[jurisdiction]
                    return {
                        'success': True,
                        'jurisdiction': jurisdiction,
                        'forms': forms,
                        'total_forms': len(forms)
                    }
                else:
                    return {'success': False, 'error': f'Unsupported jurisdiction: {jurisdiction}'}
            else:
                return {
                    'success': True,
                    'all_jurisdictions': self.jurisdiction_forms,
                    'total_jurisdictions': len(self.jurisdiction_forms)
                }
                
        except Exception as e:
            logger.error(f"Failed to get available forms: {e}")
            return {'success': False, 'error': str(e)}
    
    async def validate_form_data(self, 
                               form_type: str, 
                               jurisdiction: str, 
                               form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate form data against requirements"""
        try:
            template = self._get_form_template(form_type, jurisdiction)
            if not template:
                return {'success': False, 'error': 'Template not found'}
            
            validation_errors = []
            warnings = []
            
            # Check required fields
            required_fields = template.get('required_fields', [])
            for field in required_fields:
                if field not in form_data or not form_data[field]:
                    validation_errors.append(f'Required field missing: {field}')
            
            # Validate field formats
            field_validations = template.get('field_validations', {})
            for field, validation in field_validations.items():
                if field in form_data:
                    value = form_data[field]
                    if not self._validate_field(value, validation):
                        validation_errors.append(f'Invalid format for field: {field}')
            
            # Check business rules
            business_rules = template.get('business_rules', [])
            for rule in business_rules:
                if not self._check_business_rule(rule, form_data):
                    warnings.append(f'Business rule warning: {rule["message"]}')
            
            return {
                'success': True,
                'valid': len(validation_errors) == 0,
                'errors': validation_errors,
                'warnings': warnings,
                'total_errors': len(validation_errors),
                'total_warnings': len(warnings)
            }
            
        except Exception as e:
            logger.error(f"Form validation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_form_preview(self, 
                             form_type: str, 
                             jurisdiction: str) -> Dict[str, Any]:
        """Get form preview and field information"""
        try:
            template = self._get_form_template(form_type, jurisdiction)
            if not template:
                return {'success': False, 'error': 'Template not found'}
            
            return {
                'success': True,
                'form_type': form_type,
                'jurisdiction': jurisdiction,
                'title': template.get('title', ''),
                'description': template.get('description', ''),
                'sections': template.get('sections', []),
                'required_fields': template.get('required_fields', []),
                'estimated_time': template.get('estimated_time', '15-30 minutes'),
                'filing_deadline': template.get('filing_deadline', ''),
                'instructions': template.get('instructions', [])
            }
            
        except Exception as e:
            logger.error(f"Form preview failed: {e}")
            return {'success': False, 'error': str(e)}
    
    # Private helper methods
    
    def _initialize_form_templates(self):
        """Initialize form templates for different jurisdictions"""
        
        # Malta Income Tax Return
        self.form_templates['MT_income_tax_return'] = {
            'title': 'Malta Individual Income Tax Return',
            'description': 'Annual income tax return for Malta residents',
            'sections': [
                {
                    'title': 'Personal Information',
                    'fields': ['full_name', 'id_card_number', 'address', 'marital_status']
                },
                {
                    'title': 'Income Details',
                    'fields': ['employment_income', 'business_income', 'investment_income', 'other_income']
                },
                {
                    'title': 'Deductions and Allowances',
                    'fields': ['personal_allowance', 'spouse_allowance', 'children_allowance', 'other_deductions']
                },
                {
                    'title': 'Tax Calculation',
                    'fields': ['total_income', 'total_deductions', 'taxable_income', 'tax_due']
                }
            ],
            'required_fields': ['full_name', 'id_card_number', 'employment_income'],
            'field_validations': {
                'id_card_number': {'type': 'malta_id', 'pattern': r'^\d{7}[MFGH]$'},
                'employment_income': {'type': 'currency', 'min': 0},
                'business_income': {'type': 'currency', 'min': 0}
            },
            'business_rules': [
                {
                    'condition': 'total_income > 60000',
                    'message': 'High income may require additional documentation'
                }
            ],
            'filing_deadline': 'June 30th',
            'estimated_time': '20-30 minutes'
        }
        
        # France Income Declaration
        self.form_templates['FR_declaration_revenus'] = {
            'title': 'Déclaration de Revenus (France)',
            'description': 'Déclaration annuelle des revenus pour résidents français',
            'sections': [
                {
                    'title': 'État Civil',
                    'fields': ['nom', 'prenom', 'numero_fiscal', 'adresse', 'situation_familiale']
                },
                {
                    'title': 'Revenus',
                    'fields': ['salaires', 'revenus_fonciers', 'revenus_mobiliers', 'autres_revenus']
                },
                {
                    'title': 'Charges Déductibles',
                    'fields': ['frais_professionnels', 'pensions_alimentaires', 'dons', 'autres_charges']
                }
            ],
            'required_fields': ['nom', 'prenom', 'numero_fiscal'],
            'filing_deadline': 'Mai 31',
            'estimated_time': '25-35 minutes'
        }
        
        # Add more templates as needed...
    
    def _get_form_template(self, form_type: str, jurisdiction: str) -> Optional[Dict[str, Any]]:
        """Get form template for specific type and jurisdiction"""
        template_key = f"{jurisdiction}_{form_type}"
        return self.form_templates.get(template_key)
    
    async def _generate_pdf_form(self, 
                               template: Dict[str, Any], 
                               user_data: Dict[str, Any], 
                               tax_data: Dict[str, Any], 
                               jurisdiction: str) -> Optional[str]:
        """Generate PDF form using template and data"""
        try:
            # Create temporary file
            output_path = tempfile.mktemp(suffix='.pdf')
            
            # Create PDF document
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=TA_CENTER
            )
            story.append(Paragraph(template['title'], title_style))
            story.append(Spacer(1, 20))
            
            # Form sections
            for section in template.get('sections', []):
                # Section title
                section_style = ParagraphStyle(
                    'SectionTitle',
                    parent=styles['Heading2'],
                    fontSize=14,
                    spaceAfter=10,
                    textColor=colors.darkblue
                )
                story.append(Paragraph(section['title'], section_style))
                
                # Section fields
                field_data = []
                for field in section['fields']:
                    field_label = self._format_field_label(field)
                    field_value = self._get_field_value(field, user_data, tax_data)
                    field_data.append([field_label, field_value])
                
                # Create table for fields
                if field_data:
                    table = Table(field_data, colWidths=[3*inch, 3*inch])
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 12),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    story.append(table)
                    story.append(Spacer(1, 20))
            
            # Tax calculation summary (if available)
            if tax_data:
                story.append(PageBreak())
                story.append(Paragraph("Tax Calculation Summary", title_style))
                story.append(Spacer(1, 20))
                
                calc_data = [
                    ['Total Income', self._format_currency(tax_data.get('total_income', 0))],
                    ['Total Deductions', self._format_currency(tax_data.get('total_deductions', 0))],
                    ['Taxable Income', self._format_currency(tax_data.get('taxable_income', 0))],
                    ['Tax Due', self._format_currency(tax_data.get('tax_due', 0))],
                    ['Tax Paid', self._format_currency(tax_data.get('tax_paid', 0))],
                    ['Balance Due/Refund', self._format_currency(tax_data.get('balance', 0))]
                ]
                
                calc_table = Table(calc_data, colWidths=[3*inch, 2*inch])
                calc_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(calc_table)
            
            # Footer
            story.append(Spacer(1, 40))
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=10,
                alignment=TA_CENTER,
                textColor=colors.grey
            )
            story.append(Paragraph(f"Generated by AI Tax Agent on {datetime.now().strftime('%B %d, %Y')}", footer_style))
            story.append(Paragraph("This form is computer-generated and may require manual review", footer_style))
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"PDF form generated successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            return None
    
    def _format_field_label(self, field: str) -> str:
        """Format field name as human-readable label"""
        return field.replace('_', ' ').title()
    
    def _get_field_value(self, field: str, user_data: Dict[str, Any], tax_data: Dict[str, Any]) -> str:
        """Get field value from user or tax data"""
        # Try user data first
        if field in user_data:
            value = user_data[field]
        # Then try tax data
        elif tax_data and field in tax_data:
            value = tax_data[field]
        else:
            value = ''
        
        # Format value based on type
        if isinstance(value, (int, float)) and 'income' in field.lower():
            return self._format_currency(value)
        elif isinstance(value, bool):
            return 'Yes' if value else 'No'
        else:
            return str(value) if value else ''
    
    def _format_currency(self, amount: float, currency: str = 'EUR') -> str:
        """Format currency amount"""
        if currency == 'EUR':
            return f"€{amount:,.2f}"
        elif currency == 'USD':
            return f"${amount:,.2f}"
        elif currency == 'GBP':
            return f"£{amount:,.2f}"
        else:
            return f"{currency} {amount:,.2f}"
    
    def _validate_field(self, value: Any, validation: Dict[str, Any]) -> bool:
        """Validate field value against validation rules"""
        try:
            field_type = validation.get('type')
            
            if field_type == 'malta_id':
                pattern = validation.get('pattern')
                if pattern:
                    import re
                    return bool(re.match(pattern, str(value)))
            
            elif field_type == 'currency':
                min_val = validation.get('min', 0)
                max_val = validation.get('max', float('inf'))
                return min_val <= float(value) <= max_val
            
            elif field_type == 'email':
                import re
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                return bool(re.match(email_pattern, str(value)))
            
            return True
            
        except Exception:
            return False
    
    def _check_business_rule(self, rule: Dict[str, Any], form_data: Dict[str, Any]) -> bool:
        """Check business rule against form data"""
        try:
            condition = rule.get('condition', '')
            
            # Simple condition evaluation (in production, use a proper expression evaluator)
            if 'total_income > 60000' in condition:
                total_income = form_data.get('total_income', 0)
                return float(total_income) <= 60000
            
            return True
            
        except Exception:
            return True
    
    async def _store_form_metadata(self, 
                                 form_type: str, 
                                 jurisdiction: str, 
                                 user_data: Dict[str, Any], 
                                 pdf_path: str) -> Dict[str, Any]:
        """Store form generation metadata"""
        try:
            supabase = get_supabase_client()
            
            metadata = {
                'form_type': form_type,
                'jurisdiction': jurisdiction,
                'user_id': user_data.get('user_id'),
                'pdf_path': pdf_path,
                'generated_at': datetime.now().isoformat(),
                'status': 'generated'
            }
            
            result = supabase.table('generated_forms').insert(metadata).execute()
            
            if result.data:
                return result.data[0]
            else:
                return metadata
                
        except Exception as e:
            logger.error(f"Failed to store form metadata: {e}")
            return {}

# Global service instance
pdf_form_generator = PDFFormGenerator()

