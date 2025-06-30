"""
Malta Tax Compliance and Validation Engine
Handles compliance checking, deadline tracking, penalty calculations, and audit trails
"""

from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, List, Any, Optional, Tuple
import json
import logging
from enum import Enum
import uuid

class ComplianceStatus(Enum):
    COMPLIANT = "compliant"
    WARNING = "warning"
    NON_COMPLIANT = "non_compliant"
    OVERDUE = "overdue"

class PenaltyType(Enum):
    LATE_FILING = "late_filing"
    LATE_PAYMENT = "late_payment"
    INCORRECT_FILING = "incorrect_filing"
    FAILURE_TO_FILE = "failure_to_file"

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class MaltaComplianceEngine:
    """Malta tax compliance and validation engine"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Malta tax deadlines and requirements
        self.tax_deadlines = self._initialize_tax_deadlines()
        self.penalty_rates = self._initialize_penalty_rates()
        self.compliance_rules = self._initialize_compliance_rules()
        
        # Storage for compliance records
        self.compliance_records = {}
        self.audit_logs = {}
        self.alerts = {}
    
    def _initialize_tax_deadlines(self) -> Dict[str, Any]:
        """Initialize Malta tax deadlines"""
        return {
            "income_tax": {
                "individual": {
                    "filing_deadline": "June 30",
                    "payment_deadline": "June 30",
                    "description": "Individual income tax return (FS5)",
                    "frequency": "annual"
                },
                "corporate": {
                    "filing_deadline": "9 months after year end",
                    "payment_deadline": "9 months after year end",
                    "description": "Corporate income tax return",
                    "frequency": "annual"
                }
            },
            "vat": {
                "monthly": {
                    "filing_deadline": "15th of following month",
                    "payment_deadline": "15th of following month",
                    "description": "Monthly VAT return",
                    "frequency": "monthly"
                },
                "quarterly": {
                    "filing_deadline": "15th of month following quarter end",
                    "payment_deadline": "15th of month following quarter end",
                    "description": "Quarterly VAT return",
                    "frequency": "quarterly"
                }
            },
            "social_security": {
                "class1": {
                    "filing_deadline": "15th of following month",
                    "payment_deadline": "15th of following month",
                    "description": "Class 1 Social Security contributions",
                    "frequency": "monthly"
                },
                "class2": {
                    "filing_deadline": "January 31",
                    "payment_deadline": "January 31",
                    "description": "Class 2 Social Security contributions",
                    "frequency": "annual"
                }
            },
            "withholding_tax": {
                "employment": {
                    "filing_deadline": "15th of following month",
                    "payment_deadline": "15th of following month",
                    "description": "Employment withholding tax",
                    "frequency": "monthly"
                }
            }
        }
    
    def _initialize_penalty_rates(self) -> Dict[str, Any]:
        """Initialize Malta penalty rates"""
        return {
            "late_filing": {
                "income_tax": {
                    "base_penalty": 23.29,  # EUR
                    "daily_penalty": 2.33,  # EUR per day
                    "max_penalty": 232.94   # EUR
                },
                "vat": {
                    "base_penalty": 46.59,  # EUR
                    "daily_penalty": 4.66,  # EUR per day
                    "max_penalty": 465.87   # EUR
                },
                "social_security": {
                    "base_penalty": 23.29,  # EUR
                    "daily_penalty": 2.33,  # EUR per day
                    "max_penalty": 232.94   # EUR
                }
            },
            "late_payment": {
                "interest_rate": 0.75,  # % per month
                "minimum_charge": 11.65  # EUR
            },
            "incorrect_filing": {
                "percentage_penalty": 20,  # % of tax due
                "minimum_penalty": 116.47  # EUR
            }
        }
    
    def _initialize_compliance_rules(self) -> List[Dict[str, Any]]:
        """Initialize Malta tax compliance rules"""
        return [
            {
                "rule_id": "VAT_REGISTRATION_THRESHOLD",
                "description": "VAT registration required if turnover exceeds €35,000",
                "condition": "annual_turnover > 35000",
                "severity": AlertSeverity.CRITICAL.value,
                "action": "Register for VAT within 30 days"
            },
            {
                "rule_id": "INCOME_TAX_FILING_REQUIRED",
                "description": "Income tax filing required if income exceeds €9,100",
                "condition": "annual_income > 9100",
                "severity": AlertSeverity.WARNING.value,
                "action": "File income tax return by June 30"
            },
            {
                "rule_id": "SOCIAL_SECURITY_CLASS2_REQUIRED",
                "description": "Class 2 social security required for self-employed",
                "condition": "employment_type == 'self_employed' AND annual_income > 3371.43",
                "severity": AlertSeverity.WARNING.value,
                "action": "Pay Class 2 social security contributions"
            },
            {
                "rule_id": "WITHHOLDING_TAX_REQUIRED",
                "description": "Withholding tax required for employees",
                "condition": "employment_type == 'employee' AND monthly_income > 758.33",
                "severity": AlertSeverity.INFO.value,
                "action": "Ensure employer deducts withholding tax"
            },
            {
                "rule_id": "QUARTERLY_VAT_ELIGIBLE",
                "description": "Quarterly VAT filing available if turnover < €700,000",
                "condition": "annual_turnover < 700000 AND vat_registered == True",
                "severity": AlertSeverity.INFO.value,
                "action": "Consider quarterly VAT filing to reduce compliance burden"
            }
        ]
    
    def check_compliance(self, user_id: str, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check compliance status for a user"""
        try:
            compliance_id = str(uuid.uuid4())
            
            # Extract key financial metrics
            annual_income = Decimal(str(financial_data.get('annual_income', 0)))
            annual_turnover = Decimal(str(financial_data.get('annual_turnover', 0)))
            employment_type = financial_data.get('employment_type', 'employee')
            vat_registered = financial_data.get('vat_registered', False)
            
            # Check each compliance rule
            compliance_issues = []
            recommendations = []
            
            for rule in self.compliance_rules:
                if self._evaluate_rule_condition(rule['condition'], financial_data):
                    issue = {
                        'rule_id': rule['rule_id'],
                        'description': rule['description'],
                        'severity': rule['severity'],
                        'action': rule['action'],
                        'detected_at': datetime.utcnow().isoformat()
                    }
                    
                    if rule['severity'] in [AlertSeverity.CRITICAL.value, AlertSeverity.WARNING.value]:
                        compliance_issues.append(issue)
                    else:
                        recommendations.append(issue)
            
            # Determine overall compliance status
            if any(issue['severity'] == AlertSeverity.CRITICAL.value for issue in compliance_issues):
                overall_status = ComplianceStatus.NON_COMPLIANT.value
            elif compliance_issues:
                overall_status = ComplianceStatus.WARNING.value
            else:
                overall_status = ComplianceStatus.COMPLIANT.value
            
            # Check upcoming deadlines
            upcoming_deadlines = self._get_upcoming_deadlines(financial_data)
            
            # Calculate compliance score
            compliance_score = self._calculate_compliance_score(compliance_issues, upcoming_deadlines)
            
            compliance_record = {
                'compliance_id': compliance_id,
                'user_id': user_id,
                'overall_status': overall_status,
                'compliance_score': compliance_score,
                'compliance_issues': compliance_issues,
                'recommendations': recommendations,
                'upcoming_deadlines': upcoming_deadlines,
                'financial_data': financial_data,
                'checked_at': datetime.utcnow().isoformat(),
                'next_check_due': (datetime.utcnow() + timedelta(days=30)).isoformat()
            }
            
            self.compliance_records[compliance_id] = compliance_record
            
            # Log compliance check
            self._log_audit_event(user_id, 'compliance_check', {
                'compliance_id': compliance_id,
                'status': overall_status,
                'issues_count': len(compliance_issues)
            })
            
            return compliance_record
            
        except Exception as e:
            self.logger.error(f"Error checking compliance: {str(e)}")
            raise ValueError(f"Compliance check failed: {str(e)}")
    
    def _evaluate_rule_condition(self, condition: str, data: Dict[str, Any]) -> bool:
        """Evaluate a compliance rule condition"""
        try:
            # Simple condition evaluation (in production, use a proper expression evaluator)
            # Replace variables with actual values
            eval_condition = condition
            
            for key, value in data.items():
                if isinstance(value, str):
                    eval_condition = eval_condition.replace(key, f"'{value}'")
                else:
                    eval_condition = eval_condition.replace(key, str(value))
            
            # Handle boolean values
            eval_condition = eval_condition.replace('True', 'True').replace('False', 'False')
            
            # Safely evaluate simple conditions
            if 'annual_turnover' in eval_condition and '>' in eval_condition:
                annual_turnover = Decimal(str(data.get('annual_turnover', 0)))
                if '35000' in eval_condition:
                    return annual_turnover > 35000
                elif '700000' in eval_condition:
                    return annual_turnover < 700000
            
            if 'annual_income' in eval_condition and '>' in eval_condition:
                annual_income = Decimal(str(data.get('annual_income', 0)))
                if '9100' in eval_condition:
                    return annual_income > 9100
                elif '3371.43' in eval_condition:
                    return annual_income > Decimal('3371.43')
            
            if 'employment_type' in eval_condition:
                employment_type = data.get('employment_type', 'employee')
                if 'self_employed' in eval_condition:
                    return employment_type == 'self_employed'
            
            if 'monthly_income' in eval_condition:
                annual_income = Decimal(str(data.get('annual_income', 0)))
                monthly_income = annual_income / 12
                if '758.33' in eval_condition:
                    return monthly_income > Decimal('758.33')
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error evaluating rule condition: {str(e)}")
            return False
    
    def _get_upcoming_deadlines(self, financial_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get upcoming tax deadlines for a user"""
        upcoming = []
        current_date = datetime.now().date()
        
        # Income tax deadline (June 30)
        current_year = current_date.year
        income_tax_deadline = date(current_year, 6, 30)
        if current_date <= income_tax_deadline:
            days_until = (income_tax_deadline - current_date).days
            upcoming.append({
                'deadline_type': 'income_tax',
                'description': 'Individual income tax return filing',
                'due_date': income_tax_deadline.isoformat(),
                'days_until': days_until,
                'is_overdue': False,
                'severity': 'critical' if days_until <= 30 else 'warning'
            })
        elif current_date > income_tax_deadline:
            days_overdue = (current_date - income_tax_deadline).days
            upcoming.append({
                'deadline_type': 'income_tax',
                'description': 'Individual income tax return filing (OVERDUE)',
                'due_date': income_tax_deadline.isoformat(),
                'days_overdue': days_overdue,
                'is_overdue': True,
                'severity': 'critical'
            })
        
        # VAT deadlines (if VAT registered)
        if financial_data.get('vat_registered', False):
            # Next month's 15th for monthly VAT
            next_month = current_date.replace(day=1) + timedelta(days=32)
            next_month = next_month.replace(day=1)
            vat_deadline = next_month.replace(day=15)
            
            days_until = (vat_deadline - current_date).days
            upcoming.append({
                'deadline_type': 'vat',
                'description': 'VAT return filing and payment',
                'due_date': vat_deadline.isoformat(),
                'days_until': days_until,
                'is_overdue': False,
                'severity': 'warning' if days_until <= 7 else 'info'
            })
        
        # Social Security Class 2 deadline (January 31)
        ss_deadline = date(current_year + 1, 1, 31)
        if current_date <= ss_deadline:
            days_until = (ss_deadline - current_date).days
            upcoming.append({
                'deadline_type': 'social_security_class2',
                'description': 'Class 2 Social Security contributions',
                'due_date': ss_deadline.isoformat(),
                'days_until': days_until,
                'is_overdue': False,
                'severity': 'warning' if days_until <= 60 else 'info'
            })
        
        return sorted(upcoming, key=lambda x: x.get('days_until', 999))
    
    def _calculate_compliance_score(self, issues: List[Dict], deadlines: List[Dict]) -> int:
        """Calculate compliance score (0-100)"""
        base_score = 100
        
        # Deduct points for issues
        for issue in issues:
            if issue['severity'] == AlertSeverity.CRITICAL.value:
                base_score -= 25
            elif issue['severity'] == AlertSeverity.WARNING.value:
                base_score -= 10
        
        # Deduct points for overdue deadlines
        for deadline in deadlines:
            if deadline.get('is_overdue', False):
                base_score -= 20
            elif deadline.get('days_until', 999) <= 7:
                base_score -= 5
        
        return max(0, base_score)
    
    def calculate_penalties(self, violation_type: str, tax_type: str, 
                          days_late: int, tax_amount: Decimal = None) -> Dict[str, Any]:
        """Calculate penalties for tax violations"""
        try:
            penalty_info = {
                'violation_type': violation_type,
                'tax_type': tax_type,
                'days_late': days_late,
                'calculation_date': datetime.utcnow().isoformat(),
                'penalties': []
            }
            
            if violation_type == PenaltyType.LATE_FILING.value:
                if tax_type in self.penalty_rates['late_filing']:
                    rates = self.penalty_rates['late_filing'][tax_type]
                    
                    base_penalty = Decimal(str(rates['base_penalty']))
                    daily_penalty = Decimal(str(rates['daily_penalty']))
                    max_penalty = Decimal(str(rates['max_penalty']))
                    
                    total_penalty = base_penalty + (daily_penalty * days_late)
                    total_penalty = min(total_penalty, max_penalty)
                    
                    penalty_info['penalties'].append({
                        'type': 'late_filing',
                        'base_penalty': float(base_penalty),
                        'daily_penalty': float(daily_penalty),
                        'days_applied': days_late,
                        'total_penalty': float(total_penalty),
                        'description': f'Late filing penalty for {tax_type}'
                    })
            
            elif violation_type == PenaltyType.LATE_PAYMENT.value and tax_amount:
                rates = self.penalty_rates['late_payment']
                monthly_rate = Decimal(str(rates['interest_rate'])) / 100
                minimum_charge = Decimal(str(rates['minimum_charge']))
                
                months_late = max(1, days_late // 30)
                interest_amount = tax_amount * monthly_rate * months_late
                total_penalty = max(interest_amount, minimum_charge)
                
                penalty_info['penalties'].append({
                    'type': 'late_payment',
                    'tax_amount': float(tax_amount),
                    'interest_rate': float(monthly_rate * 100),
                    'months_applied': months_late,
                    'interest_amount': float(interest_amount),
                    'minimum_charge': float(minimum_charge),
                    'total_penalty': float(total_penalty),
                    'description': f'Late payment interest for {tax_type}'
                })
            
            elif violation_type == PenaltyType.INCORRECT_FILING.value and tax_amount:
                rates = self.penalty_rates['incorrect_filing']
                percentage_penalty = Decimal(str(rates['percentage_penalty'])) / 100
                minimum_penalty = Decimal(str(rates['minimum_penalty']))
                
                calculated_penalty = tax_amount * percentage_penalty
                total_penalty = max(calculated_penalty, minimum_penalty)
                
                penalty_info['penalties'].append({
                    'type': 'incorrect_filing',
                    'tax_amount': float(tax_amount),
                    'penalty_rate': float(percentage_penalty * 100),
                    'calculated_penalty': float(calculated_penalty),
                    'minimum_penalty': float(minimum_penalty),
                    'total_penalty': float(total_penalty),
                    'description': f'Incorrect filing penalty for {tax_type}'
                })
            
            # Calculate total penalties
            penalty_info['total_penalties'] = sum(
                p['total_penalty'] for p in penalty_info['penalties']
            )
            
            return penalty_info
            
        except Exception as e:
            self.logger.error(f"Error calculating penalties: {str(e)}")
            raise ValueError(f"Penalty calculation failed: {str(e)}")
    
    def create_alert(self, user_id: str, alert_type: str, severity: AlertSeverity, 
                    message: str, data: Dict[str, Any] = None) -> str:
        """Create a compliance alert"""
        try:
            alert_id = str(uuid.uuid4())
            
            alert = {
                'alert_id': alert_id,
                'user_id': user_id,
                'alert_type': alert_type,
                'severity': severity.value,
                'message': message,
                'data': data or {},
                'created_at': datetime.utcnow().isoformat(),
                'acknowledged': False,
                'resolved': False
            }
            
            self.alerts[alert_id] = alert
            
            # Log alert creation
            self._log_audit_event(user_id, 'alert_created', {
                'alert_id': alert_id,
                'alert_type': alert_type,
                'severity': severity.value
            })
            
            return alert_id
            
        except Exception as e:
            self.logger.error(f"Error creating alert: {str(e)}")
            raise ValueError(f"Alert creation failed: {str(e)}")
    
    def _log_audit_event(self, user_id: str, event_type: str, data: Dict[str, Any]):
        """Log an audit event"""
        try:
            audit_id = str(uuid.uuid4())
            
            audit_log = {
                'audit_id': audit_id,
                'user_id': user_id,
                'event_type': event_type,
                'data': data,
                'timestamp': datetime.utcnow().isoformat(),
                'ip_address': None,  # Would be populated from request context
                'user_agent': None   # Would be populated from request context
            }
            
            self.audit_logs[audit_id] = audit_log
            
        except Exception as e:
            self.logger.error(f"Error logging audit event: {str(e)}")
    
    def get_compliance_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get compliance dashboard data for a user"""
        try:
            # Get latest compliance record
            user_compliance_records = [
                record for record in self.compliance_records.values()
                if record['user_id'] == user_id
            ]
            
            latest_compliance = None
            if user_compliance_records:
                latest_compliance = max(
                    user_compliance_records, 
                    key=lambda r: r['checked_at']
                )
            
            # Get active alerts
            user_alerts = [
                alert for alert in self.alerts.values()
                if alert['user_id'] == user_id and not alert['resolved']
            ]
            
            # Get recent audit logs
            user_audit_logs = [
                log for log in self.audit_logs.values()
                if log['user_id'] == user_id
            ]
            recent_audit_logs = sorted(
                user_audit_logs, 
                key=lambda l: l['timestamp'], 
                reverse=True
            )[:10]
            
            dashboard = {
                'user_id': user_id,
                'compliance_status': latest_compliance['overall_status'] if latest_compliance else 'unknown',
                'compliance_score': latest_compliance['compliance_score'] if latest_compliance else 0,
                'active_issues': len(latest_compliance['compliance_issues']) if latest_compliance else 0,
                'upcoming_deadlines': len(latest_compliance['upcoming_deadlines']) if latest_compliance else 0,
                'active_alerts': len(user_alerts),
                'last_check': latest_compliance['checked_at'] if latest_compliance else None,
                'next_check_due': latest_compliance['next_check_due'] if latest_compliance else None,
                'recent_activity': recent_audit_logs
            }
            
            return dashboard
            
        except Exception as e:
            self.logger.error(f"Error getting compliance dashboard: {str(e)}")
            raise ValueError(f"Dashboard generation failed: {str(e)}")
    
    def get_regulatory_updates(self) -> List[Dict[str, Any]]:
        """Get recent regulatory changes and updates"""
        # In a real implementation, this would fetch from a regulatory database
        return [
            {
                'update_id': 'REG-2025-001',
                'title': 'VAT Rate Changes for 2025',
                'description': 'Standard VAT rate remains at 18% for 2025',
                'effective_date': '2025-01-01',
                'impact': 'No changes required for existing VAT calculations',
                'severity': 'info',
                'published_date': '2024-12-15'
            },
            {
                'update_id': 'REG-2025-002',
                'title': 'Income Tax Brackets Update',
                'description': 'Minor adjustments to income tax brackets for inflation',
                'effective_date': '2025-01-01',
                'impact': 'Updated tax calculations for individual taxpayers',
                'severity': 'warning',
                'published_date': '2024-11-30'
            }
        ]

