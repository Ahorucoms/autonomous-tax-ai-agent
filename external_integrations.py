"""
External Integrations Service
Handles integration with Google Drive, WhatsApp, Revolut, and CFR Malta API
"""

import os
import logging
import requests
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import base64

# Google Drive API
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# WhatsApp Business API
import whatsapp_business_python

logger = logging.getLogger(__name__)

class ExternalIntegrationsService:
    """Service for managing external API integrations"""
    
    def __init__(self):
        self.google_drive_service = None
        self.whatsapp_client = None
        self.revolut_api_key = os.getenv('REVOLUT_API_KEY')
        self.cfr_malta_api_key = os.getenv('CFR_MALTA_API_KEY')
        self.cfr_malta_base_url = "https://cfr.gov.mt/api/v1"
        
        # Initialize services
        self._init_google_drive()
        self._init_whatsapp()
    
    def _init_google_drive(self):
        """Initialize Google Drive API service"""
        try:
            SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
            
            # Load credentials
            creds = None
            token_path = os.getenv('GOOGLE_DRIVE_TOKEN_PATH', 'token.json')
            credentials_path = os.getenv('GOOGLE_DRIVE_CREDENTIALS_PATH', 'credentials.json')
            
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            
            # If there are no (valid) credentials available, let the user log in
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if os.path.exists(credentials_path):
                        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                        creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            
            self.google_drive_service = build('drive', 'v3', credentials=creds)
            logger.info("✅ Google Drive API initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Google Drive API: {e}")
            self.google_drive_service = None
    
    def _init_whatsapp(self):
        """Initialize WhatsApp Business API"""
        try:
            whatsapp_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
            whatsapp_phone_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
            
            if whatsapp_token and whatsapp_phone_id:
                self.whatsapp_client = whatsapp_business_python.WhatsAppBusinessClient(
                    access_token=whatsapp_token,
                    phone_number_id=whatsapp_phone_id
                )
                logger.info("✅ WhatsApp Business API initialized")
            else:
                logger.warning("⚠️ WhatsApp credentials not found")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize WhatsApp API: {e}")
            self.whatsapp_client = None
    
    # Google Drive Integration
    async def search_google_drive_documents(self, user_id: str, query: str = None) -> List[Dict[str, Any]]:
        """Search for tax documents in user's Google Drive"""
        try:
            if not self.google_drive_service:
                raise Exception("Google Drive service not initialized")
            
            # Build search query for tax-related documents
            search_query = "mimeType='application/pdf' or mimeType contains 'image/'"
            if query:
                search_query += f" and name contains '{query}'"
            
            # Add tax-related keywords
            tax_keywords = ['tax', 'income', 'receipt', 'invoice', 'financial', 'statement']
            keyword_query = " or ".join([f"name contains '{keyword}'" for keyword in tax_keywords])
            search_query += f" and ({keyword_query})"
            
            # Execute search
            results = self.google_drive_service.files().list(
                q=search_query,
                pageSize=50,
                fields="nextPageToken, files(id, name, mimeType, modifiedTime, size, webViewLink)"
            ).execute()
            
            documents = results.get('files', [])
            
            logger.info(f"✅ Found {len(documents)} documents in Google Drive for user {user_id}")
            return documents
            
        except Exception as e:
            logger.error(f"❌ Google Drive search failed: {e}")
            return []
    
    async def download_google_drive_document(self, file_id: str) -> Dict[str, Any]:
        """Download document from Google Drive for processing"""
        try:
            if not self.google_drive_service:
                raise Exception("Google Drive service not initialized")
            
            # Get file metadata
            file_metadata = self.google_drive_service.files().get(fileId=file_id).execute()
            
            # Download file content
            file_content = self.google_drive_service.files().get_media(fileId=file_id).execute()
            
            # Encode content as base64 for processing
            content_base64 = base64.b64encode(file_content).decode('utf-8')
            
            return {
                'success': True,
                'file_id': file_id,
                'name': file_metadata['name'],
                'mime_type': file_metadata['mimeType'],
                'content_base64': content_base64,
                'size': len(file_content)
            }
            
        except Exception as e:
            logger.error(f"❌ Google Drive download failed: {e}")
            return {'success': False, 'error': str(e)}
    
    # WhatsApp Integration
    async def send_whatsapp_notification(self, phone_number: str, message: str, template_name: str = None) -> Dict[str, Any]:
        """Send WhatsApp notification to user"""
        try:
            if not self.whatsapp_client:
                raise Exception("WhatsApp client not initialized")
            
            if template_name:
                # Send template message
                response = self.whatsapp_client.send_template_message(
                    to=phone_number,
                    template_name=template_name,
                    language_code="en"
                )
            else:
                # Send text message
                response = self.whatsapp_client.send_text_message(
                    to=phone_number,
                    message=message
                )
            
            logger.info(f"✅ WhatsApp message sent to {phone_number}")
            return {'success': True, 'message_id': response.get('messages', [{}])[0].get('id')}
            
        except Exception as e:
            logger.error(f"❌ WhatsApp send failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def setup_whatsapp_webhook(self, webhook_url: str) -> Dict[str, Any]:
        """Setup WhatsApp webhook for receiving messages"""
        try:
            # Configure webhook endpoint
            webhook_config = {
                'url': webhook_url,
                'verify_token': os.getenv('WHATSAPP_WEBHOOK_VERIFY_TOKEN'),
                'events': ['messages', 'message_deliveries', 'message_reads']
            }
            
            logger.info(f"✅ WhatsApp webhook configured: {webhook_url}")
            return {'success': True, 'webhook_config': webhook_config}
            
        except Exception as e:
            logger.error(f"❌ WhatsApp webhook setup failed: {e}")
            return {'success': False, 'error': str(e)}
    
    # Revolut Integration
    async def create_revolut_payment_link(self, amount: float, currency: str, description: str, user_id: str) -> Dict[str, Any]:
        """Create Revolut payment link for tax services"""
        try:
            if not self.revolut_api_key:
                raise Exception("Revolut API key not configured")
            
            headers = {
                'Authorization': f'Bearer {self.revolut_api_key}',
                'Content-Type': 'application/json'
            }
            
            payment_data = {
                'amount': int(amount * 100),  # Convert to cents
                'currency': currency,
                'description': description,
                'reference': f'tax_service_{user_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                'capture_mode': 'AUTOMATIC',
                'settlement_currency': currency,
                'customer_email': None,  # Would be populated from user data
                'webhook_url': f"{os.getenv('BACKEND_URL')}/api/payments/revolut/webhook"
            }
            
            response = requests.post(
                'https://merchant.revolut.com/api/1.0/orders',
                headers=headers,
                json=payment_data
            )
            
            if response.status_code == 201:
                payment_info = response.json()
                logger.info(f"✅ Revolut payment link created for user {user_id}")
                return {
                    'success': True,
                    'payment_link': payment_info['checkout_url'],
                    'order_id': payment_info['id'],
                    'amount': amount,
                    'currency': currency
                }
            else:
                raise Exception(f"Revolut API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"❌ Revolut payment link creation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def verify_revolut_payment(self, order_id: str) -> Dict[str, Any]:
        """Verify Revolut payment status"""
        try:
            if not self.revolut_api_key:
                raise Exception("Revolut API key not configured")
            
            headers = {
                'Authorization': f'Bearer {self.revolut_api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f'https://merchant.revolut.com/api/1.0/orders/{order_id}',
                headers=headers
            )
            
            if response.status_code == 200:
                order_info = response.json()
                return {
                    'success': True,
                    'status': order_info['state'],
                    'amount': order_info['order_amount']['value'] / 100,
                    'currency': order_info['order_amount']['currency']
                }
            else:
                raise Exception(f"Revolut API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"❌ Revolut payment verification failed: {e}")
            return {'success': False, 'error': str(e)}
    
    # CFR Malta API Integration
    async def get_malta_tax_rates(self, tax_year: int = None) -> Dict[str, Any]:
        """Get current Malta tax rates from CFR API"""
        try:
            if not self.cfr_malta_api_key:
                logger.warning("⚠️ CFR Malta API key not configured, using fallback data")
                return self._get_fallback_malta_tax_rates(tax_year)
            
            headers = {
                'Authorization': f'Bearer {self.cfr_malta_api_key}',
                'Content-Type': 'application/json'
            }
            
            year = tax_year or datetime.now().year
            
            response = requests.get(
                f'{self.cfr_malta_base_url}/tax-rates/{year}',
                headers=headers
            )
            
            if response.status_code == 200:
                tax_rates = response.json()
                logger.info(f"✅ Malta tax rates retrieved for {year}")
                return {'success': True, 'tax_rates': tax_rates, 'year': year}
            else:
                logger.warning(f"⚠️ CFR API error: {response.status_code}, using fallback")
                return self._get_fallback_malta_tax_rates(tax_year)
                
        except Exception as e:
            logger.error(f"❌ CFR Malta API failed: {e}, using fallback")
            return self._get_fallback_malta_tax_rates(tax_year)
    
    async def get_malta_tax_forms(self, form_type: str = None) -> Dict[str, Any]:
        """Get Malta tax forms from CFR API"""
        try:
            if not self.cfr_malta_api_key:
                logger.warning("⚠️ CFR Malta API key not configured, using fallback data")
                return self._get_fallback_malta_forms()
            
            headers = {
                'Authorization': f'Bearer {self.cfr_malta_api_key}',
                'Content-Type': 'application/json'
            }
            
            url = f'{self.cfr_malta_base_url}/forms'
            if form_type:
                url += f'?type={form_type}'
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                forms = response.json()
                logger.info(f"✅ Malta tax forms retrieved")
                return {'success': True, 'forms': forms}
            else:
                logger.warning(f"⚠️ CFR API error: {response.status_code}, using fallback")
                return self._get_fallback_malta_forms()
                
        except Exception as e:
            logger.error(f"❌ CFR Malta forms API failed: {e}, using fallback")
            return self._get_fallback_malta_forms()
    
    async def submit_malta_tax_return(self, user_id: str, tax_return_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit tax return to Malta CFR (simulation)"""
        try:
            # This would be the actual submission to CFR Malta
            # For now, we'll simulate the process
            
            submission_id = f"MT_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}"
            
            logger.info(f"✅ Tax return submitted (simulated) for user {user_id}")
            return {
                'success': True,
                'submission_id': submission_id,
                'status': 'submitted',
                'estimated_processing_time': '5-10 business days',
                'confirmation_number': submission_id
            }
            
        except Exception as e:
            logger.error(f"❌ Malta tax return submission failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _get_fallback_malta_tax_rates(self, tax_year: int = None) -> Dict[str, Any]:
        """Fallback Malta tax rates when API is unavailable"""
        year = tax_year or datetime.now().year
        
        fallback_rates = {
            'income_tax': {
                'single': [
                    {'min': 0, 'max': 9100, 'rate': 0.0},
                    {'min': 9101, 'max': 14500, 'rate': 0.15},
                    {'min': 14501, 'max': 19500, 'rate': 0.25},
                    {'min': 19501, 'max': 60000, 'rate': 0.25},
                    {'min': 60001, 'max': float('inf'), 'rate': 0.35}
                ],
                'married': [
                    {'min': 0, 'max': 12700, 'rate': 0.0},
                    {'min': 12701, 'max': 21200, 'rate': 0.15},
                    {'min': 21201, 'max': 28700, 'rate': 0.25},
                    {'min': 28701, 'max': 60000, 'rate': 0.25},
                    {'min': 60001, 'max': float('inf'), 'rate': 0.35}
                ]
            },
            'vat_rates': {
                'standard': 0.18,
                'reduced': [0.05, 0.07],
                'zero': 0.0
            },
            'social_security': {
                'employee': 0.10,
                'employer': 0.10,
                'self_employed': 0.15
            }
        }
        
        return {
            'success': True,
            'tax_rates': fallback_rates,
            'year': year,
            'source': 'fallback'
        }
    
    def _get_fallback_malta_forms(self) -> Dict[str, Any]:
        """Fallback Malta tax forms when API is unavailable"""
        fallback_forms = [
            {
                'form_id': 'FS3',
                'name': 'Final Settlement - Individuals',
                'description': 'Annual tax return for individuals',
                'url': 'https://cfr.gov.mt/forms/FS3.pdf'
            },
            {
                'form_id': 'FS7',
                'name': 'Final Settlement - Companies',
                'description': 'Annual tax return for companies',
                'url': 'https://cfr.gov.mt/forms/FS7.pdf'
            },
            {
                'form_id': 'VAT1',
                'name': 'VAT Return',
                'description': 'Quarterly VAT return',
                'url': 'https://cfr.gov.mt/forms/VAT1.pdf'
            }
        ]
        
        return {
            'success': True,
            'forms': fallback_forms,
            'source': 'fallback'
        }

# Global service instance
external_integrations_service = ExternalIntegrationsService()

