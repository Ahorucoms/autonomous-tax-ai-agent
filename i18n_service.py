"""
Internationalization (i18n) Service for Malta Tax AI Agent
Multilingual support and localization capabilities
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid
from enum import Enum

class SupportedLanguage(Enum):
    ENGLISH = "en"
    MALTESE = "mt"
    ITALIAN = "it"
    FRENCH = "fr"
    GERMAN = "de"
    SPANISH = "es"
    ARABIC = "ar"

class TextDirection(Enum):
    LTR = "ltr"  # Left-to-right
    RTL = "rtl"  # Right-to-left

class I18nService:
    """Internationalization service for Malta Tax AI Agent"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Translation storage
        self.translations = {}
        self.language_configs = {}
        self.user_preferences = {}
        
        # Initialize supported languages and translations
        self._initialize_languages()
        self._initialize_translations()
    
    def _initialize_languages(self):
        """Initialize supported language configurations"""
        self.language_configs = {
            SupportedLanguage.ENGLISH.value: {
                'code': 'en',
                'name': 'English',
                'native_name': 'English',
                'direction': TextDirection.LTR.value,
                'locale': 'en-US',
                'currency': 'EUR',
                'date_format': 'MM/DD/YYYY',
                'time_format': '12h',
                'decimal_separator': '.',
                'thousands_separator': ',',
                'is_default': True,
                'is_official_malta': True,
                'flag_emoji': '🇬🇧',
                'completion_percentage': 100
            },
            SupportedLanguage.MALTESE.value: {
                'code': 'mt',
                'name': 'Maltese',
                'native_name': 'Malti',
                'direction': TextDirection.LTR.value,
                'locale': 'mt-MT',
                'currency': 'EUR',
                'date_format': 'DD/MM/YYYY',
                'time_format': '24h',
                'decimal_separator': '.',
                'thousands_separator': ',',
                'is_default': False,
                'is_official_malta': True,
                'flag_emoji': '🇲🇹',
                'completion_percentage': 85
            },
            SupportedLanguage.ITALIAN.value: {
                'code': 'it',
                'name': 'Italian',
                'native_name': 'Italiano',
                'direction': TextDirection.LTR.value,
                'locale': 'it-IT',
                'currency': 'EUR',
                'date_format': 'DD/MM/YYYY',
                'time_format': '24h',
                'decimal_separator': ',',
                'thousands_separator': '.',
                'is_default': False,
                'is_official_malta': False,
                'flag_emoji': '🇮🇹',
                'completion_percentage': 75
            },
            SupportedLanguage.FRENCH.value: {
                'code': 'fr',
                'name': 'French',
                'native_name': 'Français',
                'direction': TextDirection.LTR.value,
                'locale': 'fr-FR',
                'currency': 'EUR',
                'date_format': 'DD/MM/YYYY',
                'time_format': '24h',
                'decimal_separator': ',',
                'thousands_separator': ' ',
                'is_default': False,
                'is_official_malta': False,
                'flag_emoji': '🇫🇷',
                'completion_percentage': 70
            },
            SupportedLanguage.GERMAN.value: {
                'code': 'de',
                'name': 'German',
                'native_name': 'Deutsch',
                'direction': TextDirection.LTR.value,
                'locale': 'de-DE',
                'currency': 'EUR',
                'date_format': 'DD.MM.YYYY',
                'time_format': '24h',
                'decimal_separator': ',',
                'thousands_separator': '.',
                'is_default': False,
                'is_official_malta': False,
                'flag_emoji': '🇩🇪',
                'completion_percentage': 65
            },
            SupportedLanguage.SPANISH.value: {
                'code': 'es',
                'name': 'Spanish',
                'native_name': 'Español',
                'direction': TextDirection.LTR.value,
                'locale': 'es-ES',
                'currency': 'EUR',
                'date_format': 'DD/MM/YYYY',
                'time_format': '24h',
                'decimal_separator': ',',
                'thousands_separator': '.',
                'is_default': False,
                'is_official_malta': False,
                'flag_emoji': '🇪🇸',
                'completion_percentage': 60
            },
            SupportedLanguage.ARABIC.value: {
                'code': 'ar',
                'name': 'Arabic',
                'native_name': 'العربية',
                'direction': TextDirection.RTL.value,
                'locale': 'ar-SA',
                'currency': 'EUR',
                'date_format': 'DD/MM/YYYY',
                'time_format': '12h',
                'decimal_separator': '.',
                'thousands_separator': ',',
                'is_default': False,
                'is_official_malta': False,
                'flag_emoji': '🇸🇦',
                'completion_percentage': 50
            }
        }
    
    def _initialize_translations(self):
        """Initialize base translations for all supported languages"""
        
        # English (base language)
        self.translations['en'] = {
            # Common UI elements
            'common': {
                'welcome': 'Welcome',
                'login': 'Login',
                'logout': 'Logout',
                'register': 'Register',
                'submit': 'Submit',
                'cancel': 'Cancel',
                'save': 'Save',
                'delete': 'Delete',
                'edit': 'Edit',
                'view': 'View',
                'search': 'Search',
                'filter': 'Filter',
                'sort': 'Sort',
                'loading': 'Loading...',
                'error': 'Error',
                'success': 'Success',
                'warning': 'Warning',
                'info': 'Information',
                'yes': 'Yes',
                'no': 'No',
                'ok': 'OK',
                'close': 'Close',
                'back': 'Back',
                'next': 'Next',
                'previous': 'Previous',
                'home': 'Home',
                'dashboard': 'Dashboard',
                'settings': 'Settings',
                'profile': 'Profile',
                'help': 'Help',
                'about': 'About',
                'contact': 'Contact',
                'privacy': 'Privacy',
                'terms': 'Terms of Service'
            },
            
            # Tax-specific terms
            'tax': {
                'income_tax': 'Income Tax',
                'corporate_tax': 'Corporate Tax',
                'vat': 'VAT',
                'social_security': 'Social Security',
                'stamp_duty': 'Stamp Duty',
                'capital_gains': 'Capital Gains',
                'tax_return': 'Tax Return',
                'filing': 'Filing',
                'deadline': 'Deadline',
                'penalty': 'Penalty',
                'refund': 'Refund',
                'payment': 'Payment',
                'calculation': 'Calculation',
                'compliance': 'Compliance',
                'audit': 'Audit',
                'deduction': 'Deduction',
                'allowance': 'Allowance',
                'exemption': 'Exemption',
                'rate': 'Rate',
                'bracket': 'Bracket',
                'threshold': 'Threshold'
            },
            
            # Malta-specific terms
            'malta': {
                'cfr': 'Commissioner for Revenue',
                'malta_government': 'Malta Government',
                'maltese_citizen': 'Maltese Citizen',
                'eu_citizen': 'EU Citizen',
                'third_country_national': 'Third Country National',
                'residence_permit': 'Residence Permit',
                'work_permit': 'Work Permit',
                'malta_tax_number': 'Malta Tax Number',
                'id_card': 'ID Card',
                'passport': 'Passport'
            },
            
            # Form labels
            'forms': {
                'personal_details': 'Personal Details',
                'contact_information': 'Contact Information',
                'tax_information': 'Tax Information',
                'employment_details': 'Employment Details',
                'income_details': 'Income Details',
                'expense_details': 'Expense Details',
                'document_upload': 'Document Upload',
                'declaration': 'Declaration',
                'signature': 'Signature',
                'date': 'Date',
                'amount': 'Amount',
                'currency': 'Currency',
                'percentage': 'Percentage',
                'description': 'Description',
                'category': 'Category',
                'type': 'Type',
                'status': 'Status'
            },
            
            # Messages
            'messages': {
                'welcome_message': 'Welcome to Malta Tax AI Agent',
                'login_success': 'Login successful',
                'login_failed': 'Login failed',
                'logout_success': 'Logout successful',
                'save_success': 'Saved successfully',
                'save_failed': 'Save failed',
                'delete_success': 'Deleted successfully',
                'delete_failed': 'Delete failed',
                'validation_error': 'Please check your input',
                'network_error': 'Network error occurred',
                'server_error': 'Server error occurred',
                'not_found': 'Not found',
                'unauthorized': 'Unauthorized access',
                'forbidden': 'Access forbidden',
                'session_expired': 'Session expired',
                'file_upload_success': 'File uploaded successfully',
                'file_upload_failed': 'File upload failed',
                'calculation_complete': 'Calculation completed',
                'filing_submitted': 'Filing submitted successfully',
                'payment_processed': 'Payment processed successfully'
            }
        }
        
        # Maltese translations
        self.translations['mt'] = {
            'common': {
                'welcome': 'Merħba',
                'login': 'Idħol',
                'logout': 'Oħroġ',
                'register': 'Irreġistra',
                'submit': 'Ibgħat',
                'cancel': 'Ikkanċella',
                'save': 'Ħażen',
                'delete': 'Ħassar',
                'edit': 'Editja',
                'view': 'Ara',
                'search': 'Fittex',
                'filter': 'Filtru',
                'sort': 'Issortja',
                'loading': 'Qed jitgħabba...',
                'error': 'Żball',
                'success': 'Suċċess',
                'warning': 'Twissija',
                'info': 'Informazzjoni',
                'yes': 'Iva',
                'no': 'Le',
                'ok': 'OK',
                'close': 'Agħlaq',
                'back': 'Lura',
                'next': 'Li jmiss',
                'previous': 'Ta\' qabel',
                'home': 'Dar',
                'dashboard': 'Dashboard',
                'settings': 'Settings',
                'profile': 'Profil',
                'help': 'Għajnuna',
                'about': 'Dwar',
                'contact': 'Kuntatt',
                'privacy': 'Privatezza',
                'terms': 'Termini tas-Servizz'
            },
            'tax': {
                'income_tax': 'Taxxa fuq id-Dħul',
                'corporate_tax': 'Taxxa Korporattiva',
                'vat': 'VAT',
                'social_security': 'Sigurtà Soċjali',
                'stamp_duty': 'Dazju tal-Bolli',
                'capital_gains': 'Qligħ fuq il-Kapital',
                'tax_return': 'Ritorn tat-Taxxa',
                'filing': 'Preżentazzjoni',
                'deadline': 'Skadenza',
                'penalty': 'Penali',
                'refund': 'Rifużjoni',
                'payment': 'Ħlas',
                'calculation': 'Kalkolu',
                'compliance': 'Konformità',
                'audit': 'Verifika',
                'deduction': 'Tnaqqis',
                'allowance': 'Allowance',
                'exemption': 'Eżenzjoni',
                'rate': 'Rata',
                'bracket': 'Bracket',
                'threshold': 'Limitu'
            }
        }
        
        # Italian translations
        self.translations['it'] = {
            'common': {
                'welcome': 'Benvenuto',
                'login': 'Accedi',
                'logout': 'Esci',
                'register': 'Registrati',
                'submit': 'Invia',
                'cancel': 'Annulla',
                'save': 'Salva',
                'delete': 'Elimina',
                'edit': 'Modifica',
                'view': 'Visualizza',
                'search': 'Cerca',
                'filter': 'Filtro',
                'sort': 'Ordina',
                'loading': 'Caricamento...',
                'error': 'Errore',
                'success': 'Successo',
                'warning': 'Avviso',
                'info': 'Informazione',
                'yes': 'Sì',
                'no': 'No',
                'ok': 'OK',
                'close': 'Chiudi',
                'back': 'Indietro',
                'next': 'Avanti',
                'previous': 'Precedente',
                'home': 'Home',
                'dashboard': 'Dashboard',
                'settings': 'Impostazioni',
                'profile': 'Profilo',
                'help': 'Aiuto',
                'about': 'Informazioni',
                'contact': 'Contatto',
                'privacy': 'Privacy',
                'terms': 'Termini di Servizio'
            },
            'tax': {
                'income_tax': 'Imposta sul Reddito',
                'corporate_tax': 'Imposta Societaria',
                'vat': 'IVA',
                'social_security': 'Sicurezza Sociale',
                'stamp_duty': 'Imposta di Bollo',
                'capital_gains': 'Plusvalenze',
                'tax_return': 'Dichiarazione dei Redditi',
                'filing': 'Presentazione',
                'deadline': 'Scadenza',
                'penalty': 'Penale',
                'refund': 'Rimborso',
                'payment': 'Pagamento',
                'calculation': 'Calcolo',
                'compliance': 'Conformità',
                'audit': 'Audit',
                'deduction': 'Deduzione',
                'allowance': 'Indennità',
                'exemption': 'Esenzione',
                'rate': 'Aliquota',
                'bracket': 'Scaglione',
                'threshold': 'Soglia'
            }
        }
        
        # French translations
        self.translations['fr'] = {
            'common': {
                'welcome': 'Bienvenue',
                'login': 'Connexion',
                'logout': 'Déconnexion',
                'register': 'S\'inscrire',
                'submit': 'Soumettre',
                'cancel': 'Annuler',
                'save': 'Enregistrer',
                'delete': 'Supprimer',
                'edit': 'Modifier',
                'view': 'Voir',
                'search': 'Rechercher',
                'filter': 'Filtrer',
                'sort': 'Trier',
                'loading': 'Chargement...',
                'error': 'Erreur',
                'success': 'Succès',
                'warning': 'Avertissement',
                'info': 'Information',
                'yes': 'Oui',
                'no': 'Non',
                'ok': 'OK',
                'close': 'Fermer',
                'back': 'Retour',
                'next': 'Suivant',
                'previous': 'Précédent',
                'home': 'Accueil',
                'dashboard': 'Tableau de bord',
                'settings': 'Paramètres',
                'profile': 'Profil',
                'help': 'Aide',
                'about': 'À propos',
                'contact': 'Contact',
                'privacy': 'Confidentialité',
                'terms': 'Conditions de Service'
            },
            'tax': {
                'income_tax': 'Impôt sur le Revenu',
                'corporate_tax': 'Impôt des Sociétés',
                'vat': 'TVA',
                'social_security': 'Sécurité Sociale',
                'stamp_duty': 'Droit de Timbre',
                'capital_gains': 'Plus-values',
                'tax_return': 'Déclaration d\'Impôts',
                'filing': 'Dépôt',
                'deadline': 'Date Limite',
                'penalty': 'Pénalité',
                'refund': 'Remboursement',
                'payment': 'Paiement',
                'calculation': 'Calcul',
                'compliance': 'Conformité',
                'audit': 'Audit',
                'deduction': 'Déduction',
                'allowance': 'Allocation',
                'exemption': 'Exemption',
                'rate': 'Taux',
                'bracket': 'Tranche',
                'threshold': 'Seuil'
            }
        }
        
        # German translations
        self.translations['de'] = {
            'common': {
                'welcome': 'Willkommen',
                'login': 'Anmelden',
                'logout': 'Abmelden',
                'register': 'Registrieren',
                'submit': 'Senden',
                'cancel': 'Abbrechen',
                'save': 'Speichern',
                'delete': 'Löschen',
                'edit': 'Bearbeiten',
                'view': 'Anzeigen',
                'search': 'Suchen',
                'filter': 'Filter',
                'sort': 'Sortieren',
                'loading': 'Laden...',
                'error': 'Fehler',
                'success': 'Erfolg',
                'warning': 'Warnung',
                'info': 'Information',
                'yes': 'Ja',
                'no': 'Nein',
                'ok': 'OK',
                'close': 'Schließen',
                'back': 'Zurück',
                'next': 'Weiter',
                'previous': 'Vorherige',
                'home': 'Startseite',
                'dashboard': 'Dashboard',
                'settings': 'Einstellungen',
                'profile': 'Profil',
                'help': 'Hilfe',
                'about': 'Über',
                'contact': 'Kontakt',
                'privacy': 'Datenschutz',
                'terms': 'Nutzungsbedingungen'
            },
            'tax': {
                'income_tax': 'Einkommensteuer',
                'corporate_tax': 'Körperschaftsteuer',
                'vat': 'Mehrwertsteuer',
                'social_security': 'Sozialversicherung',
                'stamp_duty': 'Stempelsteuer',
                'capital_gains': 'Kapitalerträge',
                'tax_return': 'Steuererklärung',
                'filing': 'Einreichung',
                'deadline': 'Frist',
                'penalty': 'Strafe',
                'refund': 'Erstattung',
                'payment': 'Zahlung',
                'calculation': 'Berechnung',
                'compliance': 'Compliance',
                'audit': 'Prüfung',
                'deduction': 'Abzug',
                'allowance': 'Freibetrag',
                'exemption': 'Befreiung',
                'rate': 'Satz',
                'bracket': 'Stufe',
                'threshold': 'Schwelle'
            }
        }
    
    def get_supported_languages(self) -> Dict[str, Any]:
        """Get all supported languages with their configurations"""
        try:
            return {
                'success': True,
                'languages': self.language_configs,
                'total_count': len(self.language_configs)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting supported languages: {str(e)}")
            raise ValueError(f"Supported languages retrieval failed: {str(e)}")
    
    def get_translation(self, language_code: str, key: str, category: str = None) -> Dict[str, Any]:
        """Get a specific translation"""
        try:
            if language_code not in self.translations:
                # Fallback to English
                language_code = 'en'
            
            translations = self.translations[language_code]
            
            if category:
                if category in translations and key in translations[category]:
                    return {
                        'success': True,
                        'translation': translations[category][key],
                        'language': language_code,
                        'key': key,
                        'category': category
                    }
            else:
                # Search across all categories
                for cat, cat_translations in translations.items():
                    if key in cat_translations:
                        return {
                            'success': True,
                            'translation': cat_translations[key],
                            'language': language_code,
                            'key': key,
                            'category': cat
                        }
            
            # Return key if translation not found
            return {
                'success': False,
                'translation': key,
                'language': language_code,
                'key': key,
                'category': category,
                'error': 'Translation not found'
            }
            
        except Exception as e:
            self.logger.error(f"Error getting translation: {str(e)}")
            raise ValueError(f"Translation retrieval failed: {str(e)}")
    
    def get_translations(self, language_code: str, category: str = None) -> Dict[str, Any]:
        """Get translations for a language, optionally filtered by category"""
        try:
            if language_code not in self.translations:
                return {
                    'success': False,
                    'error': f'Language {language_code} not supported'
                }
            
            translations = self.translations[language_code]
            
            if category:
                if category in translations:
                    return {
                        'success': True,
                        'translations': translations[category],
                        'language': language_code,
                        'category': category
                    }
                else:
                    return {
                        'success': False,
                        'error': f'Category {category} not found'
                    }
            else:
                return {
                    'success': True,
                    'translations': translations,
                    'language': language_code
                }
            
        except Exception as e:
            self.logger.error(f"Error getting translations: {str(e)}")
            raise ValueError(f"Translations retrieval failed: {str(e)}")
    
    def add_translation(self, language_code: str, key: str, value: str, category: str = 'custom') -> Dict[str, Any]:
        """Add or update a translation"""
        try:
            if language_code not in self.translations:
                self.translations[language_code] = {}
            
            if category not in self.translations[language_code]:
                self.translations[language_code][category] = {}
            
            self.translations[language_code][category][key] = value
            
            return {
                'success': True,
                'message': 'Translation added successfully',
                'language': language_code,
                'key': key,
                'value': value,
                'category': category
            }
            
        except Exception as e:
            self.logger.error(f"Error adding translation: {str(e)}")
            raise ValueError(f"Translation addition failed: {str(e)}")
    
    def detect_language(self, text: str) -> Dict[str, Any]:
        """Detect language from text (simplified implementation)"""
        try:
            # Simple language detection based on common words
            # In production, this would use a proper language detection library
            
            language_indicators = {
                'en': ['the', 'and', 'is', 'in', 'to', 'of', 'a', 'that', 'it', 'with'],
                'mt': ['u', 'li', 'ta\'', 'fil', 'għal', 'minn', 'ma\'', 'jew', 'bħal', 'wara'],
                'it': ['il', 'di', 'che', 'e', 'la', 'per', 'in', 'un', 'è', 'con'],
                'fr': ['le', 'de', 'et', 'à', 'un', 'il', 'être', 'et', 'en', 'avoir'],
                'de': ['der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit', 'sich'],
                'es': ['el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'ser', 'se'],
                'ar': ['في', 'من', 'إلى', 'على', 'هذا', 'هذه', 'التي', 'الذي', 'كان', 'كانت']
            }
            
            text_lower = text.lower()
            scores = {}
            
            for lang, indicators in language_indicators.items():
                score = 0
                for indicator in indicators:
                    score += text_lower.count(indicator)
                scores[lang] = score
            
            # Get the language with highest score
            detected_lang = max(scores, key=scores.get) if scores else 'en'
            confidence = scores[detected_lang] / len(text.split()) if text.split() else 0
            
            return {
                'success': True,
                'detected_language': detected_lang,
                'confidence': min(confidence, 1.0),
                'all_scores': scores
            }
            
        except Exception as e:
            self.logger.error(f"Error detecting language: {str(e)}")
            return {
                'success': False,
                'detected_language': 'en',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def set_user_language_preference(self, user_id: str, language_code: str) -> Dict[str, Any]:
        """Set language preference for a user"""
        try:
            if language_code not in self.language_configs:
                return {
                    'success': False,
                    'error': f'Language {language_code} not supported'
                }
            
            self.user_preferences[user_id] = {
                'language': language_code,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            return {
                'success': True,
                'message': 'Language preference updated',
                'user_id': user_id,
                'language': language_code
            }
            
        except Exception as e:
            self.logger.error(f"Error setting user language preference: {str(e)}")
            raise ValueError(f"Language preference setting failed: {str(e)}")
    
    def get_user_language_preference(self, user_id: str) -> Dict[str, Any]:
        """Get language preference for a user"""
        try:
            if user_id in self.user_preferences:
                return {
                    'success': True,
                    'language': self.user_preferences[user_id]['language'],
                    'updated_at': self.user_preferences[user_id]['updated_at']
                }
            else:
                # Return default language
                return {
                    'success': True,
                    'language': 'en',
                    'is_default': True
                }
            
        except Exception as e:
            self.logger.error(f"Error getting user language preference: {str(e)}")
            raise ValueError(f"Language preference retrieval failed: {str(e)}")
    
    def format_number(self, number: float, language_code: str) -> Dict[str, Any]:
        """Format a number according to language locale"""
        try:
            if language_code not in self.language_configs:
                language_code = 'en'
            
            config = self.language_configs[language_code]
            decimal_sep = config['decimal_separator']
            thousands_sep = config['thousands_separator']
            
            # Split number into integer and decimal parts
            parts = f"{number:.2f}".split('.')
            integer_part = parts[0]
            decimal_part = parts[1]
            
            # Add thousands separators
            if len(integer_part) > 3:
                formatted_integer = ''
                for i, digit in enumerate(reversed(integer_part)):
                    if i > 0 and i % 3 == 0:
                        formatted_integer = thousands_sep + formatted_integer
                    formatted_integer = digit + formatted_integer
            else:
                formatted_integer = integer_part
            
            # Combine with decimal part
            formatted_number = formatted_integer + decimal_sep + decimal_part
            
            return {
                'success': True,
                'formatted_number': formatted_number,
                'language': language_code
            }
            
        except Exception as e:
            self.logger.error(f"Error formatting number: {str(e)}")
            return {
                'success': False,
                'formatted_number': str(number),
                'error': str(e)
            }
    
    def format_currency(self, amount: float, language_code: str, currency: str = 'EUR') -> Dict[str, Any]:
        """Format currency according to language locale"""
        try:
            if language_code not in self.language_configs:
                language_code = 'en'
            
            # Format the number first
            number_result = self.format_number(amount, language_code)
            formatted_amount = number_result['formatted_number']
            
            # Add currency symbol based on language
            currency_symbols = {
                'EUR': '€',
                'USD': '$',
                'GBP': '£'
            }
            
            symbol = currency_symbols.get(currency, currency)
            
            # Currency placement varies by language
            if language_code in ['en']:
                formatted_currency = f"{symbol}{formatted_amount}"
            else:
                formatted_currency = f"{formatted_amount} {symbol}"
            
            return {
                'success': True,
                'formatted_currency': formatted_currency,
                'language': language_code,
                'currency': currency
            }
            
        except Exception as e:
            self.logger.error(f"Error formatting currency: {str(e)}")
            return {
                'success': False,
                'formatted_currency': f"{amount} {currency}",
                'error': str(e)
            }
    
    def format_date(self, date_str: str, language_code: str) -> Dict[str, Any]:
        """Format date according to language locale"""
        try:
            if language_code not in self.language_configs:
                language_code = 'en'
            
            config = self.language_configs[language_code]
            date_format = config['date_format']
            
            # Parse the input date (assuming ISO format)
            from datetime import datetime
            try:
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            
            # Format according to language preference
            if date_format == 'DD/MM/YYYY':
                formatted_date = date_obj.strftime('%d/%m/%Y')
            elif date_format == 'MM/DD/YYYY':
                formatted_date = date_obj.strftime('%m/%d/%Y')
            elif date_format == 'DD.MM.YYYY':
                formatted_date = date_obj.strftime('%d.%m.%Y')
            else:
                formatted_date = date_obj.strftime('%Y-%m-%d')
            
            return {
                'success': True,
                'formatted_date': formatted_date,
                'language': language_code,
                'format': date_format
            }
            
        except Exception as e:
            self.logger.error(f"Error formatting date: {str(e)}")
            return {
                'success': False,
                'formatted_date': date_str,
                'error': str(e)
            }
    
    def get_language_config(self, language_code: str) -> Dict[str, Any]:
        """Get configuration for a specific language"""
        try:
            if language_code not in self.language_configs:
                return {
                    'success': False,
                    'error': f'Language {language_code} not supported'
                }
            
            return {
                'success': True,
                'language_config': self.language_configs[language_code]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting language config: {str(e)}")
            raise ValueError(f"Language config retrieval failed: {str(e)}")
    
    def get_translation_completeness(self) -> Dict[str, Any]:
        """Get translation completeness statistics"""
        try:
            base_lang = 'en'
            base_translations = self.translations[base_lang]
            
            # Count total keys in base language
            total_keys = 0
            for category in base_translations.values():
                total_keys += len(category)
            
            completeness = {}
            
            for lang_code in self.translations:
                if lang_code == base_lang:
                    completeness[lang_code] = 100.0
                    continue
                
                translated_keys = 0
                lang_translations = self.translations[lang_code]
                
                for cat_name, cat_translations in base_translations.items():
                    if cat_name in lang_translations:
                        for key in cat_translations:
                            if key in lang_translations[cat_name]:
                                translated_keys += 1
                
                percentage = (translated_keys / total_keys * 100) if total_keys > 0 else 0
                completeness[lang_code] = round(percentage, 1)
            
            return {
                'success': True,
                'completeness': completeness,
                'total_keys': total_keys,
                'base_language': base_lang
            }
            
        except Exception as e:
            self.logger.error(f"Error getting translation completeness: {str(e)}")
            raise ValueError(f"Translation completeness calculation failed: {str(e)}")

